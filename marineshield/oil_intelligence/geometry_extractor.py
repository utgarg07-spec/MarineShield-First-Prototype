import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class SpillGeometryExtractor:
    """Extracts canonical vector GeoJSON polygons and geometric properties from binary oil masks

    using pure NumPy connected-component analysis and boundary tracing.
    
    Conforms to §7 of OIL_INTELLIGENCE_CONTRACTS.md without third-party C++ dependencies.
    """
    def __init__(self, min_area_px: int = 50, pixel_resolution_m: float = 10.0):
        self.min_area_px = min_area_px
        self.pixel_resolution_m = pixel_resolution_m  # Sentinel-1 IW GRD ~10m/pixel

    def _extract_connected_components(self, bin_mask: np.ndarray) -> List[List[Tuple[int, int]]]:
        """Finds 8-connected components of foreground pixels (y, x)."""
        h, w = bin_mask.shape
        visited = np.zeros((h, w), dtype=bool)
        components = []

        # Find foreground coordinates
        y_indices, x_indices = np.where(bin_mask)
        foreground_set = set(zip(y_indices, x_indices))

        for start_node in foreground_set:
            if visited[start_node[0], start_node[1]]:
                continue

            # BFS for component
            comp = []
            queue = [start_node]
            visited[start_node[0], start_node[1]] = True

            while queue:
                cy, cx = queue.pop(0)
                comp.append((cy, cx))

                # Check 8 neighbors
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            if bin_mask[ny, nx] and not visited[ny, nx]:
                                visited[ny, nx] = True
                                queue.append((ny, nx))
            
            if len(comp) >= self.min_area_px:
                components.append(comp)

        return components

    def _extract_boundary_polygon(self, component: List[Tuple[int, int]], h: int, w: int) -> List[Tuple[int, int]]:
        """Extracts the outer boundary coordinates using 8-directional convex/concave hull boundary sampling."""
        comp_set = set(component)
        # Find border pixels: pixels with at least one 4-connected non-member neighbor
        border_pixels = []
        for y, x in component:
            is_border = False
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                if not (0 <= ny < h and 0 <= nx < w) or (ny, nx) not in comp_set:
                    is_border = True
                    break
            if is_border:
                border_pixels.append((y, x))

        if not border_pixels:
            return []

        # Sort border pixels radially around centroid to form a closed polygon
        cy = sum(p[0] for p in component) / len(component)
        cx = sum(p[1] for p in component) / len(component)

        def angle_from_centroid(pt: Tuple[int, int]) -> float:
            return math.atan2(pt[0] - cy, pt[1] - cx)

        # Group by angular bins to downsample to smooth polygon (e.g. 36 angular sectors = 10 deg each)
        num_bins = 36
        bins: Dict[int, Tuple[float, Tuple[int, int]]] = {}

        for y, x in border_pixels:
            ang = angle_from_centroid((y, x))
            bin_idx = int(((ang + math.pi) / (2.0 * math.pi)) * num_bins) % num_bins
            dist_sq = (y - cy) ** 2 + (x - cx) ** 2
            if bin_idx not in bins or dist_sq > bins[bin_idx][0]:
                bins[bin_idx] = (dist_sq, (y, x))

        sorted_bins = sorted(bins.keys())
        polygon_pts = [bins[b][1] for b in sorted_bins]
        
        # Ensure at least 3 vertices
        if len(polygon_pts) < 3:
            polygon_pts = border_pixels[:min(len(border_pixels), 20)]

        return polygon_pts

    def extract_geometry(
        self,
        prob_mask: np.ndarray,
        threshold: float = 0.50,
        tile_bounds: Optional[Tuple[float, float, float, float]] = None
    ) -> Optional[Dict[str, Any]]:
        """Extracts primary spill polygon GeoJSON and geometric metrics.

        
        :param prob_mask: 2D numpy array [512, 512] of float probabilities [0.0, 1.0]
        :param threshold: Binarization threshold
        :param tile_bounds: (lon_min, lat_min, lon_max, lat_max).
        :return: GeoJSON Feature dict with properties, or None if no valid contours found.
        """
        if tile_bounds is None:
            tile_bounds = (72.0, 18.0, 72.5, 18.5)
        lon_min, lat_min, lon_max, lat_max = tile_bounds

        bin_mask = prob_mask >= threshold
        if not np.any(bin_mask):
            return None

        components = self._extract_connected_components(bin_mask)
        if not components:
            return None

        # Select largest component
        components.sort(key=len, reverse=True)
        primary_comp = components[0]
        area_px = len(primary_comp)

        h, w = prob_mask.shape
        def px_to_geo(x: float, y: float) -> Tuple[float, float]:
            lon = lon_min + (x / float(w)) * (lon_max - lon_min)
            lat = lat_max - (y / float(h)) * (lat_max - lat_min)
            return (round(lon, 6), round(lat, 6))

        # Extract boundary points (y, x)
        boundary_px = self._extract_boundary_polygon(primary_comp, h, w)
        if len(boundary_px) < 3:
            return None

        # Convert to (lon, lat) GeoJSON coordinate list
        polygon_coords = []
        for y, x in boundary_px:
            gx, gy = px_to_geo(float(x), float(y))
            polygon_coords.append([gx, gy])

        # Ensure ring is closed
        if polygon_coords[0] != polygon_coords[-1]:
            polygon_coords.append(polygon_coords[0])

        # Centroid calculation
        cy_px = sum(p[0] for p in primary_comp) / float(area_px)
        cx_px = sum(p[1] for p in primary_comp) / float(area_px)
        centroid_lon, centroid_lat = px_to_geo(cx_px, cy_px)

        # Orientation and elongation via PCA / Covariance of (x, y) coordinates
        pts_y = np.array([p[0] for p in primary_comp], dtype=np.float32)
        pts_x = np.array([p[1] for p in primary_comp], dtype=np.float32)
        cov = np.cov(pts_x, pts_y)
        if cov.ndim == 2 and not np.isnan(cov).any():
            eigvals, eigvecs = np.linalg.eigh(cov)
            major_eigval = max(1e-4, eigvals[1])
            minor_eigval = max(1e-4, eigvals[0])
            elongation = round(float(math.sqrt(major_eigval / minor_eigval)), 2)
            # Angle of principal axis in degrees (0 - 180)
            principal_vec = eigvecs[:, 1]
            angle_rad = math.atan2(principal_vec[1], principal_vec[0])
            orientation = round(float(math.degrees(angle_rad) % 180.0), 1)
        else:
            elongation = 1.0
            orientation = 0.0

        # Perimeter estimation
        perimeter_px = len(boundary_px)
        for i in range(len(boundary_px)):
            p1 = boundary_px[i]
            p2 = boundary_px[(i + 1) % len(boundary_px)]
            perimeter_px += math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        perimeter_km = round((perimeter_px * self.pixel_resolution_m) / 1000.0, 4)

        # Area in km^2
        area_m2 = area_px * (self.pixel_resolution_m ** 2)
        area_km2 = round(area_m2 / 1_000_000.0, 4)

        # Fragmentation index
        total_valid_area = sum(len(c) for c in components)
        fragmentation_index = round(float(1.0 - (area_px / max(1.0, total_valid_area))), 3)

        # Bounding box
        lons = [p[0] for p in polygon_coords]
        lats = [p[1] for p in polygon_coords]
        bbox = {
            "lon_min": min(lons),
            "lat_min": min(lats),
            "lon_max": max(lons),
            "lat_max": max(lats)
        }

        # Mean probability within polygon
        comp_probs = [prob_mask[y, x] for y, x in primary_comp]
        mean_prob_inside = float(np.mean(comp_probs)) if comp_probs else float(threshold)

        geojson_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon_coords]
            },
            "properties": {
                "area_km2": area_km2,
                "perimeter_km": perimeter_km,
                "centroid_lon": centroid_lon,
                "centroid_lat": centroid_lat,
                "orientation_deg": orientation,
                "elongation_ratio": elongation,
                "fragmentation_index": fragmentation_index,
                "bounding_box": bbox,
                "pixel_count": int(area_px),
                "mean_oil_probability": round(mean_prob_inside, 4)
            }
        }
        return geojson_feature
