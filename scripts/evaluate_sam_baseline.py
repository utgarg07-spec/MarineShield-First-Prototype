import os
import time
import json
import numpy as np
import torch
from pathlib import Path
from PIL import Image
from segment_anything import sam_model_registry, SamPredictor

def compute_binary_metrics(pred_mask: np.ndarray, gt_mask: np.ndarray):
    """Computes IoU, Dice, Precision, and Recall between binary boolean/uint8 masks."""
    p = (pred_mask > 0).astype(bool)
    g = (gt_mask > 0).astype(bool)

    intersection = np.logical_and(p, g).sum()
    union = np.logical_or(p, g).sum()
    p_sum = p.sum()
    g_sum = g.sum()

    if union == 0:
        # Both masks are empty (e.g. perfect true negative on clean water/look-alike)
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

def run_sam_baseline_experiment():
    print("=" * 70)
    print("MarineShield — Experiment 01: Vanilla Meta SAM (ViT-B) SAR Baseline")
    print("=" * 70)

    # 1. Device and GPU Setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
        gpu_name = torch.cuda.get_device_name(0)
        gpu_total_mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"GPU: {gpu_name} ({gpu_total_mem_gb:.2f} GB VRAM)")
    else:
        gpu_name = "CPU"
        gpu_total_mem_gb = 0.0

    # 2. Model Loading
    checkpoint_path = Path("models/checkpoints/sam_vit_b_01ec64.pth")
    assert checkpoint_path.exists(), f"Checkpoint missing: {checkpoint_path}"
    checkpoint_size_mb = checkpoint_path.stat().st_size / (1024 * 1024)
    print(f"Loading SAM ViT-B checkpoint from {checkpoint_path} ({checkpoint_size_mb:.2f} MB)...")

    t0_load = time.perf_counter()
    sam = sam_model_registry["vit_b"](checkpoint=str(checkpoint_path))
    sam.to(device=device)
    sam.eval()
    predictor = SamPredictor(sam)
    load_time_sec = time.perf_counter() - t0_load
    print(f"[+] Model loaded in {load_time_sec:.2f}s")

    # 3. Load Samples Manifest
    samples_dir = Path("data/samples")
    manifest_path = samples_dir / "samples_manifest.json"
    assert manifest_path.exists(), f"Manifest missing: {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    predictions_dir = Path("experiments/sam_baseline/predictions")
    predictions_dir.mkdir(parents=True, exist_ok=True)

    results_by_prompt = {
        "box_prompt": [],
        "point_prompt_center": [],
        "multi_point_prompts": []
    }
    sample_records = []

    print("\nEvaluating samples across 3 controlled prompt strategies...")

    for sample_meta in manifest["samples"]:
        s_id = sample_meta["sample_id"]
        c_label = sample_meta["class_label"]
        subcat = sample_meta["subcategory"]
        is_oil = c_label == "PETROLEUM_OIL"

        # Determine file path (oil vs lookalike dir)
        folder = "oil" if is_oil else "lookalike"
        img_path = samples_dir / folder / f"{s_id}.png"
        mask_path = samples_dir / folder / f"{s_id}_mask.png"

        image_pil = Image.open(img_path).convert("RGB")
        image_np = np.array(image_pil)
        gt_mask = np.array(Image.open(mask_path).convert("L"))

        # Time image embedding
        t0_emb = time.perf_counter()
        with torch.no_grad():
            predictor.set_image(image_np)
        emb_time_ms = (time.perf_counter() - t0_emb) * 1000.0

        sample_eval = {
            "sample_id": s_id,
            "class_label": c_label,
            "subcategory": subcat,
            "is_oil": is_oil,
            "embedding_time_ms": round(emb_time_ms, 2),
            "prompts_evaluated": {}
        }

        # --- A. Box Prompt ---
        box = np.array(sample_meta["prompts"]["box_prompt"])
        t0_box = time.perf_counter()
        with torch.no_grad():
            masks, scores, _ = predictor.predict(
                box=box,
                multimask_output=False
            )
        box_infer_ms = (time.perf_counter() - t0_box) * 1000.0
        pred_box = masks[0]
        metrics_box = compute_binary_metrics(pred_box, gt_mask)
        metrics_box["decode_time_ms"] = round(box_infer_ms, 2)
        metrics_box["total_time_ms"] = round(emb_time_ms + box_infer_ms, 2)
        metrics_box["sam_confidence_score"] = float(round(scores[0], 4))
        sample_eval["prompts_evaluated"]["box_prompt"] = metrics_box
        results_by_prompt["box_prompt"].append({"is_oil": is_oil, **metrics_box})

        # Save prediction visualization
        pred_box_img = Image.fromarray((pred_box * 255).astype(np.uint8))
        pred_box_img.save(predictions_dir / f"{s_id}_pred_box.png")

        # --- B. Single Center Point Prompt ---
        pt_coords = np.array(sample_meta["prompts"]["point_prompt_center"])
        pt_labels = np.array(sample_meta["prompts"]["point_labels_center"])
        t0_pt = time.perf_counter()
        with torch.no_grad():
            masks_pt, scores_pt, _ = predictor.predict(
                point_coords=pt_coords,
                point_labels=pt_labels,
                multimask_output=True # 3 ambiguous masks for point
            )
        pt_infer_ms = (time.perf_counter() - t0_pt) * 1000.0
        # Best mask by SAM internal score
        best_idx = np.argmax(scores_pt)
        pred_pt = masks_pt[best_idx]
        metrics_pt = compute_binary_metrics(pred_pt, gt_mask)
        metrics_pt["decode_time_ms"] = round(pt_infer_ms, 2)
        metrics_pt["total_time_ms"] = round(emb_time_ms + pt_infer_ms, 2)
        metrics_pt["sam_confidence_score"] = float(round(scores_pt[best_idx], 4))
        sample_eval["prompts_evaluated"]["point_prompt_center"] = metrics_pt
        results_by_prompt["point_prompt_center"].append({"is_oil": is_oil, **metrics_pt})

        pred_pt_img = Image.fromarray((pred_pt * 255).astype(np.uint8))
        pred_pt_img.save(predictions_dir / f"{s_id}_pred_center_point.png")

        # --- C. Multi-Point Prompt (Positive + Negative) ---
        m_coords = np.array(sample_meta["prompts"]["multi_point_prompts"])
        m_labels = np.array(sample_meta["prompts"]["multi_point_labels"])
        t0_mpt = time.perf_counter()
        with torch.no_grad():
            masks_mpt, scores_mpt, _ = predictor.predict(
                point_coords=m_coords,
                point_labels=m_labels,
                multimask_output=True
            )
        mpt_infer_ms = (time.perf_counter() - t0_mpt) * 1000.0
        best_mpt_idx = np.argmax(scores_mpt)
        pred_mpt = masks_mpt[best_mpt_idx]
        metrics_mpt = compute_binary_metrics(pred_mpt, gt_mask)
        metrics_mpt["decode_time_ms"] = round(mpt_infer_ms, 2)
        metrics_mpt["total_time_ms"] = round(emb_time_ms + mpt_infer_ms, 2)
        metrics_mpt["sam_confidence_score"] = float(round(scores_mpt[best_mpt_idx], 4))
        sample_eval["prompts_evaluated"]["multi_point_prompts"] = metrics_mpt
        results_by_prompt["multi_point_prompts"].append({"is_oil": is_oil, **metrics_mpt})

        pred_mpt_img = Image.fromarray((pred_mpt * 255).astype(np.uint8))
        pred_mpt_img.save(predictions_dir / f"{s_id}_pred_multi_point.png")

        sample_records.append(sample_eval)
        print(f"  [{'OIL' if is_oil else 'LOOKALIKE':9s}] {s_id[:35]:35s} | Box IoU: {metrics_box['iou']:.3f} | Pt IoU: {metrics_pt['iou']:.3f} | M-Pt IoU: {metrics_mpt['iou']:.3f}")

    # Peak GPU Memory
    if device == "cuda":
        peak_vram_mb = torch.cuda.max_memory_allocated() / (1024 * 1024)
        print(f"\n[+] Peak GPU VRAM allocated: {peak_vram_mb:.2f} MB")
    else:
        peak_vram_mb = 0.0

    # Aggregate Metrics Calculation
    summary_by_prompt = {}
    for prompt_name, p_results in results_by_prompt.items():
        oil_res = [r for r in p_results if r["is_oil"]]
        look_res = [r for r in p_results if not r["is_oil"]]

        mean_oil_iou = float(np.mean([r["iou"] for r in oil_res]))
        mean_oil_dice = float(np.mean([r["dice"] for r in oil_res]))
        mean_oil_prec = float(np.mean([r["precision"] for r in oil_res]))
        mean_oil_rec = float(np.mean([r["recall"] for r in oil_res]))
        mean_total_time_ms = float(np.mean([r["total_time_ms"] for r in p_results]))
        
        # Look-alike False Positive Analysis
        look_fp_pixels = [r["predicted_pixels"] for r in look_res]
        look_fp_rate = float(np.mean([1.0 if px > 0 else 0.0 for px in look_fp_pixels]))

        summary_by_prompt[prompt_name] = {
            "oil_samples": {
                "mean_iou": round(mean_oil_iou, 4),
                "mean_dice": round(mean_oil_dice, 4),
                "mean_precision": round(mean_oil_prec, 4),
                "mean_recall": round(mean_oil_rec, 4)
            },
            "lookalike_samples": {
                "false_positive_activation_rate": round(look_fp_rate, 4),
                "mean_false_positive_pixels_per_patch": float(round(np.mean(look_fp_pixels), 1))
            },
            "timing_benchmarks": {
                "mean_total_latency_ms": round(mean_total_time_ms, 2)
            }
        }

    experiment_report = {
        "experiment_id": "EXP-01-SAM-VIT-B-SAR-BASELINE",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_architecture": "Segment Anything Model (SAM) — ViT-B Backbone",
        "model_checkpoint": "sam_vit_b_01ec64.pth",
        "model_parameters_m": 93.7,
        "dataset_version_id": "DARTIS-2019-test",
        "split": "TEST_BENCHMARK",
        "hardware": {
            "device": device,
            "gpu_name": gpu_name,
            "peak_vram_allocated_mb": round(peak_vram_mb, 2)
        },
        "summary_metrics_by_prompt": summary_by_prompt,
        "per_sample_evaluations": sample_records
    }

    out_json = Path("experiments/sam_baseline/baseline_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(experiment_report, f, indent=2)

    print(f"\n[+] Results saved to {out_json}")
    print("=" * 70)
    return experiment_report

if __name__ == "__main__":
    run_sam_baseline_experiment()
