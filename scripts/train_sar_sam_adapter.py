import os
import sys
import time
import json
import numpy as np
import torch
from pathlib import Path
from PIL import Image

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from marineshield.models.sam_adapter import SarSamAdapter

def load_dataset_samples(data_dir: Path):
    """Loads images, masks, and prompt metadata from a split directory."""
    manifest_path = data_dir / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    samples = []
    for item in manifest["samples"]:
        s_id = item["sample_id"]
        is_oil = item["class_label"] == "PETROLEUM_OIL"
        folder = "oil" if is_oil else "lookalike"
        
        img_path = data_dir / folder / f"{s_id}.png"
        mask_path = data_dir / folder / f"{s_id}_mask.png"

        # Load Image: SAM expects (3, 1024, 1024) or input resized through transform
        # For SAM, we normalize and convert to tensor
        img_np = np.array(Image.open(img_path).convert("RGB"))
        mask_np = np.array(Image.open(mask_path).convert("L"))

        samples.append({
            "sample_id": s_id,
            "class_label": item["class_label"],
            "is_oil": is_oil,
            "image_np": img_np,
            "mask_np": mask_np,
            "box_prompt": item["box_prompt"],
            "center_point": item["center_point"]
        })
    return samples

def train_sar_sam():
    print("=" * 70)
    print("MarineShield — Training Controlled SAR SAM Adapter (SAM-OIL Inspiration)")
    print("=" * 70)

    torch.manual_seed(42)
    np.random.seed(42)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # 1. Instantiate Model
    model = SarSamAdapter(checkpoint_path="models/checkpoints/sam_vit_b_01ec64.pth", device=device)
    param_counts = model.count_parameters()
    print(f"Total Parameters:     {param_counts['total_parameters']:,}")
    print(f"Trainable Parameters: {param_counts['trainable_parameters']:,} ({param_counts['trainable_percentage']}%)")
    print(f"Frozen Parameters:    {param_counts['frozen_parameters']:,}")

    # 2. Load Datasets
    train_samples = load_dataset_samples(Path("data/dartis_train"))
    val_samples = load_dataset_samples(Path("data/dartis_val"))
    print(f"\nLoaded {len(train_samples)} training samples (DARTIS-2019-train)")
    print(f"Loaded {len(val_samples)} validation samples (DARTIS-2019-val)")

    # 3. Optimizer and Scheduler
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=1e-4, weight_decay=1e-4)
    num_epochs = 15
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs, eta_min=1e-6)

    output_dir = Path("models/adapted")
    output_dir.mkdir(parents=True, exist_ok=True)
    history = []
    best_val_loss = float("inf")

    # SAM preprocessor helper: converts 512x512 RGB to SAM input tensor (1, 3, 1024, 1024)
    def preprocess_for_sam(img_np):
        # SAM expects pixels normalized with pixel_mean and pixel_std
        tensor = torch.as_tensor(img_np, device=device).permute(2, 0, 1).contiguous().float()
        # Scale to 1024x1024
        tensor_resized = torch.nn.functional.interpolate(tensor.unsqueeze(0), size=(1024, 1024), mode="bilinear", align_corners=False)
        # Apply SAM normalization
        pixel_mean = torch.tensor([123.675, 116.28, 103.53], device=device).view(1, 3, 1, 1)
        pixel_std = torch.tensor([58.395, 57.12, 57.375], device=device).view(1, 3, 1, 1)
        return (tensor_resized - pixel_mean) / pixel_std

    def scale_box_to_1024(box_512):
        # Scale box coords from 512 to 1024
        return [c * 2.0 for c in box_512]

    # 4. Training Loop
    print("\nBeginning training loop across 15 epochs...")
    t0_train = time.perf_counter()

    for epoch in range(1, num_epochs + 1):
        model.train()
        train_losses = []
        bce_losses = []
        dice_losses = []

        # Shuffle training samples
        indices = np.random.permutation(len(train_samples))
        for idx in indices:
            item = train_samples[idx]
            img_tensor = preprocess_for_sam(item["image_np"])
            gt_mask_tensor = torch.as_tensor(item["mask_np"] > 0, device=device, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            
            box_1024 = torch.as_tensor([scale_box_to_1024(item["box_prompt"])], device=device, dtype=torch.float32)

            optimizer.zero_grad()
            high_res_masks, _ = model(img_tensor, boxes=box_1024)
            
            loss_dict = model.compute_loss(high_res_masks, gt_mask_tensor)
            loss_dict["total_loss"].backward()
            optimizer.step()

            train_losses.append(loss_dict["total_loss"].item())
            bce_losses.append(loss_dict["bce_loss"])
            dice_losses.append(loss_dict["dice_loss"])

        scheduler.step()

        # Validation Pass
        model.eval()
        val_losses = []
        val_oil_ious = []
        val_look_fp_pixels = []

        with torch.no_grad():
            for item in val_samples:
                img_tensor = preprocess_for_sam(item["image_np"])
                gt_mask_tensor = torch.as_tensor(item["mask_np"] > 0, device=device, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                box_1024 = torch.as_tensor([scale_box_to_1024(item["box_prompt"])], device=device, dtype=torch.float32)

                high_res_masks, _ = model(img_tensor, boxes=box_1024)
                v_loss = model.compute_loss(high_res_masks, gt_mask_tensor)
                val_losses.append(v_loss["total_loss"].item())

                # Mask evaluation
                pred_binary = (torch.sigmoid(high_res_masks) > 0.5).squeeze().cpu().numpy()
                gt_binary = item["mask_np"] > 0
                
                if item["is_oil"]:
                    inter = np.logical_and(pred_binary, gt_binary).sum()
                    union = np.logical_or(pred_binary, gt_binary).sum()
                    val_oil_ious.append(inter / union if union > 0 else 0.0)
                else:
                    fp_px = int(pred_binary.sum())
                    val_look_fp_pixels.append(fp_px)

        mean_train_loss = float(np.mean(train_losses))
        mean_val_loss = float(np.mean(val_losses))
        mean_val_oil_iou = float(np.mean(val_oil_ious))
        mean_val_fp_px = float(np.mean(val_look_fp_pixels))

        epoch_rec = {
            "epoch": epoch,
            "train_loss": round(mean_train_loss, 4),
            "val_loss": round(mean_val_loss, 4),
            "val_oil_mean_iou": round(mean_val_oil_iou, 4),
            "val_lookalike_mean_fp_pixels": round(mean_val_fp_px, 1),
            "lr": round(optimizer.param_groups[0]["lr"], 6)
        }
        history.append(epoch_rec)

        print(f"Epoch [{epoch:02d}/{num_epochs:02d}] | Train Loss: {mean_train_loss:.4f} | Val Loss: {mean_val_loss:.4f} | Val Oil IoU: {mean_val_oil_iou:.4f} | Lookalike FP Px: {mean_val_fp_px:.0f}")

        # Save Best Model Checkpoint
        if mean_val_loss < best_val_loss:
            best_val_loss = mean_val_loss
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": best_val_loss,
                "param_counts": param_counts
            }, output_dir / "sar_sam_adapter_best.pth")

    total_time_sec = time.perf_counter() - t0_train
    print(f"\n[+] Training complete in {total_time_sec:.2f}s! Best Val Loss: {best_val_loss:.4f}")

    # Save training history
    history_file = Path("experiments/sam_adaptation/training_history.json")
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump({
            "experiment_id": "EXP-02-SAR-SAM-ADAPTATION",
            "epochs": num_epochs,
            "train_time_sec": round(total_time_sec, 2),
            "best_val_loss": round(best_val_loss, 4),
            "parameter_summary": param_counts,
            "history": history
        }, f, indent=2)
    print(f"[+] Training log saved to {history_file}")

if __name__ == "__main__":
    train_sar_sam()
