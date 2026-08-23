"""
MarineShield Copernicus Authentication Manager
Manages OAuth2 token acquisition, caching, and open-catalog fallback for CDSE.
"""

import time
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any

from marineshield.config import settings

logger = logging.getLogger(__name__)

class CopernicusAuthManager:
    """
    Manages authentication for Copernicus Data Space Ecosystem (CDSE).
    Supports client credentials OAuth2 flow with token expiry tracking and
    transparent fallback to open-catalog mode when credentials are not configured.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        auth_url: Optional[str] = None
    ):
        self.client_id = client_id or settings.COPERNICUS_CLIENT_ID
        self.client_secret = client_secret or settings.COPERNICUS_CLIENT_SECRET
        self.auth_url = auth_url or settings.COPERNICUS_AUTH_URL
        
        self._access_token: Optional[str] = None
        self._token_expiry_epoch: float = 0.0

    @property
    def is_configured(self) -> bool:
        """Return True if credentials are provided."""
        return bool(self.client_id and self.client_secret)

    def get_token(self) -> Optional[str]:
        """
        Retrieve a valid OAuth2 access token. Returns cached token if still valid.
        Returns None if credentials are not configured (allowing open catalog queries).
        """
        if not self.is_configured:
            return None

        # Return cached token if valid (with 60s safety buffer)
        if self._access_token and time.time() < (self._token_expiry_epoch - 60):
            return self._access_token

        return self._fetch_new_token()

    def _fetch_new_token(self) -> Optional[str]:
        """Request a new token from Keycloak CDSE endpoint using client credentials."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            self.auth_url,
            data=encoded_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "MarineShield-Acquisition/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                token_resp = json.loads(resp.read().decode("utf-8"))
                self._access_token = token_resp.get("access_token")
                expires_in = token_resp.get("expires_in", 300)
                self._token_expiry_epoch = time.time() + float(expires_in)
                logger.info("Successfully acquired Copernicus CDSE access token.")
                return self._access_token
        except urllib.error.HTTPError as e:
            logger.warning(f"Copernicus OAuth2 authentication failed with HTTP {e.code}: {e.reason}")
            return None
        except Exception as e:
            logger.warning(f"Error connecting to Copernicus authentication endpoint: {e}")
            return None

    def get_auth_header(self) -> Dict[str, str]:
        """Return Authorization header if token is available, or empty dict for open access."""
        token = self.get_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
