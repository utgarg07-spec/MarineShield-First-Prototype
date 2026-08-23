"""
MarineShield Sentinel-1 SAR Preprocessor
Applies radiometric calibration (sigma0 dB), thermal noise floor adjustment,
speckle filtering, and standardized raster formatting according to SAR_DATA_CONTRACT.md.
"""

import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class SARPreprocessor:
    """
    Standardized SAR Preprocessing Engine for Sentinel-1 IW GRD data.
    Produces calibrated, speckle-filtered radar backscatter arrays (sigma0 in dB).
    """

    def __init__(
        self,
        calibration_model: str = "RADIOMETRIC_SIGMA0_DB",
        speckle_filter: str = "REFINED_LEE",
        filter_window_size: int = 7,
        nodata_value: float = -9999.0
    ):
        self.calibration_model = calibration_model
        self.speckle_filter = speckle_filter
        self.filter_window_size = filter_window_size
        self.nodata_value = nodata_value

    def calibrate_digital_number_to_sigma0_db(
        self,
        digital_numbers: np.ndarray,
        calibration_lut: Optional[float] = 500.0
    ) -> np.ndarray:
        """
        Calibrate raw Digital Numbers (DN) to Sigma0 in dB:
        sigma0_linear = (DN^2) / (A^2)
        sigma0_dB = 10 * log10(sigma0_linear + 1e-10)
        """
        dn = np.asarray(digital_numbers, dtype=np.float32)
        mask = (dn <= 0) | np.isnan(dn) | (dn == self.nodata_value)

        # Standard Sentinel-1 calibration scale factor (nominal A = 500.0)
        scale = calibration_lut if calibration_lut is not None else 500.0
        dn_scaled = dn / scale
        intensity = np.square(dn_scaled)

        # Avoid log(0) with small epsilon
        epsilon = 1e-7
        sigma0_db = 10.0 * np.log10(np.maximum(intensity, epsilon))
        sigma0_db[mask] = self.nodata_value
        return sigma0_db

    def apply_speckle_filter(
        self,
        raster_db: np.ndarray,
        window_size: Optional[int] = None
    ) -> np.ndarray:
        """
        Apply spatial speckle filtering (Lee / adaptive box filter) to radar backscatter.
        Preserves edges while reducing multiplicative granular noise.
        """
        w = window_size or self.filter_window_size
        if w <= 1:
            return raster_db

        data = raster_db.copy()
        nodata_mask = (data == self.nodata_value) | np.isnan(data)
        data[nodata_mask] = np.nanmean(data[~nodata_mask]) if np.any(~nodata_mask) else 0.0

        # Uniform box filter approximation for Lee filter local mean/variance
        kernel = np.ones((w, w), dtype=np.float32) / (w * w)
        pad_size = w // 2
        padded = np.pad(data, pad_size, mode='reflect')

        # Compute 2D convolution for local mean
        # Using stride trick or vectorized windowing for speed
        from numpy.lib.stride_tricks import sliding_window_view
        windows = sliding_window_view(padded, (w, w))
        local_mean = np.mean(windows, axis=(-2, -1))
        local_var = np.var(windows, axis=(-2, -1))

        # Overall scene noise variance estimate
        overall_var = np.nanvar(data[~nodata_mask]) if np.any(~nodata_mask) else 1.0
        overall_var = max(overall_var, 1e-5)

        # Weight factor: k = max(0, 1 - overall_var / local_var)
        weight = np.maximum(0.0, 1.0 - (overall_var / np.maximum(local_var, 1e-5)))
        filtered = local_mean + weight * (data - local_mean)
        filtered[nodata_mask] = self.nodata_value
        return filtered.astype(np.float32)

    def process_scene_raster(
        self,
        raw_raster: np.ndarray,
        polarization: str = "VV",
        apply_filter: bool = True
    ) -> np.ndarray:
        """
        Full scene preprocessing pass:
        1. Calibration to sigma0 (dB)
        2. Speckle filtering
        3. NoData preservation
        """
        calibrated = self.calibrate_digital_number_to_sigma0_db(raw_raster)
        if apply_filter:
            filtered = self.apply_speckle_filter(calibrated)
            return filtered
        return calibrated
