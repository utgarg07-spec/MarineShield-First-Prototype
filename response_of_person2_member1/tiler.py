"""
MarineShield SAR ML Tile Generation Engine
Extracts deterministic ML-ready tiles with metadata sidecars, consistent spatial resolution,
standardized normalization, cryptographic hashing, and leak-free split partitioning.
"""

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

@dataclass
class TileConfig:
    tile_size_px: int = 512
    stride_px: int = 512
    pixel_spacing_m: float = 10.0
    crs: str = "EPSG:4326"
    normalization_method: str = "linear_clip_db"
    min_db: float = -30.0
    max_db: float = 0.0
    clip_min: float = 0.0
    clip_max: float = 1.0
    val_ratio: float = 0.2
    split_policy: str = "spatial_quadrant_no_leakage"
    pipeline_version: str = "1.0.0"

@dataclass
class TileMetadata:
    tile_id: str
    source_granule_id: str
    tile_row: int
    tile_col: int
    pixel_bounds_yx: List[int]  # [y_start, y_end, x_start, x_end]
    geo_bbox_wgs84: List[float]  # [min_lon, min_lat, max_lon, max_lat]
    spatial_resolution_m: List[float]  # [res_y, res_x]
    tile_dimensions_px: List[int]  # [height, width]
    crs: str
    channels: List[str]
    normalization: Dict[str, Any]
    split: str
    sha256_hash: str
    pipeline_version: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SARTiler:
    """
    Deterministic Tiling and Normalization Engine for ML ingestion.
    """

    def __init__(self, config: Optional[TileConfig] = None):
        self.config = config or TileConfig()

    @staticmethod
    def compute_sha256_array(arr: np.ndarray) -> str:
        """Compute deterministic SHA-256 hash of a contiguous numpy array."""
        hasher = hashlib.sha256()
        hasher.update(np.ascontiguousarray(arr).tobytes())
        return hasher.hexdigest()

    def normalize_tile(
        self,
        tile_data: np.ndarray,
        nodata_val: float = -9999.0
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Normalize radar backscatter values according to SAR_DATA_CONTRACT.md:
        I_norm = clip((sigma0_dB - (-30.0)) / (0.0 - (-30.0)), 0.0, 1.0)
        """
        data = np.asarray(tile_data, dtype=np.float32)
        valid_mask = (data != nodata_val) & ~np.isnan(data)

        norm_params = {
            "method": self.config.normalization_method,
            "min_db": self.config.min_db,
            "max_db": self.config.max_db,
            "clip_min": self.config.clip_min,
            "clip_max": self.config.clip_max,
            "formula": "clip((sigma0 - min_db)/(max_db - min_db), clip_min, clip_max)"
        }

        if self.config.normalization_method == "linear_clip_db":
            denominator = max(self.config.max_db - self.config.min_db, 1e-6)
            normalized = np.zeros_like(data, dtype=np.float32)
            normalized[valid_mask] = np.clip(
                (data[valid_mask] - self.config.min_db) / denominator,
                self.config.clip_min,
                self.config.clip_max
            )
            # Retain zero for nodata regions
            normalized[~valid_mask] = 0.0
            return normalized, norm_params
        elif self.config.normalization_method == "zscore":
            mu = float(np.nanmean(data[valid_mask])) if np.any(valid_mask) else 0.0
            std = float(np.nanstd(data[valid_mask])) if np.any(valid_mask) else 1.0
            std = max(std, 1e-6)
            normalized = np.zeros_like(data, dtype=np.float32)
            normalized[valid_mask] = np.clip((data[valid_mask] - mu) / std, -3.0, 3.0)
            normalized[~valid_mask] = 0.0
            norm_params.update({"mean_db": mu, "std_db": std, "clip_min": -3.0, "clip_max": 3.0})
            return normalized, norm_params
        else:
            raise ValueError(f"Unknown normalization method: {self.config.normalization_method}")

    def compute_tile_geo_bbox(
        self,
        scene_bbox_wgs84: List[float],
        raster_height: int,
        raster_width: int,
        y_start: int,
        y_end: int,
        x_start: int,
        x_end: int
    ) -> List[float]:
        """
        Compute geodetic bounding box [min_lon, min_lat, max_lon, max_lat] in EPSG:4326 for a tile.
        """
        min_lon, min_lat, max_lon, max_lat = scene_bbox_wgs84
        lon_step = (max_lon - min_lon) / max(raster_width, 1)
        lat_step = (max_lat - min_lat) / max(raster_height, 1)

        tile_min_lon = round(min_lon + x_start * lon_step, 6)
        tile_max_lon = round(min_lon + x_end * lon_step, 6)
        # Assuming origin top-left or standard cartesian
        tile_max_lat = round(max_lat - y_start * lat_step, 6)
        tile_min_lat = round(max_lat - y_end * lat_step, 6)

        return [tile_min_lon, tile_min_lat, tile_max_lon, tile_max_lat]

    def assign_split_leak_free(
        self,
        tile_row: int,
        tile_col: int,
        total_rows: int,
        total_cols: int,
        granule_id: str
    ) -> str:
        """
        Deterministic spatial quadrant partitioning preventing neighboring tile leakage:
        The southeastern quadrant is reserved for validation; remainder for training.
        """
        row_threshold = int(total_rows * (1.0 - np.sqrt(self.config.val_ratio)))
        col_threshold = int(total_cols * (1.0 - np.sqrt(self.config.val_ratio)))

        if tile_row >= row_threshold and tile_col >= col_threshold:
            return "val"
        return "train"

    def tile_scene_raster(
        self,
        scene_raster_db: np.ndarray,
        source_granule_id: str,
        scene_bbox_wgs84: List[float],
        output_dir: Path,
        channels: Optional[List[str]] = None,
        nodata_val: float = -9999.0
    ) -> Dict[str, Any]:
        """
        Extract deterministic ML tiles from a 2D or 3D calibrated scene raster.
        Saves normalized .npy arrays and JSON metadata sidecars.
        Returns a complete tile manifest.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if scene_raster_db.ndim == 2:
            h, w = scene_raster_db.shape
            c = 1
            data = scene_raster_db[np.newaxis, ...]
        elif scene_raster_db.ndim == 3:
            c, h, w = scene_raster_db.shape
            data = scene_raster_db
        else:
            raise ValueError(f"Expected 2D or 3D raster array, got shape {scene_raster_db.shape}")

        active_channels = channels or (["VV"] if c == 1 else ["VV", "VH"][:c])
        ts = self.config.tile_size_px
        stride = self.config.stride_px

        y_coords = list(range(0, max(1, h - ts + 1), stride))
        x_coords = list(range(0, max(1, w - ts + 1), stride))
        if not y_coords:
            y_coords = [0]
        if not x_coords:
            x_coords = [0]

        total_rows = len(y_coords)
        total_cols = len(x_coords)

        manifest_tiles = []
        train_count = 0
        val_count = 0

        for r_idx, y_start in enumerate(y_coords):
            y_end = min(y_start + ts, h)
            for c_idx, x_start in enumerate(x_coords):
                x_end = min(x_start + ts, w)

                # Extract tile slice
                tile_slice = data[:, y_start:y_end, x_start:x_end]

                # Pad to exact tile_size_px if near boundary
                if tile_slice.shape[1] < ts or tile_slice.shape[2] < ts:
                    padded = np.full((c, ts, ts), nodata_val, dtype=np.float32)
                    padded[:, :tile_slice.shape[1], :tile_slice.shape[2]] = tile_slice
                    tile_slice = padded

                # Normalize tile
                normalized_tile, norm_params = self.normalize_tile(tile_slice, nodata_val=nodata_val)

                # Determine split
                split = self.assign_split_leak_free(r_idx, c_idx, total_rows, total_cols, source_granule_id)
                if split == "train":
                    train_count += 1
                else:
                    val_count += 1

                # Generate IDs & hashes
                tile_id = f"{source_granule_id}_tile_r{r_idx:03d}_c{c_idx:03d}_{split}"
                tile_sha256 = self.compute_sha256_array(normalized_tile)
                geo_bbox = self.compute_tile_geo_bbox(
                    scene_bbox_wgs84, h, w, y_start, y_end, x_start, x_end
                )

                # Build metadata sidecar
                meta = TileMetadata(
                    tile_id=tile_id,
                    source_granule_id=source_granule_id,
                    tile_row=r_idx,
                    tile_col=c_idx,
                    pixel_bounds_yx=[y_start, y_end, x_start, x_end],
                    geo_bbox_wgs84=geo_bbox,
                    spatial_resolution_m=[self.config.pixel_spacing_m, self.config.pixel_spacing_m],
                    tile_dimensions_px=[ts, ts],
                    crs=self.config.crs,
                    channels=active_channels,
                    normalization=norm_params,
                    split=split,
                    sha256_hash=tile_sha256,
                    pipeline_version=self.config.pipeline_version
                )

                # Save tile array (.npy)
                tile_filename = f"{tile_id}.npy"
                tile_path = output_dir / tile_filename
                np.save(tile_path, normalized_tile)

                # Save metadata sidecar (.json)
                sidecar_filename = f"{tile_id}_metadata.json"
                sidecar_path = output_dir / sidecar_filename
                with open(sidecar_path, "w", encoding="utf-8") as f:
                    json.dump(meta.to_dict(), f, indent=2)

                manifest_tiles.append({
                    "tile_id": tile_id,
                    "split": split,
                    "row": r_idx,
                    "col": c_idx,
                    "npy_file": tile_filename,
                    "sidecar_file": sidecar_filename,
                    "sha256": tile_sha256,
                    "geo_bbox": geo_bbox
                })

        # Save manifest
        manifest = {
            "manifest_version": "1.0.0",
            "source_granule_id": source_granule_id,
            "scene_bbox_wgs84": scene_bbox_wgs84,
            "config": asdict(self.config),
            "summary": {
                "total_tiles": len(manifest_tiles),
                "train_tiles": train_count,
                "val_tiles": val_count,
                "grid_shape": [total_rows, total_cols]
            },
            "tiles": manifest_tiles
        }

        manifest_path = output_dir / "tile_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest
