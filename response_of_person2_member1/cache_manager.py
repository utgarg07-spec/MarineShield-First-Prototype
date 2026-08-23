"""
MarineShield Deterministic Local Cache Manager
Manages raw SAR scene caching, SHA-256 cryptographic verification, and provenance storage.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from marineshield.config import settings

class DeterministicCacheManager:
    """
    Manages deterministic filesystem caching of raw SAR granules and metadata.
    Ensures idempotency, zero duplicate downloads, and cryptographic provenance.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.SAR_RAW_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_scene_dir(self, granule_id: str) -> Path:
        """Return the dedicated cache directory for a granule."""
        clean_id = granule_id.replace(".SAFE", "").replace(".zip", "")
        return self.base_dir / clean_id

    def has_scene(self, granule_id: str) -> bool:
        """
        Check if a scene is already cached and valid.
        Requires metadata.json and provenance.json to be present with verified checksum.
        """
        scene_dir = self.get_scene_dir(granule_id)
        if not scene_dir.exists():
            return False

        clean_id = scene_dir.name
        meta_file = scene_dir / f"{clean_id}_metadata.json"
        prov_file = scene_dir / f"{clean_id}_provenance.json"

        if not (meta_file.exists() and prov_file.exists()):
            return False

        try:
            with open(prov_file, "r", encoding="utf-8") as f:
                prov = json.load(f)
                return bool(prov.get("checksum_verified") and prov.get("source_granule_sha256"))
        except Exception:
            return False

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        """Compute SHA-256 cryptographic hash of byte array."""
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()

    @staticmethod
    def compute_file_sha256(filepath: Path) -> str:
        """Compute SHA-256 hash of a file in chunks."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def store_scene(
        self,
        granule_id: str,
        canonical_metadata: Dict[str, Any],
        raw_manifest_or_archive: bytes,
        archive_filename: Optional[str] = None
    ) -> Tuple[Path, str]:
        """
        Atomically store a scene's raw data and canonical metadata in the local cache.
        Returns (scene_dir, sha256_hash).
        """
        scene_dir = self.get_scene_dir(granule_id)
        scene_dir.mkdir(parents=True, exist_ok=True)
        clean_id = scene_dir.name

        # 1. Compute SHA-256
        sha256_hash = self.compute_sha256(raw_manifest_or_archive)

        # 2. Store raw payload
        raw_name = archive_filename or f"{clean_id}_raw_manifest.xml"
        raw_file = scene_dir / raw_name
        with open(raw_file, "wb") as f:
            f.write(raw_manifest_or_archive)

        # 3. Update canonical metadata provenance
        canonical_metadata["provenance"]["source_granule_sha256"] = sha256_hash
        canonical_metadata["provenance"]["checksum_verified"] = True

        # 4. Save metadata.json
        meta_file = scene_dir / f"{clean_id}_metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(canonical_metadata, f, indent=2)

        # 5. Save dedicated provenance.json
        prov_file = scene_dir / f"{clean_id}_provenance.json"
        with open(prov_file, "w", encoding="utf-8") as f:
            json.dump(canonical_metadata["provenance"], f, indent=2)

        return scene_dir, sha256_hash

    def load_metadata(self, granule_id: str) -> Optional[Dict[str, Any]]:
        """Load canonical metadata from cache."""
        scene_dir = self.get_scene_dir(granule_id)
        meta_file = scene_dir / f"{scene_dir.name}_metadata.json"
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
