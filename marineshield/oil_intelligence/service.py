import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
import numpy as np
import torch

from marineshield.models.sam_adapter import SarSamAdapter
from marineshield.oil_intelligence.schemas import (
    SpillDetectionResponse,
    SpillMaskContract,
    SpillGeometryContract,
    LookAlikeVerificationContract,
    SpillSeverityContract,
    DataQualityIndex,
    ProvenanceBlock,
    AbstentionDetails
)
from marineshield.oil_intelligence.preprocessing import SarTilePreprocessor
from marineshield.oil_intelligence.geometry_extractor import SpillGeometryExtractor
from marineshield.oil_intelligence.lookalike_classifier import LookAlikeVerifier
from marineshield.oil_intelligence.severity_classifier import SpillSeverityClassifier

class OilIntelligenceService:
    """Production Oil Intelligence Service for MarineShield.

    
    Coordinates the end-to-end ML pipeline:
    SAR Tile -> Candidate Detection -> Adapted SAM -> Probability Mask -> Geometry -> Look-Alike -> Severity -> Abstention
    
    Conforms to all canonical contracts defined in docs/ml/OIL_INTELLIGENCE_CONTRACTS.md.
    """
    def __init__(
        self,
        adapter_checkpoint_path: str = "models/adapted/sar_sam_adapter_best.pth",
        base_sam_checkpoint_path: str = "models/checkpoints/sam_vit_b_01ec64.pth",
        device: Optional[str] = None,
        min_dqi_threshold: float = 0.35,
        model_version_id: str = "sam-vit-b-sar-adapter-v1.0.0",
        dataset_version_id: str = "DARTIS-2019-v1.0"
    ):
        self.adapter_checkpoint_path = Path(adapter_checkpoint_path)
        self.base_sam_checkpoint_path = Path(base_sam_checkpoint_path)
        self.min_dqi_threshold = min_dqi_threshold
        self.model_version_id = model_version_id
        self.dataset_version_id = dataset_version_id
        
        # Select device
        if device is None:
            self.device_type = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device_type = device

        self.preprocessor = SarTilePreprocessor(target_size=(512, 512))
        self.geometry_extractor = SpillGeometryExtractor(min_area_px=50, pixel_resolution_m=10.0)
        self.lookalike_verifier = LookAlikeVerifier()
        self.severity_classifier = SpillSeverityClassifier()

        self._model: Optional[SarSamAdapter] = None

    def _validate_checkpoint_path(self, path: Path):
        """Validates that checkpoint path resides within approved model directories."""
        resolved_str = str(path.resolve()).replace("\\", "/")
        if "models/" not in resolved_str and "models/checkpoints" not in resolved_str and "models/adapted" not in resolved_str:
            raise ValueError(f"DISALLOWED_MODEL_PATH: Model checkpoint path '{path}' is not within approved model directories.")

    def _ensure_model_loaded(self):
        """Loads and verifies adapted SAM model checkpoint."""
        if self._model is not None:
            return

        self._validate_checkpoint_path(self.base_sam_checkpoint_path)
        self._validate_checkpoint_path(self.adapter_checkpoint_path)

        if not self.base_sam_checkpoint_path.exists():
            raise FileNotFoundError(f"Base SAM checkpoint missing at {self.base_sam_checkpoint_path}")
        if not self.adapter_checkpoint_path.exists():
            raise FileNotFoundError(f"Adapted SAM checkpoint missing at {self.adapter_checkpoint_path}")

        print(f"[OilIntelligenceService] Initializing SarSamAdapter on {self.device_type}...")
        model = SarSamAdapter(
            checkpoint_path=str(self.base_sam_checkpoint_path),
            device=self.device_type
        )
        
        # Load adapted weights
        print(f"[OilIntelligenceService] Loading adapted weights from {self.adapter_checkpoint_path}...")
        checkpoint = torch.load(str(self.adapter_checkpoint_path), map_location=self.device_type, weights_only=True)
        if "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint)

        model.eval()
        self._model = model

    def process_tile(
        self,
        input_source: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SpillDetectionResponse:
        """Processes a single SAR tile through the complete canonical Oil Intelligence pipeline.

        
        :param input_source: File path, numpy array (512, 512), or PyTorch Tensor.
        :param metadata: Contextual metadata (sar_granule_id, tile_id, tile_bounds, data_quality, prompts).
        :return: Canonical SpillDetectionResponse object.
        """
        meta = metadata or {}
        incident_id = meta.get("incident_id", str(uuid.uuid4()))
        tile_id = meta.get("tile_id", f"T_{str(uuid.uuid4())[:8]}")
        sar_granule_id = meta.get("sar_granule_id", "S1A_IW_GRDH_UNKNOWN")
        tile_bounds = meta.get("tile_bounds", (72.0, 18.0, 72.5, 18.5))

        # 1. Data Quality Evaluation (§11)
        raw_dqi = meta.get("data_quality", {})
        dqi_score = float(raw_dqi.get("index", 1.0) if isinstance(raw_dqi, dict) else raw_dqi)
        quality_flags = list(raw_dqi.get("quality_flags", []) if isinstance(raw_dqi, dict) else [])
        
        dqi_obj = DataQualityIndex(index=dqi_score, quality_flags=quality_flags)

        # 2. Hard Abstention Gating (§10)
        if dqi_score < self.min_dqi_threshold or "ORBIT_CORRECTION_FAILED" in quality_flags or "FATAL_DATA_CORRUPTION" in quality_flags:
            abstention = AbstentionDetails(
                abstention_reason_primary="LOW_DATA_QUALITY",
                abstention_reasons_all=["LOW_DATA_QUALITY", *quality_flags],
                triggering_values={
                    "data_quality_index": dqi_score,
                    "configured_min_dqi": self.min_dqi_threshold
                },
                recommendation="ANALYST_REVIEW_REQUIRED"
            )
            dummy_verification = LookAlikeVerificationContract(
                sar_granule_id=sar_granule_id,
                predicted_class="ABSTAINED",
                pipeline_decision="ABSTAIN"
            )
            dummy_severity = SpillSeverityContract(
                severity_class="UNKNOWN"
            )
            return SpillDetectionResponse(
                incident_id=incident_id,
                tile_id=tile_id,
                sar_granule_id=sar_granule_id,
                status="ABSTAINED",
                is_abstained=True,
                abstention_details=abstention,
                spill_mask=None,
                spill_geometry=None,
                lookalike_verification=dummy_verification,
                severity=dummy_severity,
                data_quality=dqi_obj
            )

        # 3. Deterministic Preprocessing
        raw_arr = self.preprocessor.load_and_validate(input_source)
        input_tensor = self.preprocessor.normalize_for_sam(raw_arr).to(self.device_type)
        candidate_meta = self.preprocessor.detect_candidate_regions(raw_arr)

        # 4. Prompt Preparation
        if "prompts" in meta and "box_prompt" in meta["prompts"]:
            box_512 = meta["prompts"]["box_prompt"]
            box_1024 = self.preprocessor.scale_box_to_sam(box_512)
            boxes = torch.tensor([box_1024], device=self.device_type, dtype=torch.float32)
        elif candidate_meta["has_candidate"]:
            box_1024 = self.preprocessor.scale_box_to_sam(candidate_meta["bounding_box"])
            boxes = torch.tensor([box_1024], device=self.device_type, dtype=torch.float32)
        else:
            boxes = torch.tensor([[0, 0, 1024, 1024]], device=self.device_type, dtype=torch.float32)

        # 5. Model Inference with Adapted SAM
        self._ensure_model_loaded()
        with torch.no_grad():
            pred_masks, iou_predictions = self._model(input_tensor, boxes=boxes)
            prob_mask = torch.sigmoid(pred_masks[0, 0]).cpu().numpy()

        oil_pixels = int(np.sum(prob_mask >= 0.50))
        mean_oil_prob = float(np.mean(prob_mask[prob_mask >= 0.50])) if oil_pixels > 0 else 0.0
        pixel_coverage = float(oil_pixels / (512.0 * 512.0))

        # 6. Vector Geometry Extraction (§7)
        geometry_feature = self.geometry_extractor.extract_geometry(
            prob_mask=prob_mask,
            threshold=0.50,
            tile_bounds=tile_bounds
        )

        spill_geometry = None
        if geometry_feature:
            spill_geometry = SpillGeometryContract(
                incident_id=incident_id,
                geometry_geojson=geometry_feature,
                properties=geometry_feature.get("properties", {}),
                model_confidence={
                    "mean_oil_probability_within_polygon": geometry_feature.get("properties", {}).get("mean_oil_probability", 0.0),
                    "polygon_pixel_count": geometry_feature.get("properties", {}).get("pixel_count", 0)
                }
            )

        # 7. Look-Alike Verification (§6)
        lookalike_res = self.lookalike_verifier.verify_candidate(
            raw_tile=raw_arr,
            prob_mask=prob_mask,
            candidate_meta=candidate_meta
        )
        lookalike_res.sar_granule_id = sar_granule_id

        # 8. Operational Severity Classification (§5)
        area_km2 = geometry_feature.get("properties", {}).get("area_km2", 0.0) if geometry_feature else 0.0
        # SAR backscatter damping proxy (dB)
        mean_db = float(np.mean(raw_arr))
        suppression_db = float(candidate_meta.get("suppression_contrast", 0.0))
        
        is_valid_oil = (lookalike_res.predicted_class == "PETROLEUM_OIL" and spill_geometry is not None)
        severity_res = self.severity_classifier.classify_severity(
            mean_db=mean_db,
            suppression_db=suppression_db,
            area_km2=area_km2,
            is_valid_detection=is_valid_oil
        )

        # 9. Determine Overall Status
        if lookalike_res.predicted_class == "PETROLEUM_OIL" and spill_geometry is not None:
            overall_status = "OIL_DETECTED"
        elif lookalike_res.predicted_class in ["BIOGENIC_SLICK", "LOW_WIND_AREA", "SHIP_WAKE", "NATURAL_FILM"]:
            overall_status = "LOOKALIKE_REJECTED"
        elif lookalike_res.predicted_class == "UNCERTAIN":
            overall_status = "UNCERTAIN_ANALYSIS"
        else:
            overall_status = "NO_CANDIDATE_FOUND"

        # 10. Build Spill Mask Contract (§1)
        spill_mask = SpillMaskContract(
            incident_id=incident_id,
            tile_id=tile_id,
            sar_granule_id=sar_granule_id,
            binarization_threshold=0.50,
            model_confidence={
                "mean_oil_probability": round(mean_oil_prob, 4),
                "pixel_coverage_fraction": round(pixel_coverage, 4)
            },
            data_quality=dqi_obj
        )

        # 11. Build Provenance Record (§9)
        provenance = ProvenanceBlock(
            sar_granule_id=sar_granule_id,
            model_version_id=self.model_version_id,
            dataset_version_id=self.dataset_version_id,
            inference_device=f"{self.device_type} (PyTorch)"
        )

        return SpillDetectionResponse(
            incident_id=incident_id,
            tile_id=tile_id,
            sar_granule_id=sar_granule_id,
            status=overall_status,
            is_abstained=False,
            abstention_details=None,
            spill_mask=spill_mask,
            spill_geometry=spill_geometry,
            lookalike_verification=lookalike_res,
            severity=severity_res,
            data_quality=dqi_obj,
            provenance=provenance
        )
