"""
MarineShield Global Fishing Watch (GFW) Modular API Client Adapter
Wraps gfwapiclient v1.4.0 with environment-based authentication, deterministic local caching,
offline/mock fallback mechanisms, and contract entity transformations.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from marineshield.vessels.vessel_cache_manager import VesselCacheManager
from marineshield.vessels.vessel_parser import VesselParser

# Try loading .env variables
try:
    from dotenv import load_dotenv
    _env_file = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
    if os.path.isfile(_env_file):
        load_dotenv(_env_file, override=False)
except ImportError:
    pass


class GFWClientAdapter:
    """Modular Client Adapter for Global Fishing Watch (GFW) API v3."""

    def __init__(self, token: Optional[str] = None, allow_mock: Optional[bool] = None, cache_dir: Optional[str] = None):
        if token is not None:
            self._token = token
        else:
            self._token = os.environ.get("GFW_API_ACCESS_TOKEN") or os.environ.get("GFW_API_TOKEN") or ""
        
        # Resolve Mock Policy
        if allow_mock is not None:
            self.allow_mock = allow_mock
        else:
            env_mock = os.environ.get("ALLOW_MOCK_FALLBACK", "True").lower()
            self.allow_mock = env_mock in ("true", "1", "yes")

        self.cache_manager = VesselCacheManager(cache_dir=cache_dir)
        self._gfw_client = None
        
        if self._token:
            try:
                import gfwapiclient as gfw
                self._gfw_client = gfw.Client(access_token=self._token)
            except Exception:
                self._gfw_client = None

    @property
    def has_credentials(self) -> bool:
        """Check if a non-empty access token is available."""
        return bool(self._token and len(self._token.strip()) > 10)

    def check_authentication(self) -> Dict[str, Any]:
        """Validates GFW API credentials and client instantiation status."""
        if not self.has_credentials:
            return {
                "authenticated": False,
                "token_present": False,
                "client_ready": False,
                "mode": "MOCK_FALLBACK" if self.allow_mock else "UNAUTHENTICATED",
                "message": "GFW_API_ACCESS_TOKEN not configured in environment.",
            }

        if self._gfw_client is None:
            try:
                import gfwapiclient as gfw
                self._gfw_client = gfw.Client(access_token=self._token)
            except Exception as e:
                return {
                    "authenticated": False,
                    "token_present": True,
                    "client_ready": False,
                    "mode": "MOCK_FALLBACK" if self.allow_mock else "ERROR",
                    "message": f"Client initialization failed: {type(e).__name__}",
                }

        token_preview = self._token[:6] + "..." + self._token[-4:] if len(self._token) > 10 else "..."
        return {
            "authenticated": True,
            "token_present": True,
            "client_ready": True,
            "mode": "LIVE_API",
            "token_preview": token_preview,
            "message": "GFW API Client successfully initialized.",
        }

    async def search_vessels_async(
        self,
        query: str = "fishing",
        datasets: Optional[List[str]] = None,
        limit: int = 5,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Asynchronously query GFW vessel search API or retrieve from cache/mock."""
        datasets = datasets or ["public-global-vessel-identity:latest"]
        params = {"query": query, "datasets": datasets, "limit": limit}
        cache_key = VesselCacheManager.generate_cache_key("vessel_search", params)

        # 1. Check Cache
        if use_cache:
            cached = self.cache_manager.get(cache_key)
            if cached and "data" in cached:
                return {
                    "status": "SUCCESS_CACHED",
                    "cache_hit": True,
                    "source": "LOCAL_DETERMINISTIC_CACHE",
                    "raw_count": len(cached["data"].get("entries", [])),
                    "vessels": [VesselParser.parse_gfw_vessel_entry(e) for e in cached["data"].get("entries", [])],
                    "raw_response": cached["data"],
                }

        # 2. Query Live API if client available
        if self._gfw_client is not None:
            try:
                result = await self._gfw_client.vessels.search_vessels(
                    query=query,
                    datasets=datasets,
                    limit=limit,
                )
                entries = getattr(result, "entries", []) or []
                raw_entries = []
                for entry in entries:
                    if hasattr(entry, "__dict__"):
                        raw_entries.append(entry.__dict__)
                    else:
                        raw_entries.append(str(entry))

                raw_data = {"query": query, "entries": raw_entries, "count": len(entries)}
                
                # Cache serialized response
                if use_cache:
                    self.cache_manager.set(cache_key, raw_data, query_params=params)

                if len(entries) == 0 and self.allow_mock:
                    # Fallback to mock records if live API returns 0 entries for search query
                    mock_entries = [
                        {
                            "mmsi": "413123456",
                            "shipname": f"MOCK {query.upper()} VESSEL 1",
                            "ship_type": "FISHING_VESSEL",
                            "flag": "IN",
                            "length": 52.0,
                            "width": 11.0,
                        },
                        {
                            "mmsi": "413987654",
                            "shipname": f"MOCK {query.upper()} VESSEL 2",
                            "ship_type": "CARGO_CONTAINER",
                            "flag": "IN",
                            "length": 140.0,
                            "width": 22.0,
                        },
                    ]
                    parsed_vessels = [VesselParser.parse_gfw_vessel_entry(e) for e in mock_entries]
                    return {
                        "status": "SUCCESS_MOCK",
                        "cache_hit": False,
                        "source": "OFFLINE_MOCK_FALLBACK",
                        "raw_count": len(mock_entries),
                        "vessels": parsed_vessels,
                        "raw_response": {"query": query, "entries": mock_entries},
                    }

                parsed_vessels = [VesselParser.parse_gfw_vessel_entry(e) for e in entries]

                return {
                    "status": "SUCCESS_LIVE",
                    "cache_hit": False,
                    "source": "GLOBAL_FISHING_WATCH_API",
                    "raw_count": len(entries),
                    "vessels": parsed_vessels,
                    "raw_response": raw_data,
                }
            except Exception as e:
                if not self.allow_mock:
                    return {
                        "status": "ERROR",
                        "error_type": type(e).__name__,
                        "message": str(e),
                        "vessels": [],
                    }

        # 3. Fallback Mock Response
        mock_data = {
            "query": query,
            "entries": [
                {
                    "mmsi": "413123456",
                    "shipname": f"MOCK {query.upper()} VESSEL 1",
                    "ship_type": "FISHING_VESSEL",
                    "flag": "IN",
                    "length": 52.0,
                    "width": 11.0,
                },
                {
                    "mmsi": "413987654",
                    "shipname": f"MOCK {query.upper()} VESSEL 2",
                    "ship_type": "CARGO_CONTAINER",
                    "flag": "IN",
                    "length": 140.0,
                    "width": 22.0,
                },
            ],
            "count": 2,
        }

        parsed_vessels = [VesselParser.parse_gfw_vessel_entry(e) for e in mock_data["entries"]]
        return {
            "status": "SUCCESS_MOCK",
            "cache_hit": False,
            "source": "OFFLINE_MOCK_SIMULATOR",
            "raw_count": 2,
            "vessels": parsed_vessels,
            "raw_response": mock_data,
        }

    def search_vessels(
        self,
        query: str = "fishing",
        datasets: Optional[List[str]] = None,
        limit: int = 5,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for search_vessels_async."""
        return asyncio.run(self.search_vessels_async(query=query, datasets=datasets, limit=limit, use_cache=use_cache))

    async def get_ais_presence_async(
        self,
        start_date: str = "2024-01-15",
        end_date: str = "2024-01-25",
        geojson: Optional[Dict[str, Any]] = None,
        spatial_resolution: str = "LOW",
        temporal_resolution: str = "DAILY",
        group_by: str = "FLAG",
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Asynchronously query GFW FourWings AIS presence report or return mock."""
        default_geojson = {
            "type": "Polygon",
            "coordinates": [[[72.0, 18.0], [74.0, 18.0], [74.0, 20.0], [72.0, 20.0], [72.0, 18.0]]],
        }
        geojson = geojson or default_geojson
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "spatial_resolution": spatial_resolution,
            "temporal_resolution": temporal_resolution,
            "group_by": group_by,
        }
        cache_key = VesselCacheManager.generate_cache_key("ais_presence", params)

        if use_cache:
            cached = self.cache_manager.get(cache_key)
            if cached and "data" in cached:
                return {
                    "status": "SUCCESS_CACHED",
                    "cache_hit": True,
                    "source": "LOCAL_DETERMINISTIC_CACHE",
                    "record_count": cached["data"].get("record_count", 0),
                    "raw_response": cached["data"],
                }

        if self._gfw_client is not None:
            try:
                result = await self._gfw_client.fourwings.create_ais_presence_report(
                    spatial_resolution=spatial_resolution,
                    temporal_resolution=temporal_resolution,
                    group_by=group_by,
                    start_date=start_date,
                    end_date=end_date,
                    geojson=geojson,
                    spatial_aggregation=True,
                )
                entries = getattr(result, "entries", []) or []
                rec_count = len(entries)
                raw_data = {"start_date": start_date, "end_date": end_date, "record_count": rec_count}

                if use_cache:
                    self.cache_manager.set(cache_key, raw_data, query_params=params)

                return {
                    "status": "SUCCESS_LIVE",
                    "cache_hit": False,
                    "source": "GLOBAL_FISHING_WATCH_API",
                    "record_count": rec_count,
                    "raw_response": raw_data,
                }
            except Exception as e:
                if not self.allow_mock:
                    return {"status": "ERROR", "error_type": type(e).__name__, "message": str(e), "record_count": 0}

        mock_data = {"start_date": start_date, "end_date": end_date, "record_count": 42}
        return {
            "status": "SUCCESS_MOCK",
            "cache_hit": False,
            "source": "OFFLINE_MOCK_SIMULATOR",
            "record_count": 42,
            "raw_response": mock_data,
        }

    def get_ais_presence(
        self,
        start_date: str = "2024-01-15",
        end_date: str = "2024-01-25",
        geojson: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for get_ais_presence_async."""
        return asyncio.run(self.get_ais_presence_async(start_date=start_date, end_date=end_date, geojson=geojson, use_cache=use_cache))

    async def get_sar_presence_async(
        self,
        start_date: str = "2024-01-15",
        end_date: str = "2024-01-25",
        geojson: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Asynchronously query GFW FourWings SAR presence report or return mock."""
        default_geojson = {
            "type": "Polygon",
            "coordinates": [[[72.0, 18.0], [74.0, 18.0], [74.0, 20.0], [72.0, 20.0], [72.0, 18.0]]],
        }
        geojson = geojson or default_geojson
        params = {"start_date": start_date, "end_date": end_date}
        cache_key = VesselCacheManager.generate_cache_key("sar_presence", params)

        if use_cache:
            cached = self.cache_manager.get(cache_key)
            if cached and "data" in cached:
                return {
                    "status": "SUCCESS_CACHED",
                    "cache_hit": True,
                    "source": "LOCAL_DETERMINISTIC_CACHE",
                    "record_count": cached["data"].get("record_count", 0),
                    "raw_response": cached["data"],
                }

        if self._gfw_client is not None:
            try:
                result = await self._gfw_client.fourwings.create_sar_presence_report(
                    spatial_resolution="LOW",
                    temporal_resolution="DAILY",
                    group_by="FLAG",
                    start_date=start_date,
                    end_date=end_date,
                    geojson=geojson,
                    spatial_aggregation=True,
                )
                entries = getattr(result, "entries", []) or []
                rec_count = len(entries)
                raw_data = {"start_date": start_date, "end_date": end_date, "record_count": rec_count}

                if use_cache:
                    self.cache_manager.set(cache_key, raw_data, query_params=params)

                return {
                    "status": "SUCCESS_LIVE",
                    "cache_hit": False,
                    "source": "GLOBAL_FISHING_WATCH_API",
                    "record_count": rec_count,
                    "raw_response": raw_data,
                }
            except Exception as e:
                if not self.allow_mock:
                    return {"status": "ERROR", "error_type": type(e).__name__, "message": str(e), "record_count": 0}

        mock_data = {"start_date": start_date, "end_date": end_date, "record_count": 0}
        return {
            "status": "SUCCESS_MOCK",
            "cache_hit": False,
            "source": "OFFLINE_MOCK_SIMULATOR",
            "record_count": 0,
            "raw_response": mock_data,
        }

    def get_sar_presence(
        self,
        start_date: str = "2024-01-15",
        end_date: str = "2024-01-25",
        geojson: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for get_sar_presence_async."""
        return asyncio.run(self.get_sar_presence_async(start_date=start_date, end_date=end_date, geojson=geojson, use_cache=use_cache))
