import os
import sys
import time
import json
import numpy as np
import torch
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
from segment_anything import sam_model_registry, SamPredictor
from marineshield.models.sam_adapter import SarSamAdapter

def compute_metrics(pred_mask: np.ndarray, gt_mask: np.ndarray):
    """Computes IoU, Dice, Precision, and Recall between binary uint8 masks."""
    p = (pred_mask > 0).astype(bool)
    g = (gt_mask > 0).astype(bool)

    intersection = np.logical_and(p, g).sum()
    union = np.logical_or(p, g).sum()
    p_sum = p.sum()
    g_sum = g.sum()

    if union == 0:
        iou = 1.0 if (p_sum == 0 and g_sum == 0) else 0.0
        dice = 1.0 if (p_sum == 0 and g_sum == 0) else 0.0
        precision = 1.0 if p_sum == 0 else 0.0
        recall = 1.0 if g_sum == 0 else 0.0
    else:
        iou = float(intersection) / float(union) if union > 0 else 0.0
        dice = float(2.0 * intersection) / float(p_sum + g_sum) if (p_sum + g_sum) > 0 else 0.0
        precision = float(intersection) / float(p_sum) if p_sum > 0 else (1.0 if g_sum == 0 else 0.0)
        recall = float(intersection) / float(g_sum) if g_sum > 0 else 0.0

    return {
        "iou": float(round(iou, 4)),
        "dice": float(round(dice, 4)),
        "precision": float(round(precision, 4)),
        "recall": float(round(recall, 4)),
        "predicted_pixels": int(p_sum),
        "ground_truth_pixels": int(g_sum)
    }

def run_comparison():
    print("=" * 75)
    print("MarineShield — Comparative Benchmark: Vanilla SAM vs SAR-Adapted SAM")
    print("=" * 75)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # 1. Load Vanilla SAM Predictor
    print("Loading Vanilla SAM ViT-B baseline...")
    sam_base = sam_model_registry["vit_b"](checkpoint="models/checkpoints/sam_vit_b_01ec64.pth")
    sam_base.to(device=device)
    sam_base.eval()
    vanilla_predictor = SamPredictor(sam_base)

    # 2. Load SAR-Adapted SAM
    print("Loading SAR-Adapted SAM model...")
    adapted_model = SarSamAdapter(checkpoint_path="models/checkpoints/sam_vit_b_01ec64.pth", device=device)
    best_ckpt = Path("models/adapted/sar_sam_adapter_best.pth")
    assert best_ckpt.exists(), f"Checkpoint missing: {best_ckpt}"
    ckpt_data = torch.load(best_ckpt, map_location=device)
    adapted_model.load_state_dict(ckpt_data["model_state_dict"])
    adapted_model.eval()

    # 3. Load Validation Manifest
    val_dir = Path("data/dartis_val")
    with open(val_dir / "manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    predictions_dir = Path("experiments/sam_adaptation/predictions")
    predictions_dir.mkdir(parents=True, exist_ok=True)

    vanilla_oil_metrics = []
    vanilla_look_metrics = []
    vanilla_latencies = []

    adapted_oil_metrics = []
    adapted_look_metrics = []
    adapted_latencies = []

    sample_comparisons = []

    def preprocess_for_sam(img_np):
        tensor = torch.as_tensor(img_np, device=device).permute(2, 0, 1).contiguous().float()
        tensor_resized = torch.nn.functional.interpolate(tensor.unsqueeze(0), size=(1024, 1024), mode="bilinear", align_corners=False)
        pixel_mean = torch.tensor([123.675, 116.28, 103.53], device=device).view(1, 3, 1, 1)
        pixel_std = torch.tensor([58.395, 57.12, 57.375], device=device).view(1, 3, 1, 1)
        return (tensor_resized - pixel_mean) / pixel_std

    def scale_box_to_1024(box_512):
        return [c * 2.0 for c in box_512]

    print("\nEvaluating both models on identical validation data (DARTIS-2019-val)...")

    for item in manifest["samples"]:
        s_id = item["sample_id"]
        c_label = item["class_label"]
        is_oil = c_label == "PETROLEUM_OIL"
        folder = "oil" if is_oil else "lookalike"

        img_path = val_dir / folder / f"{s_id}.png"
        mask_path = val_dir / folder / f"{s_id}_mask.png"

        image_np = np.array(Image.open(img_path).convert("RGB"))
        gt_mask = np.array(Image.open(mask_path).convert("L"))
        box_512 = item["box_prompt"]

        # --- A. Vanilla SAM Inference ---
        t0_v = time.perf_counter()
        vanilla_predictor.set_image(image_np)
        v_masks, v_scores, _ = vanilla_predictor.predict(box=np.array(box_512), multimask_output=False)
        v_latency_ms = (time.perf_counter() - t0_v) * 1000.0
        v_pred_mask = (v_masks[0] * 255).astype(np.uint8)
        v_m = compute_metrics(v_pred_mask, gt_mask)
        v_m["latency_ms"] = round(v_latency_ms, 2)
        vanilla_latencies.append(v_latency_ms)

        if is_oil:
            vanilla_oil_metrics.append(v_m)
        else:
            vanilla_look_metrics.append(v_m)

        Image.fromarray(v_pred_mask).save(predictions_dir / f"{s_id}_vanilla_sam.png")

        # --- B. SAR-Adapted SAM Inference ---
        t0_a = time.perf_counter()
        with torch.no_grad():
            img_tensor = preprocess_for_sam(image_np)
            box_1024 = torch.as_tensor([scale_box_to_1024(box_512)], device=device, dtype=torch.float32)
            high_res_masks, _ = adapted_model(img_tensor, boxes=box_1024)
            a_pred_binary = (torch.sigmoid(high_res_masks) > 0.5).squeeze().cpu().numpy()
        a_latency_ms = (time.perf_counter() - t0_a) * 1000.0
        a_pred_mask = (a_pred_binary * 255).astype(np.uint8)
        a_m = compute_metrics(a_pred_mask, gt_mask)
        a_m["latency_ms"] = round(a_latency_ms, 2)
        adapted_latencies.append(a_latency_ms)

        if is_oil:
            adapted_oil_metrics.append(a_m)
        else:
            adapted_look_metrics.append(a_m)

        Image.fromarray(a_pred_mask).save(predictions_dir / f"{s_id}_adapted_sam.png")

        sample_rec = {
            "sample_id": s_id,
            "class_label": c_label,
            "is_oil": is_oil,
            "vanilla_sam": v_m,
            "adapted_sam": a_m,
            "iou_improvement": round(a_m["iou"] - v_m["iou"], 4),
            "fp_reduction_pixels": int(v_m["predicted_pixels"] - a_m["predicted_pixels"]) if not is_oil else 0
        }
        sample_comparisons.append(sample_rec)

        tag = "OIL" if is_oil else "LOOK"
        print(f"  [{tag:4s}] {s_id:25s} | Vanilla IoU: {v_m['iou']:.3f} (FP: {v_m['predicted_pixels'] if not is_oil else 0}) -> Adapted IoU: {a_m['iou']:.3f} (FP: {a_m['predicted_pixels'] if not is_oil else 0})")

    # Aggregate Summaries
    summary = {
        "evaluation_split": "DARTIS-2019-val",
        "total_val_samples": len(manifest["samples"]),
        "oil_samples_count": len(vanilla_oil_metrics),
        "lookalike_samples_count": len(vanilla_look_metrics),
        "metrics_comparison": {
            "oil_segmentation": {
                "vanilla_sam": {
                    "mean_iou": round(float(np.mean([m["iou"] for m in vanilla_oil_metrics])), 4),
                    "mean_dice": round(float(np.mean([m["dice"] for m in vanilla_oil_metrics])), 4),
                    "mean_precision": round(float(np.mean([m["precision"] for m in vanilla_oil_metrics])), 4),
                    "mean_recall": round(float(np.mean([m["recall"] for m in vanilla_oil_metrics])), 4)
                },
                "sar_adapted_sam": {
                    "mean_iou": round(float(np.mean([m["iou"] for m in adapted_oil_metrics])), 4),
                    "mean_dice": round(float(np.mean([m["dice"] for m in adapted_oil_metrics])), 4),
                    "mean_precision": round(float(np.mean([m["precision"] for m in adapted_oil_metrics])), 4),
                    "mean_recall": round(float(np.mean([m["recall"] for m in adapted_oil_metrics])), 4)
                }
            },
            "lookalike_suppression": {
                "vanilla_sam": {
                    "false_positive_activation_rate": round(float(np.mean([1.0 if m["predicted_pixels"] > 0 else 0.0 for m in vanilla_look_metrics])), 4),
                    "mean_false_positive_pixels": round(float(np.mean([m["predicted_pixels"] for m in vanilla_look_metrics])), 1)
                },
                "sar_adapted_sam": {
                    "false_positive_activation_rate": round(float(np.mean([1.0 if m["predicted_pixels"] > 0 else 0.0 for m in adapted_look_metrics])), 4),
                    "mean_false_positive_pixels": round(float(np.mean([m["predicted_pixels"] for m in adapted_look_metrics])), 1)
                }
            },
            "latency_benchmarks": {
                "vanilla_sam_mean_latency_ms": round(float(np.mean(vanilla_latencies)), 2),
                "sar_adapted_sam_mean_latency_ms": round(float(np.mean(adapted_latencies)), 2)
            }
        },
        "per_sample_details": sample_comparisons
    }

    out_file = Path("experiments/sam_adaptation/comparison_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[+] Comparison report written to {out_file}")
    print("=" * 75)
    return summary

if __name__ == "__main__":
    run_comparison()
