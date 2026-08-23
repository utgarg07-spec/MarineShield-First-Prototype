"""
MarineShield Sentinel-1 SAR Acquisition Pipeline
Coordinates search, sample acquisition, metadata parsing, provenance tracking, and local caching.
"""

import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from marineshield.config import settings
from marineshield.acquisition.copernicus_auth import CopernicusAuthManager
from marineshield.acquisition.copernicus_client import CopernicusClient
from marineshield.acquisition.metadata_parser import SARMetadataParser
from marineshield.acquisition.cache_manager import DeterministicCacheManager

logger = logging.getLogger(__name__)

class Sentinel1AcquisitionPipeline:
    """End-to-end coordinator for Sentinel-1 scene search and ingestion."""

    def __init__(
        self,
        auth_manager: Optional[CopernicusAuthManager] = None,
        client: Optional[CopernicusClient] = None,
        cache_manager: Optional[DeterministicCacheManager] = None,
        worker_id: str = "acquisition-worker-01"
    ):
        self.auth = auth_manager or CopernicusAuthManager()
        self.client = client or CopernicusClient(auth_manager=self.auth)
        self.cache = cache_manager or DeterministicCacheManager()
        self.worker_id = worker_id

    def search_scenes(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        product_type: str = "GRD",
        mission: str = "SENTINEL-1",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search Sentinel-1 scenes matching criteria."""
        return self.client.search_scenes(
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            product_type=product_type,
            mission=mission,
            max_results=max_results
        )

    def ingest_single_scene(
        self,
        product_dict: Dict[str, Any],
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest a single real Sentinel-1 scene:
        1. Check deterministic local cache.
        2. Download raw sample payload.
        3. Parse metadata into canonical SAR Data Contract v1.0.0.
        4. Compute cryptographic SHA-256 hash and store provenance.
        5. Save atomically to local cache.
        """
        start_time = time.time()
        product_id = product_dict["Id"]
        name = product_dict.get("Name", "")
        clean_id = name.replace(".SAFE", "").replace(".zip", "")

        # 1. Deterministic Cache Check
        if not force and self.cache.has_scene(clean_id):
            cached_meta = self.cache.load_metadata(clean_id)
            if cached_meta:
                logger.info(f"Scene '{clean_id}' already present in deterministic cache. Cache HIT.")
                return {
                    "granule_id": clean_id,
                    "status": "CACHE_HIT",
                    "cache_dir": str(self.cache.get_scene_dir(clean_id)),
                    "sha256": cached_meta["provenance"]["source_granule_sha256"],
                    "canonical_metadata": cached_meta,
                    "duration_seconds": 0.0
                }

        # 2. Download sample raw payload
        logger.info(f"Downloading raw sample payload for '{clean_id}' (ID: {product_id})...")
        raw_bytes = self.client.download_product_bytes(product_id)
        sha256_hash = DeterministicCacheManager.compute_sha256(raw_bytes)
        duration_s = time.time() - start_time

        # 3. Parse Metadata into Canonical Contract
        canonical_metadata = SARMetadataParser.parse_cdse_product(
            cdse_product=product_dict,
            sha256_hash=sha256_hash,
            worker_id=self.worker_id,
            duration_seconds=duration_s,
            raw_cache_path=str(self.cache.get_scene_dir(clean_id))
        )

        # 4. Store in Deterministic Cache with Provenance
        scene_dir, verified_hash = self.cache.store_scene(
            granule_id=clean_id,
            canonical_metadata=canonical_metadata,
            raw_manifest_or_archive=raw_bytes,
            archive_filename=f"{clean_id}_manifest.xml"
        )

        logger.info(f"Successfully ingested and cached scene '{clean_id}' to {scene_dir}.")

        return {
            "granule_id": clean_id,
            "status": "SUCCESS_INGESTED",
            "cache_dir": str(scene_dir),
            "sha256": verified_hash,
            "canonical_metadata": canonical_metadata,
            "duration_seconds": round(duration_s, 2)
        }

    def search_and_acquire_sample(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        product_type: str = "GRD",
        mission: str = "SENTINEL-1",
        force: bool = False
    ) -> Dict[str, Any]:
        """Search and acquire the top matching real Sentinel-1 scene."""
        scenes = self.search_scenes(
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            product_type=product_type,
            mission=mission,
            max_results=5
        )

        if not scenes:
            raise RuntimeError(f"No Sentinel-1 {product_type} scenes found matching bounding box {bbox} in date range {start_date} - {end_date}.")

        top_scene = scenes[0]
        return self.ingest_single_scene(top_scene, force=force)
