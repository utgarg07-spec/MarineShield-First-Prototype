"""
MarineShield Vessel Cache Manager
Provides deterministic JSON caching with cryptographic SHA-256 provenance tracking
for vessel lookup, AIS presence, and SAR presence queries.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class VesselCacheManager:
    """Manages local filesystem JSON cache with SHA-256 provenance verification."""

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            self.cache_dir = os.path.join(base_dir, "data", "vessel_cache")
        
        os.makedirs(self.cache_dir, exist_ok=True)

    @staticmethod
    def compute_hash(data_bytes: bytes) -> str:
        """Calculate SHA-256 hash digest of raw content bytes."""
        return hashlib.sha256(data_bytes).hexdigest()

    @staticmethod
    def generate_cache_key(prefix: str, params: Dict[str, Any]) -> str:
        """Generate a deterministic cache filename stem based on query parameters."""
        serialized = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
        clean_prefix = "".join([c if c.isalnum() else "_" for c in prefix]).lower()
        return f"{clean_prefix}_{param_hash}"

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached entry by key. Returns payload dictionary or None on miss."""
        file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        if not os.path.isfile(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                cached_obj = json.load(f)

            # Verify cryptographic SHA-256 integrity
            stored_digest = cached_obj.get("provenance", {}).get("sha256")
            payload = cached_obj.get("data")
            if stored_digest and payload is not None:
                payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
                computed_digest = self.compute_hash(payload_bytes)
                if computed_digest != stored_digest:
                    # Corruption detected; invalidate cache entry
                    return None

            return cached_obj
        except Exception:
            return None

    def set(
        self,
        cache_key: str,
        data: Any,
        query_params: Optional[Dict[str, Any]] = None,
        provider: str = "GLOBAL_FISHING_WATCH",
    ) -> str:
        """Save data entry with SHA-256 cryptographic provenance to cache directory."""
        file_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        payload_bytes = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        sha256_digest = self.compute_hash(payload_bytes)

        cache_record = {
            "cache_key": cache_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "query_params": query_params or {},
            "provenance": {
                "sha256": sha256_digest,
                "byte_size": len(payload_bytes),
                "format": "JSON",
            },
            "data": data,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cache_record, f, indent=2, default=str)

        return file_path

    def clear(self) -> int:
        """Clears all JSON files in the vessel cache directory."""
        count = 0
        if os.path.exists(self.cache_dir):
            for fname in os.listdir(self.cache_dir):
                if fname.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, fname))
                    count += 1
        return count
