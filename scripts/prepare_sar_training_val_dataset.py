import json
import math
import numpy as np
from pathlib import Path
from PIL import Image

def generate_split_samples(output_dir: Path, split_name: str, seed: int, n_oil: int = 10, n_lookalike: int = 10):
    """Generates synthetic SAR samples for a specific split following DARTIS specifications."""
    output_dir.mkdir(parents=True, exist_ok=True)
    oil_dir = output_dir / "oil"
    lookalike_dir = output_dir / "lookalike"
    oil_dir.mkdir(parents=True, exist_ok=True)
    lookalike_dir.mkdir(parents=True, exist_ok=True)

    np.random.seed(seed)
    dim = 512

    def add_radar_speckle(img_linear, looks=4):
        noise = np.random.gamma(shape=looks, scale=1.0/looks, size=img_linear.shape)
        return np.clip(img_linear * noise, 0.0, 1.0)

    samples = []
    yy, xx = np.mgrid[0:dim, 0:dim]

    # Generate Oil Samples
    for i in range(1, n_oil + 1):
        s_id = f"{split_name}_oil_{i:02d}"
        base_sea = np.full((dim, dim), 0.55 + np.random.uniform(-0.04, 0.04), dtype=np.float32)
        mask = np.zeros((dim, dim), dtype=np.uint8)

        oil_type = i % 4
        if oil_type == 0: # Linear ribbon
            slope = np.random.uniform(0.5, 1.2)
            intercept = np.random.uniform(20, 80)
            width = np.random.uniform(15, 25)
            ribbon = (np.abs(yy - (slope * xx + intercept)) < width) & (xx > 60) & (xx < 450)
            mask[ribbon] = 255
            base_sea[ribbon] = np.random.uniform(0.10, 0.14)
            ymin, xmin = np.min(np.where(mask > 0), axis=1)
            ymax, xmax = np.max(np.where(mask > 0), axis=1)
            box = [int(xmin), int(ymin), int(xmax), int(ymax)]
        elif oil_type == 1: # Cohesive patch
            cx, cy = np.random.uniform(200, 312), np.random.uniform(200, 312)
            rx, ry = np.random.uniform(70, 110), np.random.uniform(50, 80)
            radial = np.sqrt(((xx - cx)/rx)**2 + ((yy - cy)/ry)**2)
            patch = radial < 1.0
            mask[patch] = 255
            base_sea[patch] = np.random.uniform(0.09, 0.13)
            box = [int(max(0, cx - rx - 5)), int(max(0, cy - ry - 5)), int(min(dim-1, cx + rx + 5)), int(min(dim-1, cy + ry + 5))]
        elif oil_type == 2: # Coastal slick
            coast_x = np.random.uniform(40, 70)
            base_sea[xx < coast_x] = 0.92 # land
            slick = (xx >= coast_x) & (xx < coast_x + np.random.uniform(120, 160)) & (yy > 100) & (yy < 400)
            mask[slick] = 255
            base_sea[slick] = np.random.uniform(0.11, 0.15)
            box = [int(coast_x), 100, int(coast_x + 160), 400]
        else: # Curved weathered ribbon
            freq = np.random.uniform(40, 70)
            amp = np.random.uniform(50, 85)
            curve_y = 250 + amp * np.sin(xx / freq)
            ribbon = (np.abs(yy - curve_y) < 16) & (xx > 50) & (xx < 460)
            mask[ribbon] = 255
            base_sea[ribbon] = np.random.uniform(0.12, 0.16)
            ymin, xmin = np.min(np.where(mask > 0), axis=1)
            ymax, xmax = np.max(np.where(mask > 0), axis=1)
            box = [int(xmin), int(ymin), int(xmax), int(ymax)]

        speckled = add_radar_speckle(base_sea)
        img_rgb = np.stack([(speckled * 255).astype(np.uint8)] * 3, axis=-1)

        Image.fromarray(img_rgb).save(oil_dir / f"{s_id}.png")
        Image.fromarray(mask).save(oil_dir / f"{s_id}_mask.png")

        meta = {
            "sample_id": s_id,
            "class_label": "PETROLEUM_OIL",
            "split": split_name,
            "dimensions": [dim, dim],
            "oil_pixel_count": int(np.sum(mask > 0)),
            "box_prompt": box,
            "center_point": [int((box[0] + box[2]) // 2), int((box[1] + box[3]) // 2)]
        }
        with open(oil_dir / f"{s_id}_meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        samples.append(meta)

    # Generate Look-Alike Samples (Ground truth mask = 0 everywhere)
    look_classes = ["LOW_WIND_AREA", "BIOGENIC_SLICK", "INTERNAL_WAVE", "SHIP_WAKE", "CLEAN_WATER"]
    for i in range(1, n_lookalike + 1):
        s_id = f"{split_name}_lookalike_{i:02d}"
        c_name = look_classes[(i - 1) % len(look_classes)]
        base_sea = np.full((dim, dim), 0.55 + np.random.uniform(-0.03, 0.03), dtype=np.float32)
        mask = np.zeros((dim, dim), dtype=np.uint8)

        if c_name == "LOW_WIND_AREA":
            dist_calm = np.sqrt(((xx - 256)/180.0)**2 + ((yy - 256)/180.0)**2)
            base_sea -= np.clip(1.0 - dist_calm, 0.0, 1.0) * np.random.uniform(0.25, 0.32)
            box = [80, 80, 430, 430]
        elif c_name == "BIOGENIC_SLICK":
            theta = np.arctan2(yy - 256, xx - 256)
            r = np.sqrt((xx - 256)**2 + (yy - 256)**2)
            spiral = np.abs(r - (60 + theta * 35)) < 10
            base_sea[spiral & (r < 220)] = np.random.uniform(0.20, 0.25)
            box = [80, 80, 430, 430]
        elif c_name == "INTERNAL_WAVE":
            soliton = 0.25 * np.sin(xx / 20.0) * np.exp(-((yy - 256)/140.0)**2)
            base_sea = np.clip(base_sea + soliton, 0.05, 0.95)
            box = [100, 120, 420, 390]
        elif c_name == "SHIP_WAKE":
            scar = (np.abs(yy - 256) < 6) & (xx > 100) & (xx < 450)
            base_sea[scar] = 0.18
            box = [100, 200, 450, 310]
        else: # CLEAN_WATER
            box = [100, 100, 400, 400]

        speckled = add_radar_speckle(base_sea)
        img_rgb = np.stack([(speckled * 255).astype(np.uint8)] * 3, axis=-1)

        Image.fromarray(img_rgb).save(lookalike_dir / f"{s_id}.png")
        Image.fromarray(mask).save(lookalike_dir / f"{s_id}_mask.png")

        meta = {
            "sample_id": s_id,
            "class_label": c_name,
            "split": split_name,
            "dimensions": [dim, dim],
            "oil_pixel_count": 0,
            "box_prompt": box,
            "center_point": [int((box[0] + box[2]) // 2), int((box[1] + box[3]) // 2)]
        }
        with open(lookalike_dir / f"{s_id}_meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        samples.append(meta)

    manifest = {
        "split": split_name,
        "total_samples": len(samples),
        "oil_samples": n_oil,
        "lookalike_samples": n_lookalike,
        "samples": samples
    }
    with open(output_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Created {len(samples)} samples for split '{split_name}' in {output_dir}")
    return manifest

if __name__ == "__main__":
    # Generate Training Split (DARTIS-2019-train: 20 samples, seed 101)
    generate_split_samples(Path("data/dartis_train"), "DARTIS-2019-train", seed=101, n_oil=10, n_lookalike=10)
    # Generate Validation Split (DARTIS-2019-val: 10 samples, seed 202)
    generate_split_samples(Path("data/dartis_val"), "DARTIS-2019-val", seed=202, n_oil=5, n_lookalike=5)
