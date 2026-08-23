import unittest
import json
from pathlib import Path

class TestSamBaselineExperiment(unittest.TestCase):
    """Test suite verifying Experiment 01 (Vanilla SAM ViT-B Baseline) results and artifacts."""

    RESULTS_PATH = Path("experiments/sam_baseline/baseline_results.json")
    PREDICTIONS_DIR = Path("experiments/sam_baseline/predictions")

    @classmethod
    def setUpClass(cls):
        assert cls.RESULTS_PATH.exists(), f"Results missing: {cls.RESULTS_PATH}"
        with open(cls.RESULTS_PATH, "r", encoding="utf-8") as f:
            cls.report = json.load(f)

    def test_experiment_metadata(self):
        """Verifies model, checkpoint, parameter count, and dataset split metadata."""
        self.assertEqual(self.report["experiment_id"], "EXP-01-SAM-VIT-B-SAR-BASELINE")
        self.assertEqual(self.report["model_checkpoint"], "sam_vit_b_01ec64.pth")
        self.assertEqual(self.report["dataset_version_id"], "DARTIS-2019-test")
        self.assertAlmostEqual(self.report["model_parameters_m"], 93.7, places=1)
        self.assertEqual(len(self.report["per_sample_evaluations"]), 10)

    def test_box_prompt_metrics(self):
        """Verifies oil and lookalike summary metrics under bounding box prompting."""
        box_metrics = self.report["summary_metrics_by_prompt"]["box_prompt"]
        
        # Oil segmentation accuracy
        oil = box_metrics["oil_samples"]
        self.assertGreater(oil["mean_iou"], 0.95)
        self.assertGreater(oil["mean_dice"], 0.98)
        self.assertGreater(oil["mean_precision"], 0.98)
        self.assertGreater(oil["mean_recall"], 0.98)

        # Look-alike false positive behavior
        look = box_metrics["lookalike_samples"]
        self.assertEqual(look["false_positive_activation_rate"], 1.0)
        self.assertGreater(look["mean_false_positive_pixels_per_patch"], 10000)

    def test_predictions_exist_on_disk(self):
        """Verifies that predicted mask files were properly saved to disk."""
        self.assertTrue(self.PREDICTIONS_DIR.exists())
        pred_files = list(self.PREDICTIONS_DIR.glob("*.png"))
        self.assertGreaterEqual(len(pred_files), 30) # 10 samples * 3 prompts

    def test_hardware_profiling(self):
        """Verifies GPU allocation records within 6GB hardware limits."""
        hw = self.report["hardware"]
        if hw["device"] == "cuda":
            self.assertLess(hw["peak_vram_allocated_mb"], 4000.0) # < 4 GB used
            self.assertGreater(hw["peak_vram_allocated_mb"], 1000.0)

if __name__ == "__main__":
    unittest.main()
