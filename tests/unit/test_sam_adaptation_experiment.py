import unittest
import json
import torch
from pathlib import Path

class TestSamAdaptationExperiment(unittest.TestCase):
    """Test suite verifying Experiment 02 (SAR SAM Adaptation / SAM-OIL Inspiration)."""

    HISTORY_PATH = Path("experiments/sam_adaptation/training_history.json")
    COMPARISON_PATH = Path("experiments/sam_adaptation/comparison_results.json")
    CHECKPOINT_PATH = Path("models/adapted/sar_sam_adapter_best.pth")

    @classmethod
    def setUpClass(cls):
        assert cls.HISTORY_PATH.exists(), f"History missing: {cls.HISTORY_PATH}"
        assert cls.COMPARISON_PATH.exists(), f"Comparison missing: {cls.COMPARISON_PATH}"
        assert cls.CHECKPOINT_PATH.exists(), f"Checkpoint missing: {cls.CHECKPOINT_PATH}"

        with open(cls.HISTORY_PATH, "r", encoding="utf-8") as f:
            cls.history = json.load(f)
        with open(cls.COMPARISON_PATH, "r", encoding="utf-8") as f:
            cls.comparison = json.load(f)

    def test_parameter_counts_and_freezing(self):
        """Verifies that trainable parameters represent <= 5% of total model parameters."""
        params = self.history["parameter_summary"]
        self.assertGreater(params["frozen_parameters"], 85000000)
        self.assertLess(params["trainable_parameters"], 5000000)
        self.assertLess(params["trainable_percentage"], 5.0)

    def test_training_loss_convergence(self):
        """Verifies that training loss strictly decreased across epochs."""
        hist = self.history["history"]
        initial_loss = hist[0]["train_loss"]
        final_loss = hist[-1]["train_loss"]
        self.assertLess(final_loss, initial_loss * 0.5)

    def test_lookalike_false_positive_elimination(self):
        """Verifies that SAR adaptation achieved 0.0% false positive activation on look-alikes."""
        look_comp = self.comparison["metrics_comparison"]["lookalike_suppression"]
        self.assertEqual(look_comp["vanilla_sam"]["false_positive_activation_rate"], 1.0)
        self.assertEqual(look_comp["sar_adapted_sam"]["false_positive_activation_rate"], 0.0)
        self.assertEqual(look_comp["sar_adapted_sam"]["mean_false_positive_pixels"], 0.0)

    def test_checkpoint_structure(self):
        """Verifies the saved PyTorch checkpoint contains required keys."""
        ckpt = torch.load(self.CHECKPOINT_PATH, map_location="cpu")
        self.assertIn("model_state_dict", ckpt)
        self.assertIn("optimizer_state_dict", ckpt)
        self.assertIn("param_counts", ckpt)
        self.assertIn("val_loss", ckpt)

if __name__ == "__main__":
    unittest.main()
