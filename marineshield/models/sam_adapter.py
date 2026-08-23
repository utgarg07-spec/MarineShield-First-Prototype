import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from segment_anything import sam_model_registry

class SarFeatureAdapter(nn.Module):
    """Parameter-Efficient SAR Feature Adapter.

    
    Adapts 256-dimensional ViT-B image embeddings to SAR speckle texture
    and radar backscatter damping characteristics via a lightweight residual bottleneck.
    """
    def __init__(self, in_channels: int = 256, bottleneck_channels: int = 64):
        super().__init__()
        self.adapter = nn.Sequential(
            nn.Conv2d(in_channels, bottleneck_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(bottleneck_channels),
            nn.GELU(),
            nn.Conv2d(bottleneck_channels, bottleneck_channels, kernel_size=3, padding=1, groups=bottleneck_channels, bias=False),
            nn.BatchNorm2d(bottleneck_channels),
            nn.GELU(),
            nn.Conv2d(bottleneck_channels, in_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(in_channels)
        )
        self.scale = nn.Parameter(torch.tensor([0.1]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Residual connection
        return x + self.scale * self.adapter(x)


class SarSamAdapter(nn.Module):
    """SAR-Adapted Segment Anything Model (SAM-OIL Methodology).

    
    • Frozen: ViT-B Image Encoder (86.4M params) & Prompt Encoder (0.0M params)
    • Trainable: SAR Feature Adapter (~0.05M params) + Mask Decoder (4.06M params)
    • Total Trainable: ~4.11M params (4.3% of 93.7M total model parameters)
    """
    def __init__(self, checkpoint_path: str = "models/checkpoints/sam_vit_b_01ec64.pth", device: str = "cuda"):
        super().__init__()
        self.device_type = device
        
        # 1. Load Base SAM ViT-B
        print(f"Loading Base SAM ViT-B from {checkpoint_path}...")
        self.sam = sam_model_registry["vit_b"](checkpoint=checkpoint_path)
        
        # 2. Freeze Image Encoder & Prompt Encoder
        for param in self.sam.image_encoder.parameters():
            param.requires_grad = False
        for param in self.sam.prompt_encoder.parameters():
            param.requires_grad = False

        # 3. Add Trainable SAR Feature Adapter
        self.sar_adapter = SarFeatureAdapter(in_channels=256, bottleneck_channels=64)
        
        # 4. Unfreeze Mask Decoder
        for param in self.sam.mask_decoder.parameters():
            param.requires_grad = True

        self.to(device)

    def count_parameters(self):
        """Returns total, trainable, and frozen parameter counts."""
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.parameters())
        frozen = total - trainable
        return {
            "total_parameters": total,
            "trainable_parameters": trainable,
            "frozen_parameters": frozen,
            "trainable_percentage": round((trainable / total) * 100.0, 2)
        }

    def encode_image(self, image_tensor: torch.Tensor) -> torch.Tensor:
        """Computes ViT-B image embedding and passes through SAR feature adapter."""
        with torch.no_grad():
            base_embedding = self.sam.image_encoder(image_tensor)
        adapted_embedding = self.sar_adapter(base_embedding)
        return adapted_embedding

    def forward(self, image_tensor: torch.Tensor, boxes: torch.Tensor = None, points: tuple = None):
        """Forward pass generating mask logits and IoU prediction."""
        # 1. Image Embedding
        image_embedding = self.encode_image(image_tensor)
        
        # 2. Prompt Encoding
        sparse_embeddings, dense_embeddings = self.sam.prompt_encoder(
            points=points,
            boxes=boxes,
            masks=None
        )

        # 3. Mask Decoding
        low_res_masks, iou_predictions = self.sam.mask_decoder(
            image_embeddings=image_embedding,
            image_pe=self.sam.prompt_encoder.get_dense_pe(),
            sparse_prompt_embeddings=sparse_embeddings,
            dense_prompt_embeddings=dense_embeddings,
            multimask_output=False
        )

        # Upscale masks to 512x512
        high_res_masks = self.sam.postprocess_masks(
            low_res_masks,
            input_size=(512, 512),
            original_size=(512, 512)
        )
        return high_res_masks, iou_predictions

    def compute_loss(self, pred_logits: torch.Tensor, gt_mask: torch.Tensor):
        """Combined Binary Cross-Entropy + Soft Dice Loss for oil segmentation and look-alike suppression."""
        bce_loss = F.binary_cross_entropy_with_logits(pred_logits, gt_mask)
        
        pred_probs = torch.sigmoid(pred_logits)
        intersection = (pred_probs * gt_mask).sum()
        union = pred_probs.sum() + gt_mask.sum()
        dice_loss = 1.0 - ((2.0 * intersection + 1.0) / (union + 1.0))

        total_loss = bce_loss + dice_loss
        return {
            "total_loss": total_loss,
            "bce_loss": bce_loss.item(),
            "dice_loss": dice_loss.item()
        }
