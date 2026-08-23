"""
MarineShield Vessel Domain Package
Provides modular access to Global Fishing Watch (GFW) API, deterministic caching,
response parsing, and data contract entity transformation.
"""

from marineshield.vessels.vessel_parser import VesselParser
from marineshield.vessels.vessel_cache_manager import VesselCacheManager
from marineshield.vessels.gfw_client import GFWClientAdapter
from marineshield.vessels.intelligence_service import VesselIntelligenceService

__all__ = [
    "VesselParser",
    "VesselCacheManager",
    "GFWClientAdapter",
    "VesselIntelligenceService",
]
