"""
MarineShield SAR Tiling Verification Suite
Validates:
1. Tile output files exist and are readable (.npy & .json sidecars)
2. Training and validation examples are present and correctly labeled
3. Tile dimensions and resolution are consistent (512x512, 10.0m)
4. Normalization parameters are recorded in sidecars
5. Metadata sidecars are valid JSON conforming to contract
6. Deterministic tile generation (identical inputs produce 100% matching hashes)
7. Zero data leakage between train and validation sets
"""

import sys
import json
import tempfile
import numpy as np
from pathlib import Path

# Setup paths
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(src_dir))

from marineshield.config import settings
from scripts.generate_sar_tiles import run_sar_tile_generation

def run_sar_tiling_tests():
    print("=" * 80)
    print("      MarineShield SAR Preprocessing & Tiling Verification Suite")
    print("=" * 80)

    # 1. Run Tile Generation
    tiles_dir = settings.SAR_PREPROCESSED_DIR / "tiles"
    manifest = run_sar_tile_generation(output_tiles_dir=tiles_dir)

    print("\n--- [Test 1] Validating Tile Files and Sidecars ---")
    manifest_path = tiles_dir / "tile_manifest.json"
    assert manifest_path.exists(), f"Tile manifest {manifest_path} missing"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    tiles = manifest_data["tiles"]
    assert len(tiles) >= 2, f"Expected at least 2 tiles, got {len(tiles)}"
    print(f"[PASS] Tile manifest contains {len(tiles)} tiles.")

    # 2. Check Training and Validation Examples
    print("\n--- [Test 2] Training & Validation Tile Example Inspection ---")
    train_tiles = [t for t in tiles if t["split"] == "train"]
    val_tiles = [t for t in tiles if t["split"] == "val"]
    assert len(train_tiles) > 0, "No training tiles found"
    assert len(val_tiles) > 0, "No validation tiles found"

    train_example = train_tiles[0]
    val_example = val_tiles[0]
    print(f"[PASS] Found Training Tile Example:   {train_example['tile_id']} ({train_example['npy_file']})")
    print(f"[PASS] Found Validation Tile Example: {val_example['tile_id']} ({val_example['npy_file']})")

    # 3. Validate Dimensions, Resolution, and Normalization in Array
    print("\n--- [Test 3] Array Dimensions & Normalization Range ---")
    for t in [train_example, val_example]:
        npy_path = tiles_dir / t["npy_file"]
        arr = np.load(npy_path)
        assert arr.ndim == 3, f"Expected 3D array (C, H, W), got shape {arr.shape}"
        assert arr.shape[1] == 512 and arr.shape[2] == 512, f"Tile shape mismatch: {arr.shape}"
        assert arr.min() >= 0.0 and arr.max() <= 1.0, f"Normalized values out of [0.0, 1.0] range: min={arr.min()}, max={arr.max()}"
        print(f"[PASS] Array {t['npy_file']} shape={arr.shape}, range=[{arr.min():.4f}, {arr.max():.4f}]")

    # 4. Validate Metadata Sidecar
    print("\n--- [Test 4] Metadata Sidecar Parsing & Schema ---")
    sidecar_path = tiles_dir / train_example["sidecar_file"]
    assert sidecar_path.exists(), f"Sidecar {sidecar_path} does not exist"
    with open(sidecar_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["tile_dimensions_px"] == [512, 512], "Tile dimension mismatch"
    assert meta["spatial_resolution_m"] == [10.0, 10.0], "Resolution mismatch"
    assert meta["crs"] == "EPSG:4326", "CRS mismatch"
    assert meta["channels"] == ["VV", "VH"], "Channels mismatch"
    assert meta["normalization"]["method"] == "linear_clip_db", "Normalization method mismatch"
    assert len(meta["sha256_hash"]) == 64, "Invalid SHA-256 hash"
    print(f"[PASS] Sidecar parsed successfully: Resolution={meta['spatial_resolution_m']}, CRS={meta['crs']}, SHA256={meta['sha256_hash'][:12]}...")

    # 5. Determinism Smoke Test
    print("\n--- [Test 5] Determinism Smoke Test (Double-Run Hash Equality) ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        manifest2 = run_sar_tile_generation(output_tiles_dir=tmp_path)
        for t1, t2 in zip(manifest["tiles"], manifest2["tiles"]):
            assert t1["tile_id"] == t2["tile_id"], f"Tile ID mismatch: {t1['tile_id']} != {t2['tile_id']}"
            assert t1["sha256"] == t2["sha256"], f"SHA256 mismatch for {t1['tile_id']}: {t1['sha256']} != {t2['sha256']}"
    print("[PASS] Deterministic reproducibility verified: 100% identical tile IDs and cryptographic hashes across runs.")

    # 6. Leak-Free Split Validation
    print("\n--- [Test 6] Leak-Free Split Partitioning Verification ---")
    train_ids = {t["tile_id"] for t in train_tiles}
    val_ids = {t["tile_id"] for t in val_tiles}
    assert len(train_ids.intersection(val_ids)) == 0, "Data leakage detected: overlapping tile IDs between train and val"
    print(f"[PASS] Zero data leakage: {len(train_ids)} train tiles and {len(val_ids)} val tiles are strictly disjoint.")

    print("\n" + "=" * 80)
    print("   [SUCCESS] All SAR Preprocessing & ML Tiling Tests Passed 100%!")
    print("=" * 80)

if __name__ == "__main__":
    run_sar_tiling_tests()
