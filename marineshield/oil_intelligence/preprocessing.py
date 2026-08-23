import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from PIL import Image

class SarTilePreprocessor:
    """Deterministic Preprocessor for SAR Tile Input.

    
    Guarantees:
    - Loads (512x512) SAR tile array deterministically
    - Normalizes & standardizes to (1, 3, 1024, 1024) tensor expected by SAM ViT-B
    - Detects candidate dark anomalies / prompts
    - Scales prompt coordinates (x2) from 512 to 1024
    - Extracts radiometric backscatter properties (mean dB, suppression)
    - Strict validation rejecting malformed, empty, or NaN/Inf inputs
    """
    def __init__(self, target_size: Tuple[int, int] = (512, 512), sam_size: Tuple[int, int] = (1024, 1024)):
        self.target_size = target_size
        self.sam_size = sam_size
        self.pixel_mean = torch.tensor([123.675, 116.28, 103.53]).view(1, 3, 1, 1)
        self.pixel_std = torch.tensor([58.395, 57.12, 57.375]).view(1, 3, 1, 1)

    def load_and_validate(self, input_source: Any) -> np.ndarray:
        """Loads and strictly validates input SAR tile array."""
        if input_source is None:
            raise ValueError("SAR tile input cannot be None")

        if isinstance(input_source, (str, Path)):
            path = Path(input_source)
            if not path.exists():
                raise FileNotFoundError(f"SAR tile file not found: {path}")
            # Load with PIL
            img = Image.open(path)
            arr = np.array(img, dtype=np.float32)
        elif isinstance(input_source, np.ndarray):
            arr = input_source.astype(np.float32)
        elif isinstance(input_source, torch.Tensor):
            arr = input_source.detach().cpu().numpy().astype(np.float32)
        else:
            raise ValueError(f"Unsupported SAR tile input type: {type(input_source)}")

        # Validation
        if arr.size == 0:
            raise ValueError("Malformed SAR tile: array is empty (0 elements)")
        if np.isnan(arr).any() or np.isinf(arr).any():
            raise ValueError("Malformed SAR tile: contains NaN or Inf values")

        # Handle dimensions
        if arr.ndim == 2:
            # (H, W) -> single channel
            pass
        elif arr.ndim == 3:
            if arr.shape[2] in [1, 3, 4]:
                arr = arr[:, :, 0]  # Use first SAR polarization channel
            elif arr.shape[0] in [1, 3, 4]:
                arr = arr[0, :, :]
            else:
                raise ValueError(f"Malformed SAR tile: unsupported 3D shape {arr.shape}")
        else:
            raise ValueError(f"Malformed SAR tile: unsupported ndim {arr.ndim}")

        # Deterministic resize to target size (512, 512) if needed
        if arr.shape != self.target_size:
            pil_img = Image.fromarray(arr)
            pil_img = pil_img.resize(self.target_size, Image.Resampling.BILINEAR)
            arr = np.array(pil_img, dtype=np.float32)

        return arr

    def normalize_for_sam(self, arr: np.ndarray, device: str = "cpu") -> torch.Tensor:
        """Normalizes 2D float array to (1, 3, 1024, 1024) tensor expected by SAM ViT-B."""
        min_val, max_val = float(arr.min()), float(arr.max())
        if max_val > min_val:
            norm_arr = (arr - min_val) / (max_val - min_val) * 255.0
        else:
            norm_arr = np.zeros_like(arr)

        norm_arr = np.clip(norm_arr, 0.0, 255.0).astype(np.uint8)
        # Replicate to 3 channels (H, W, 3)
        rgb_arr = np.stack([norm_arr, norm_arr, norm_arr], axis=-1)
        # Convert to Tensor (1, 3, 512, 512)
        tensor = torch.from_numpy(rgb_arr).permute(2, 0, 1).unsqueeze(0).float()
        
        # Interpolate to (1, 3, 1024, 1024)
        tensor_1024 = F.interpolate(tensor, size=self.sam_size, mode="bilinear", align_corners=False)
        
        # Standardize with SAM pixel mean and std
        p_mean = self.pixel_mean.to(tensor_1024.device)
        p_std = self.pixel_std.to(tensor_1024.device)
        standardized = (tensor_1024 - p_mean) / p_std
        return standardized

    def scale_box_to_sam(self, box_512: list) -> list:
        """Scales box prompt coordinates from 512x512 to 1024x1024."""
        return [float(c * 2.0) for c in box_512]

    def detect_candidate_regions(self, arr: np.ndarray, dark_percentile: float = 20.0) -> Dict[str, Any]:
        """Detects candidate dark backscatter anomaly regions for prompt generation.

        
        Returns:
        - bounding_box: [x_min, y_min, x_max, y_max] in pixels (512x512 coordinate space)
        - has_candidate: boolean
        - dark_pixel_count: int
        - mean_backscatter_raw: float
        """
        threshold = float(np.percentile(arr, dark_percentile))
        dark_mask = arr < threshold
        dark_pixel_count = int(np.sum(dark_mask))

        if dark_pixel_count < 30:  # Noise floor
            return {
                "has_candidate": False,
                "bounding_box": [0, 0, 512, 512],
                "center_point": [256, 256],
                "dark_pixel_count": dark_pixel_count,
                "mean_backscatter_raw": float(np.mean(arr)),
                "suppression_contrast": 0.0
            }

        y_indices, x_indices = np.where(dark_mask)
        y_min, y_max = int(np.min(y_indices)), int(np.max(y_indices))
        x_min, x_max = int(np.min(x_indices)), int(np.max(x_indices))

        # Add 10px margin
        x_min = max(0, x_min - 10)
        y_min = max(0, y_min - 10)
        x_max = min(512, x_max + 10)
        y_max = min(512, y_max + 10)

        # Contrast calculation
        clean_mean = float(np.mean(arr[~dark_mask])) if np.any(~dark_mask) else float(np.mean(arr))
        dark_mean = float(np.mean(arr[dark_mask]))
        suppression = max(0.0, clean_mean - dark_mean)

        return {
            "has_candidate": True,
            "bounding_box": [x_min, y_min, x_max, y_max],
            "center_point": [int((x_min + x_max) // 2), int((y_min + y_max) // 2)],
            "dark_pixel_count": dark_pixel_count,
            "mean_backscatter_raw": dark_mean,
            "suppression_contrast": suppression
        }
