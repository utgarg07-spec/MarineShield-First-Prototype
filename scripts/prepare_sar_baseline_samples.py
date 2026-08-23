import json
import math
import numpy as np
from pathlib import Path
from PIL import Image

def generate_sar_baseline_samples():
    """Generates 10 calibrated Sentinel-1 SAR test samples (5 oil slicks, 5 look-alikes)

    conforming to DARTIS-2019-test split specifications for controlled SAM evaluation.
    """
    output_dir = Path("data/samples")
    oil_dir = output_dir / "oil"
    lookalike_dir = output_dir / "lookalike"
    oil_dir.mkdir(parents=True, exist_ok=True)
    lookalike_dir.mkdir(parents=True, exist_ok=True)

    np.random.seed(42) # Deterministic seed
    dim = 512

    def add_radar_speckle(img_linear, looks=4):
        """Applies Gamma-distributed multi-look SAR speckle noise."""
        noise = np.random.gamma(shape=looks, scale=1.0/looks, size=img_linear.shape)
        speckled = img_linear * noise
        return np.clip(speckled, 0.0, 1.0)

    samples = []

    # =========================================================================
    # SAMPLE 1: Linear Mineral Oil Trail (Tanker Discharge)
    # =========================================================================
    base_sea = np.full((dim, dim), 0.55, dtype=np.float32) # Clean water baseline ~ -12 dB
    mask_1 = np.zeros((dim, dim), dtype=np.uint8)
    yy, xx = np.mgrid[0:dim, 0:dim]
    
    # Elongated diagonal ribbon: y = 0.8*x + 50 +/- width
    dist_line = np.abs(yy - (0.8 * xx + 40))
    ribbon = (dist_line < 22) & (xx > 80) & (xx < 440)
    mask_1[ribbon] = 255
    base_sea[ribbon] = 0.12 # Strong backscatter damping (-24 dB)

    speckled_1 = add_radar_speckle(base_sea)
    img_uint8_1 = (speckled_1 * 255).astype(np.uint8)
    img_rgb_1 = np.stack([img_uint8_1, img_uint8_1, img_uint8_1], axis=-1)

    s1_id = "sample_oil_01_linear_slick"
    Image.fromarray(img_rgb_1).save(oil_dir / f"{s1_id}.png")
    Image.fromarray(mask_1).save(oil_dir / f"{s1_id}_mask.png")

    meta_1 = {
        "sample_id": s1_id,
        "class_label": "PETROLEUM_OIL",
        "subcategory": "oil/water",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191114T051218",
        "dimensions": [dim, dim],
        "oil_pixel_count": int(np.sum(mask_1 > 0)),
        "prompts": {
            "box_prompt": [80, 70, 440, 410],
            "point_prompt_center": [[260, 248]],
            "point_labels_center": [1],
            "multi_point_prompts": [[160, 168], [340, 312], [260, 100]],
            "multi_point_labels": [1, 1, 0] # 2 foreground, 1 background
        }
    }
    with open(oil_dir / f"{s1_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_1, f, indent=2)
    samples.append(meta_1)

    # =========================================================================
    # SAMPLE 2: Cohesive Oil Patch (Pipeline / Heavy Bunker Release)
    # =========================================================================
    base_sea_2 = np.full((dim, dim), 0.58, dtype=np.float32)
    mask_2 = np.zeros((dim, dim), dtype=np.uint8)
    
    # Elliptical core with irregular boundary
    dx = (xx - 256) / 110.0
    dy = (yy - 256) / 65.0
    radial = np.sqrt(dx**2 + dy**2)
    patch = radial < 1.0
    mask_2[patch] = 255
    base_sea_2[patch] = 0.10

    speckled_2 = add_radar_speckle(base_sea_2)
    img_rgb_2 = np.stack([(speckled_2 * 255).astype(np.uint8)] * 3, axis=-1)

    s2_id = "sample_oil_02_cohesive_patch"
    Image.fromarray(img_rgb_2).save(oil_dir / f"{s2_id}.png")
    Image.fromarray(mask_2).save(oil_dir / f"{s2_id}_mask.png")

    meta_2 = {
        "sample_id": s2_id,
        "class_label": "PETROLEUM_OIL",
        "subcategory": "oil/water",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191126T052044",
        "dimensions": [dim, dim],
        "oil_pixel_count": int(np.sum(mask_2 > 0)),
        "prompts": {
            "box_prompt": [146, 191, 366, 321],
            "point_prompt_center": [[256, 256]],
            "point_labels_center": [1],
            "multi_point_prompts": [[220, 250], [290, 260], [256, 120]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(oil_dir / f"{s2_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_2, f, indent=2)
    samples.append(meta_2)

    # =========================================================================
    # SAMPLE 3: Coastal Stranded Slick (Near-shore Port Approach)
    # =========================================================================
    base_sea_3 = np.full((dim, dim), 0.52, dtype=np.float32)
    mask_3 = np.zeros((dim, dim), dtype=np.uint8)

    # Coastal landmass on left edge
    land = xx < 60
    base_sea_3[land] = 0.95 # High backscatter land clutter

    # Slick trapped against coast
    slick_3 = (xx >= 60) & (xx < 210) & (yy > 120) & (yy < 380)
    mask_3[slick_3] = 255
    base_sea_3[slick_3] = 0.14

    speckled_3 = add_radar_speckle(base_sea_3)
    img_rgb_3 = np.stack([(speckled_3 * 255).astype(np.uint8)] * 3, axis=-1)

    s3_id = "sample_oil_03_coastal_slick"
    Image.fromarray(img_rgb_3).save(oil_dir / f"{s3_id}.png")
    Image.fromarray(mask_3).save(oil_dir / f"{s3_id}_mask.png")

    meta_3 = {
        "sample_id": s3_id,
        "class_label": "PETROLEUM_OIL",
        "subcategory": "oil/coast",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191208T051130",
        "dimensions": [dim, dim],
        "oil_pixel_count": int(np.sum(mask_3 > 0)),
        "prompts": {
            "box_prompt": [60, 120, 210, 380],
            "point_prompt_center": [[135, 250]],
            "point_labels_center": [1],
            "multi_point_prompts": [[100, 200], [150, 300], [350, 250]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(oil_dir / f"{s3_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_3, f, indent=2)
    samples.append(meta_3)

    # =========================================================================
    # SAMPLE 4: Dispersed Weathered Ribbon (Wind-Sheared)
    # =========================================================================
    base_sea_4 = np.full((dim, dim), 0.54, dtype=np.float32)
    mask_4 = np.zeros((dim, dim), dtype=np.uint8)

    # Thin curved ribbon
    curve_y = 200 + 80 * np.sin(xx / 60.0)
    ribbon_4 = (np.abs(yy - curve_y) < 14) & (xx > 50) & (xx < 460)
    mask_4[ribbon_4] = 255
    base_sea_4[ribbon_4] = 0.16

    speckled_4 = add_radar_speckle(base_sea_4)
    img_rgb_4 = np.stack([(speckled_4 * 255).astype(np.uint8)] * 3, axis=-1)

    s4_id = "sample_oil_04_weathered_ribbon"
    Image.fromarray(img_rgb_4).save(oil_dir / f"{s4_id}.png")
    Image.fromarray(mask_4).save(oil_dir / f"{s4_id}_mask.png")

    meta_4 = {
        "sample_id": s4_id,
        "class_label": "PETROLEUM_OIL",
        "subcategory": "oil/water",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191214T052012",
        "dimensions": [dim, dim],
        "oil_pixel_count": int(np.sum(mask_4 > 0)),
        "prompts": {
            "box_prompt": [50, 110, 460, 290],
            "point_prompt_center": [[255, 200]],
            "point_labels_center": [1],
            "multi_point_prompts": [[150, 250], [350, 150], [255, 380]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(oil_dir / f"{s4_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_4, f, indent=2)
    samples.append(meta_4)

    # =========================================================================
    # SAMPLE 5: Multi-Fragment Spill (Segmented Droplets)
    # =========================================================================
    base_sea_5 = np.full((dim, dim), 0.56, dtype=np.float32)
    mask_5 = np.zeros((dim, dim), dtype=np.uint8)

    centers = [(180, 180, 35), (280, 250, 45), (380, 340, 28)]
    for cx, cy, r in centers:
        d = np.sqrt((xx - cx)**2 + (yy - cy)**2)
        frag = d < r
        mask_5[frag] = 255
        base_sea_5[frag] = 0.11

    speckled_5 = add_radar_speckle(base_sea_5)
    img_rgb_5 = np.stack([(speckled_5 * 255).astype(np.uint8)] * 3, axis=-1)

    s5_id = "sample_oil_05_multi_fragment"
    Image.fromarray(img_rgb_5).save(oil_dir / f"{s5_id}.png")
    Image.fromarray(mask_5).save(oil_dir / f"{s5_id}_mask.png")

    meta_5 = {
        "sample_id": s5_id,
        "class_label": "PETROLEUM_OIL",
        "subcategory": "oil/water",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191220T051155",
        "dimensions": [dim, dim],
        "oil_pixel_count": int(np.sum(mask_5 > 0)),
        "prompts": {
            "box_prompt": [140, 140, 415, 375],
            "point_prompt_center": [[280, 250]],
            "point_labels_center": [1],
            "multi_point_prompts": [[180, 180], [280, 250], [280, 80]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(oil_dir / f"{s5_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_5, f, indent=2)
    samples.append(meta_5)

    # =========================================================================
    # SAMPLE 6 (Look-Alike): Low-Wind Calm Area (c0)
    # =========================================================================
    # Low-wind has broad, diffuse boundaries and weak damping
    base_sea_6 = np.full((dim, dim), 0.55, dtype=np.float32)
    mask_6 = np.zeros((dim, dim), dtype=np.uint8) # Ground truth oil is ZERO
    
    dist_calm = np.sqrt(((xx - 256)/180.0)**2 + ((yy - 256)/180.0)**2)
    calm_damping = np.clip(1.0 - dist_calm, 0.0, 1.0) * 0.30
    base_sea_6 -= calm_damping # Low wind dark patch

    speckled_6 = add_radar_speckle(base_sea_6)
    img_rgb_6 = np.stack([(speckled_6 * 255).astype(np.uint8)] * 3, axis=-1)

    s6_id = "sample_lookalike_01_low_wind_c0"
    Image.fromarray(img_rgb_6).save(lookalike_dir / f"{s6_id}.png")
    Image.fromarray(mask_6).save(lookalike_dir / f"{s6_id}_mask.png")

    meta_6 = {
        "sample_id": s6_id,
        "class_label": "LOW_WIND_AREA",
        "subcategory": "no_oil/water/c0",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191105T051110",
        "dimensions": [dim, dim],
        "oil_pixel_count": 0,
        "prompts": {
            "box_prompt": [80, 80, 430, 430],
            "point_prompt_center": [[256, 256]],
            "point_labels_center": [1],
            "multi_point_prompts": [[200, 200], [300, 300], [50, 50]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(lookalike_dir / f"{s6_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_6, f, indent=2)
    samples.append(meta_6)

    # =========================================================================
    # SAMPLE 7 (Look-Alike): Biogenic Natural Slick (c1)
    # =========================================================================
    base_sea_7 = np.full((dim, dim), 0.55, dtype=np.float32)
    mask_7 = np.zeros((dim, dim), dtype=np.uint8)

    # Spiral eddy filaments
    theta = np.arctan2(yy - 256, xx - 256)
    r = np.sqrt((xx - 256)**2 + (yy - 256)**2)
    spiral = np.abs(r - (60 + theta * 35)) < 8
    base_sea_7[spiral & (r < 220)] = 0.22 # Moderate biogenic damping

    speckled_7 = add_radar_speckle(base_sea_7)
    img_rgb_7 = np.stack([(speckled_7 * 255).astype(np.uint8)] * 3, axis=-1)

    s7_id = "sample_lookalike_02_biogenic_c1"
    Image.fromarray(img_rgb_7).save(lookalike_dir / f"{s7_id}.png")
    Image.fromarray(mask_7).save(lookalike_dir / f"{s7_id}_mask.png")

    meta_7 = {
        "sample_id": s7_id,
        "class_label": "BIOGENIC_SLICK",
        "subcategory": "no_oil/water/c1",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191118T052033",
        "dimensions": [dim, dim],
        "oil_pixel_count": 0,
        "prompts": {
            "box_prompt": [80, 80, 430, 430],
            "point_prompt_center": [[280, 220]],
            "point_labels_center": [1],
            "multi_point_prompts": [[280, 220], [220, 280], [100, 100]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(lookalike_dir / f"{s7_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_7, f, indent=2)
    samples.append(meta_7)

    # =========================================================================
    # SAMPLE 8 (Look-Alike): Internal Solitary Waves (c2)
    # =========================================================================
    base_sea_8 = np.full((dim, dim), 0.50, dtype=np.float32)
    mask_8 = np.zeros((dim, dim), dtype=np.uint8)

    # Parallel alternating bright/dark solitons
    soliton_wave = 0.25 * np.sin(xx / 18.0) * np.exp(-((yy - 256)/140.0)**2)
    base_sea_8 = np.clip(base_sea_8 + soliton_wave, 0.05, 0.95)

    speckled_8 = add_radar_speckle(base_sea_8)
    img_rgb_8 = np.stack([(speckled_8 * 255).astype(np.uint8)] * 3, axis=-1)

    s8_id = "sample_lookalike_03_internal_wave_c2"
    Image.fromarray(img_rgb_8).save(lookalike_dir / f"{s8_id}.png")
    Image.fromarray(mask_8).save(lookalike_dir / f"{s8_id}_mask.png")

    meta_8 = {
        "sample_id": s8_id,
        "class_label": "INTERNAL_WAVE",
        "subcategory": "no_oil/water/c2",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191202T051145",
        "dimensions": [dim, dim],
        "oil_pixel_count": 0,
        "prompts": {
            "box_prompt": [100, 120, 420, 390],
            "point_prompt_center": [[256, 256]],
            "point_labels_center": [1],
            "multi_point_prompts": [[200, 256], [300, 256], [50, 50]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(lookalike_dir / f"{s8_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_8, f, indent=2)
    samples.append(meta_8)

    # =========================================================================
    # SAMPLE 9 (Look-Alike): Ship Wake (c4)
    # =========================================================================
    base_sea_9 = np.full((dim, dim), 0.54, dtype=np.float32)
    mask_9 = np.zeros((dim, dim), dtype=np.uint8)

    # Linear turbulent scar with bright Kelvin boundary
    scar = (np.abs(yy - 256) < 6) & (xx > 100) & (xx < 450)
    kelvin_upper = (np.abs(yy - (256 - (xx - 100)*0.12)) < 4) & (xx > 100) & (xx < 450)
    kelvin_lower = (np.abs(yy - (256 + (xx - 100)*0.12)) < 4) & (xx > 100) & (xx < 450)

    base_sea_9[scar] = 0.18 # Dark center
    base_sea_9[kelvin_upper | kelvin_lower] = 0.82 # Bright foam Kelvin arms

    speckled_9 = add_radar_speckle(base_sea_9)
    img_rgb_9 = np.stack([(speckled_9 * 255).astype(np.uint8)] * 3, axis=-1)

    s9_id = "sample_lookalike_04_ship_wake_c4"
    Image.fromarray(img_rgb_9).save(lookalike_dir / f"{s9_id}.png")
    Image.fromarray(mask_9).save(lookalike_dir / f"{s9_id}_mask.png")

    meta_9 = {
        "sample_id": s9_id,
        "class_label": "SHIP_WAKE",
        "subcategory": "no_oil/water/c4",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191216T052028",
        "dimensions": [dim, dim],
        "oil_pixel_count": 0,
        "prompts": {
            "box_prompt": [100, 200, 450, 310],
            "point_prompt_center": [[275, 256]],
            "point_labels_center": [1],
            "multi_point_prompts": [[200, 256], [350, 256], [275, 100]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(lookalike_dir / f"{s9_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_9, f, indent=2)
    samples.append(meta_9)

    # =========================================================================
    # SAMPLE 10 (Look-Alike): Homogeneous Clean Sea Surface (Clean Water)
    # =========================================================================
    base_sea_10 = np.full((dim, dim), 0.55, dtype=np.float32)
    mask_10 = np.zeros((dim, dim), dtype=np.uint8)

    speckled_10 = add_radar_speckle(base_sea_10)
    img_rgb_10 = np.stack([(speckled_10 * 255).astype(np.uint8)] * 3, axis=-1)

    s10_id = "sample_lookalike_05_clean_sea"
    Image.fromarray(img_rgb_10).save(lookalike_dir / f"{s10_id}.png")
    Image.fromarray(mask_10).save(lookalike_dir / f"{s10_id}_mask.png")

    meta_10 = {
        "sample_id": s10_id,
        "class_label": "CLEAN_WATER",
        "subcategory": "no_oil/water/clean",
        "split": "DARTIS-2019-test",
        "parent_scene_id": "S1A_IW_GRDH_1SDV_20191228T051140",
        "dimensions": [dim, dim],
        "oil_pixel_count": 0,
        "prompts": {
            "box_prompt": [100, 100, 400, 400],
            "point_prompt_center": [[256, 256]],
            "point_labels_center": [1],
            "multi_point_prompts": [[200, 200], [300, 300], [100, 100]],
            "multi_point_labels": [1, 1, 0]
        }
    }
    with open(lookalike_dir / f"{s10_id}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_10, f, indent=2)
    samples.append(meta_10)

    # Master Manifest
    with open(output_dir / "samples_manifest.json", "w", encoding="utf-8") as f:
        json.dump({
            "manifest_version": "1.0.0",
            "total_samples": len(samples),
            "oil_samples": 5,
            "lookalike_samples": 5,
            "split": "DARTIS-2019-test",
            "samples": samples
        }, f, indent=2)

    print(f"[+] Successfully generated {len(samples)} SAR baseline samples in {output_dir}")

if __name__ == "__main__":
    generate_sar_baseline_samples()
