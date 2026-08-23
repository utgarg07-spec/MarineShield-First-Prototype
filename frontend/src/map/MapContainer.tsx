import React, { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { Incident } from '../api/types/incident';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData, AISObservation, SARVesselDetection, VesselMatch, UnmatchedVessel, AnomalyEvent } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';
import type { SpillDetectionResponse } from '../api/types/oil_intelligence';
import type { InvestigationResult } from '../api/types/investigation';
import { api } from '../api';
import { mockVesselMetadataMap } from '../mocks/fixtures/vessels';
import type { MapTarget } from '../context/AppContext';

interface MapContainerProps {
  onSarSelect?: (sar: SARSceneMetadata | null) => void;
  onVesselSelect?: (vessel: SelectedVesselData | null) => void;
  onForecastSelect?: (forecast: Forecast | null) => void;
  onThreatSelect?: (threat: ThreatAssessment | null) => void;
  selectedSar?: SARSceneMetadata | null;
  selectedVessel?: SelectedVesselData | null;
  selectedForecast?: Forecast | null;
  selectedThreat?: ThreatAssessment | null;
  mapTarget?: MapTarget | null;
  className?: string;
  incident?: Incident | null;
  spillDetection?: SpillDetectionResponse | null;
  investigationResult?: InvestigationResult | null;
}

export const isValidEPSG4326GeoJSON = (geom: any): boolean => {
  if (!geom || typeof geom !== 'object') return false;
  if (!geom.type || !geom.coordinates || !Array.isArray(geom.coordinates)) return false;
  
  try {
    let sample: any = geom.coordinates;
    while (Array.isArray(sample[0])) {
      sample = sample[0];
    }
    if (typeof sample[0] === 'number' && typeof sample[1] === 'number') {
      const lon = sample[0];
      const lat = sample[1];
      if (lon < -180 || lon > 180 || lat < -90 || lat > 90) return false;
    }
  } catch {
    return false;
  }
  return true;
};

export const MapContainer: React.FC<MapContainerProps> = ({
  className = '',
  incident,
  spillDetection,
  investigationResult,
  selectedSar,
  selectedVessel,
  selectedForecast,
  selectedThreat,
  onSarSelect,
  onVesselSelect,
  onForecastSelect,
  onThreatSelect,
  mapTarget,
}) => {
  const [sarScenes, setSarScenes] = useState<SARSceneMetadata[]>([]);
  const [sarVisible, setSarVisible] = useState<boolean>(false);

  const [vesselsVisible, setVesselsVisible] = useState<boolean>(false);
  const [aisObservations, setAisObservations] = useState<AISObservation[]>([]);
  const [sarDetections, setSarDetections] = useState<SARVesselDetection[]>([]);
  const [vesselMatches, setVesselMatches] = useState<VesselMatch[]>([]);
  const [unmatchedVessels, setUnmatchedVessels] = useState<UnmatchedVessel[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyEvent[]>([]);

  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [forecastVisible, setForecastVisible] = useState<boolean>(false);

  const [threatAssessment, setThreatAssessment] = useState<ThreatAssessment | null>(null);
  const [threatVisible, setThreatVisible] = useState<boolean>(false);

  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSarSelectRef = useRef(onSarSelect);
  useEffect(() => { onSarSelectRef.current = onSarSelect; }, [onSarSelect]);

  const onVesselSelectRef = useRef(onVesselSelect);
  useEffect(() => { onVesselSelectRef.current = onVesselSelect; }, [onVesselSelect]);

  const onForecastSelectRef = useRef(onForecastSelect);
  useEffect(() => { onForecastSelectRef.current = onForecastSelect; }, [onForecastSelect]);

  const onThreatSelectRef = useRef(onThreatSelect);
  useEffect(() => { onThreatSelectRef.current = onThreatSelect; }, [onThreatSelect]);

  // Sync selected props to local visibility & state
  useEffect(() => {
    if (selectedForecast) {
      setForecast(selectedForecast);
      setForecastVisible(true);
    }
  }, [selectedForecast]);

  useEffect(() => {
    if (selectedVessel) setVesselsVisible(true);
  }, [selectedVessel]);

  useEffect(() => {
    if (selectedThreat) setThreatVisible(true);
  }, [selectedThreat]);

  useEffect(() => {
    if (selectedSar) setSarVisible(true);
  }, [selectedSar]);

  // Map Initialization
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    try {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: import.meta.env.VITE_MAP_STYLE_URL || '/map-style.json',
        center: [73.3, 18.3],
        zoom: 6.5,
        attributionControl: false,
      });

      map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
      map.current.addControl(
        new maplibregl.AttributionControl({
          compact: true,
          customAttribution: 'MarineShield | &copy; CARTO',
        }),
        'bottom-right'
      );

      // Background click handler: clear selection if clicked outside interactive layers
      map.current.on('click', (e) => {
        const features = map.current?.queryRenderedFeatures(e.point);
        const hitInteractive = features?.some((f) =>
          f.layer.id.includes('vessels') ||
          f.layer.id.includes('sar-fill') ||
          f.layer.id.includes('person1-spill') ||
          f.layer.id.includes('person1-release') ||
          f.layer.id.includes('forecast-trajectory') ||
          f.layer.id.includes('forecast-timesteps') ||
          f.layer.id.includes('forecast-selected-timestep') ||
          f.layer.id.includes('threat-assets') ||
          f.layer.id.includes('threat-intersections')
        );
        if (!hitInteractive) {
          onSarSelectRef.current?.(null);
          onVesselSelectRef.current?.(null);
          onForecastSelectRef.current?.(null);
          onThreatSelectRef.current?.(null);
        }
      });

      map.current.on('error', (e: any) => {
        console.error('Map error:', e);
        setError('Failed to load map resources.');
      });
    } catch (err) {
      console.error('Failed to initialize map:', err);
      setError('Failed to initialize the map.');
    }

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Fetch telemetry fixtures when incident changes
  useEffect(() => {
    const incId = incident?.id || 'MS-PHASE6-DEV-001';

    api.getSARScenes(incId)
      .then((res) => setSarScenes(res.data))
      .catch((e) => console.error('Failed to load SAR scenes', e));

    api.getForecast(incId, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then((res) => setForecast(res.data))
      .catch((e) => console.error('Failed to load forecast data', e));

    api.getThreatAssessment(incId, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then((res) => setThreatAssessment(res.data))
      .catch((e) => console.error('Failed to load threat assessment data', e));

    Promise.all([
      api.getVessels(incId),
      api.getSARDetections(incId),
      api.getVesselMatches(incId),
      api.getUnmatchedVessels(incId),
      api.getAnomalies(incId),
    ])
      .then(([vesselsRes, sarDetRes, matchesRes, unmatchedRes, anomaliesRes]) => {
        setAisObservations(vesselsRes.data);
        setSarDetections(sarDetRes.data);
        setVesselMatches(matchesRes.data);
        setUnmatchedVessels(unmatchedRes.data);
        setAnomalies(anomaliesRes.data);
      })
      .catch((e) => console.error('Failed to load vessel data', e));
  }, [incident?.id]);

  // 1. SAR Footprint WebGIS Registry
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;

    const updateSarFootprintLayers = () => {
      if (!m.isStyleLoaded()) return;

      const hasScene = sarScenes.length > 0;
      const scene = hasScene ? sarScenes[0] : null;
      const geojson = scene?.spatial_reference?.footprint_geojson;

      if (geojson && isValidEPSG4326GeoJSON(geojson)) {
        if (!m.getSource('sar-footprint')) {
          m.addSource('sar-footprint', {
            type: 'geojson',
            data: geojson as any,
          });

          m.addLayer({
            id: 'sar-fill-layer',
            type: 'fill',
            source: 'sar-footprint',
            paint: {
              'fill-color': 'rgba(6, 182, 212, 0.25)',
              'fill-outline-color': '#06b6d4',
            },
          });

          m.addLayer({
            id: 'sar-outline-layer',
            type: 'line',
            source: 'sar-footprint',
            paint: {
              'line-color': '#06b6d4',
              'line-width': 2.5,
              'line-dasharray': [4, 2],
            },
          });

          m.on('click', 'sar-fill-layer', (e) => {
            if (scene) {
              onSarSelectRef.current?.(scene);
            }
            if (e.lngLat) {
              m.flyTo({ center: e.lngLat, zoom: 8, essential: true });
            }
          });

          m.on('mouseenter', 'sar-fill-layer', () => { m.getCanvas().style.cursor = 'pointer'; });
          m.on('mouseleave', 'sar-fill-layer', () => { m.getCanvas().style.cursor = ''; });
        } else {
          (m.getSource('sar-footprint') as maplibregl.GeoJSONSource).setData(geojson as any);
        }

        const visibility = sarVisible ? 'visible' : 'none';
        if (m.getLayer('sar-fill-layer')) m.setLayoutProperty('sar-fill-layer', 'visibility', visibility);
        if (m.getLayer('sar-outline-layer')) m.setLayoutProperty('sar-outline-layer', 'visibility', visibility);
      }
    };

    if (m.isStyleLoaded()) updateSarFootprintLayers();
    else m.once('load', updateSarFootprintLayers);
  }, [sarVisible, sarScenes]);

  // 2A. Person 1 Canonical Spill Detection Layer
  useEffect(() => {
    const m = map.current;
    if (!m) return;
    const geom = (spillDetection?.spill_geometry as any)?.geometry_geojson || (spillDetection?.spill_geometry as any)?.geometry || spillDetection?.spill_geometry;
    const sourceId = 'person1-spill-detection';
    const fillLayerId = `${sourceId}-fill`;
    const lineLayerId = `${sourceId}-line`;

    if (!isValidEPSG4326GeoJSON(geom)) {
      if (m.getSource(sourceId)) {
        if (m.getLayer(fillLayerId)) m.removeLayer(fillLayerId);
        if (m.getLayer(lineLayerId)) m.removeLayer(lineLayerId);
        m.removeSource(sourceId);
      }
      return;
    }

    const geojson: any = {
      type: 'Feature',
      geometry: geom,
      properties: {
        status: spillDetection?.status,
        severity: spillDetection?.severity?.severity_class,
      },
    };

    if (m.getSource(sourceId)) {
      (m.getSource(sourceId) as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      m.addSource(sourceId, { type: 'geojson', data: geojson });
      m.addLayer({
        id: fillLayerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': '#f472b6',
          'fill-opacity': 0.35,
        },
      });
      m.addLayer({
        id: lineLayerId,
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': '#ec4899',
          'line-width': 2.5,
        },
      });

      m.on('click', fillLayerId, (e) => {
        if (sarScenes.length > 0) {
          onSarSelectRef.current?.(sarScenes[0]);
        }
        if (e.lngLat) {
          m.flyTo({ center: e.lngLat, zoom: 8, essential: true });
        }
      });
      m.on('mouseenter', fillLayerId, () => { m.getCanvas().style.cursor = 'pointer'; });
      m.on('mouseleave', fillLayerId, () => { m.getCanvas().style.cursor = ''; });
    }

    const visibility = sarVisible ? 'visible' : 'none';
    if (m.getLayer(fillLayerId)) m.setLayoutProperty(fillLayerId, 'visibility', visibility);
    if (m.getLayer(lineLayerId)) m.setLayoutProperty(lineLayerId, 'visibility', visibility);
  }, [spillDetection, sarScenes, sarVisible]);

  // 2B. Person 1 Canonical Release Reconstruction Region Polygon
  useEffect(() => {
    const m = map.current;
    if (!m) return;
    const geom = investigationResult?.release_reconstruction?.reconstruction_polygon_geojson;
    const sourceId = 'person1-release-reconstruction';
    const fillLayerId = `${sourceId}-fill`;
    const lineLayerId = `${sourceId}-line`;

    if (!isValidEPSG4326GeoJSON(geom)) {
      if (m.getSource(sourceId)) {
        if (m.getLayer(fillLayerId)) m.removeLayer(fillLayerId);
        if (m.getLayer(lineLayerId)) m.removeLayer(lineLayerId);
        m.removeSource(sourceId);
      }
      return;
    }

    const geojson: any = {
      type: 'Feature',
      geometry: geom,
      properties: {
        status: investigationResult?.release_reconstruction?.release_region_status,
      },
    };

    if (m.getSource(sourceId)) {
      (m.getSource(sourceId) as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      m.addSource(sourceId, { type: 'geojson', data: geojson });
      m.addLayer({
        id: fillLayerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': '#3b82f6',
          'fill-opacity': 0.25,
        },
      });
      m.addLayer({
        id: lineLayerId,
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': '#1d4ed8',
          'line-width': 2,
          'line-dasharray': [2, 2],
        },
      });

      m.on('click', fillLayerId, (e) => {
        const fc = selectedForecast || forecast;
        if (fc) {
          onForecastSelectRef.current?.(fc);
        }
        if (e.lngLat) {
          m.flyTo({ center: e.lngLat, zoom: 8, essential: true });
        }
      });
      m.on('mouseenter', fillLayerId, () => { m.getCanvas().style.cursor = 'pointer'; });
      m.on('mouseleave', fillLayerId, () => { m.getCanvas().style.cursor = ''; });
    }

    const visibility = forecastVisible ? 'visible' : 'none';
    if (m.getLayer(fillLayerId)) m.setLayoutProperty(fillLayerId, 'visibility', visibility);
    if (m.getLayer(lineLayerId)) m.setLayoutProperty(lineLayerId, 'visibility', visibility);
  }, [investigationResult, forecast, selectedForecast, forecastVisible]);

  // 3. Forecast WebGIS Registry
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;

    const updateForecastLayers = () => {
      if (!m.isStyleLoaded()) return;

      const activeForecast = selectedForecast || forecast;
      const hasTrajectory = activeForecast && (activeForecast.status === 'succeeded' || activeForecast.status === 'partial') && activeForecast.trajectory?.features?.length;

      if (hasTrajectory && activeForecast?.trajectory) {
        // 3A. Trajectory LineStrings
        if (!m.getSource('forecast-trajectory-source')) {
          m.addSource('forecast-trajectory-source', {
            type: 'geojson',
            data: activeForecast.trajectory as any,
          });

          m.addLayer({
            id: 'forecast-trajectory-layer',
            type: 'line',
            source: 'forecast-trajectory-source',
            paint: {
              'line-color': '#3b82f6',
              'line-width': 3.5,
              'line-opacity': 0.85,
            },
          });

          m.on('click', 'forecast-trajectory-layer', (e) => {
            if (activeForecast) onForecastSelectRef.current?.(activeForecast);
            if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8, essential: true });
          });

          m.on('mouseenter', 'forecast-trajectory-layer', () => { m.getCanvas().style.cursor = 'pointer'; });
          m.on('mouseleave', 'forecast-trajectory-layer', () => { m.getCanvas().style.cursor = ''; });
        } else {
          (m.getSource('forecast-trajectory-source') as maplibregl.GeoJSONSource).setData(activeForecast.trajectory as any);
        }

        // 3B. Timestep Point Markers & Labels (+6h, +12h, +24h, +48h)
        if (activeForecast.timesteps && activeForecast.timesteps.length > 0) {
          const timestepFeatures = activeForecast.timesteps.map((ts) => ({
            type: 'Feature',
            id: ts.horizon_hours,
            geometry: ts.position,
            properties: {
              horizon_hours: ts.horizon_hours,
              label: `+${ts.horizon_hours}h`,
              valid_time: ts.valid_time,
            },
          }));

          const timestepsGeoJson = { type: 'FeatureCollection', features: timestepFeatures };

          if (!m.getSource('forecast-timesteps-source')) {
            m.addSource('forecast-timesteps-source', { type: 'geojson', data: timestepsGeoJson as any });

            m.addLayer({
              id: 'forecast-timesteps-layer',
              type: 'circle',
              source: 'forecast-timesteps-source',
              paint: {
                'circle-color': '#60a5fa',
                'circle-radius': 8,
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff',
              },
            });

            m.addLayer({
              id: 'forecast-timesteps-label-layer',
              type: 'symbol',
              source: 'forecast-timesteps-source',
              layout: {
                'text-field': ['get', 'label'],
                'text-size': 11,
                'text-offset': [0, -1.5],
                'text-anchor': 'bottom',
              },
              paint: {
                'text-color': '#93c5fd',
                'text-halo-color': '#0f172a',
                'text-halo-width': 1.5,
              },
            });

            const handleTimestepSelect = (e: any) => {
              const feat = e.features?.[0];
              const hVal = feat?.properties?.horizon_hours ?? feat?.id;
              const hNum = Number(hVal);
              const targetFc = selectedForecast || forecast;
              if (targetFc && targetFc.timesteps) {
                const matchedTs = targetFc.timesteps.find((ts) => Number(ts.horizon_hours) === hNum);
                if (matchedTs) {
                  const enrichedForecast = {
                    ...targetFc,
                    activeTimestep: matchedTs,
                  };
                  onForecastSelectRef.current?.(enrichedForecast);
                }
              }
              if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8.5, essential: true });
            };

            m.on('click', 'forecast-timesteps-layer', handleTimestepSelect);
            m.on('click', 'forecast-timesteps-label-layer', handleTimestepSelect);

            m.on('mouseenter', 'forecast-timesteps-layer', () => { m.getCanvas().style.cursor = 'pointer'; });
            m.on('mouseleave', 'forecast-timesteps-layer', () => { m.getCanvas().style.cursor = ''; });
            m.on('mouseenter', 'forecast-timesteps-label-layer', () => { m.getCanvas().style.cursor = 'pointer'; });
            m.on('mouseleave', 'forecast-timesteps-label-layer', () => { m.getCanvas().style.cursor = ''; });
          } else {
            (m.getSource('forecast-timesteps-source') as maplibregl.GeoJSONSource).setData(timestepsGeoJson as any);
          }
        }

        // 3C. Uncertainty Polygons
        const uncertaintyFeatures: any[] = [];
        if (activeForecast.uncertainty?.regions) {
          activeForecast.uncertainty.regions.forEach((reg) => {
            if (reg.geometry && reg.valid) {
              uncertaintyFeatures.push({
                type: 'Feature',
                geometry: reg.geometry,
                properties: { horizon_hours: reg.horizon_hours, particle_fraction: reg.particle_fraction },
              });
            }
          });
        }

        if (uncertaintyFeatures.length > 0) {
          const uncertaintyGeoJson = { type: 'FeatureCollection', features: uncertaintyFeatures };

          if (!m.getSource('forecast-uncertainty-source')) {
            m.addSource('forecast-uncertainty-source', { type: 'geojson', data: uncertaintyGeoJson as any });

            m.addLayer({
              id: 'forecast-uncertainty-fill',
              type: 'fill',
              source: 'forecast-uncertainty-source',
              paint: { 'fill-color': 'rgba(59, 130, 246, 0.18)', 'fill-outline-color': '#3b82f6' },
            });

            m.addLayer({
              id: 'forecast-uncertainty-outline',
              type: 'line',
              source: 'forecast-uncertainty-source',
              paint: { 'line-color': '#3b82f6', 'line-width': 1.5, 'line-dasharray': [3, 2] },
            });
          } else {
            (m.getSource('forecast-uncertainty-source') as maplibregl.GeoJSONSource).setData(uncertaintyGeoJson as any);
          }
        }

        const vis = forecastVisible ? 'visible' : 'none';
        ['forecast-trajectory-layer', 'forecast-timesteps-layer', 'forecast-timesteps-label-layer', 'forecast-uncertainty-fill', 'forecast-uncertainty-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', vis);
        });
      } else {
        ['forecast-trajectory-layer', 'forecast-timesteps-layer', 'forecast-timesteps-label-layer', 'forecast-uncertainty-fill', 'forecast-uncertainty-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', 'none');
        });
      }
    };

    if (m.isStyleLoaded()) updateForecastLayers();
    else m.once('load', updateForecastLayers);
  }, [forecastVisible, forecast, selectedForecast]);

  // 3D. Selected Timestep Halo Layer Effect
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;

    const updateHalo = () => {
      if (!m.isStyleLoaded()) return;

      const activeTs = (selectedForecast || forecast)?.activeTimestep;
      const hasHaloGeom = Boolean(forecastVisible && activeTs && activeTs.position);

      const haloGeoJson = hasHaloGeom ? {
        type: 'FeatureCollection',
        features: [{
          type: 'Feature',
          geometry: activeTs!.position,
          properties: {
            horizon_hours: activeTs!.horizon_hours,
          },
        }],
      } : { type: 'FeatureCollection', features: [] };

      if (!m.getSource('forecast-selected-timestep-source')) {
        m.addSource('forecast-selected-timestep-source', {
          type: 'geojson',
          data: haloGeoJson as any,
        });

        m.addLayer({
          id: 'forecast-selected-timestep-halo',
          type: 'circle',
          source: 'forecast-selected-timestep-source',
          paint: {
            'circle-color': 'rgba(59, 130, 246, 0.35)',
            'circle-radius': 18,
            'circle-stroke-width': 2.5,
            'circle-stroke-color': '#3b82f6',
            'circle-stroke-opacity': 0.9,
          },
        });

        const handleHaloClick = () => {
          const targetFc = selectedForecast || forecast;
          if (targetFc) onForecastSelectRef.current?.(targetFc);
        };

        m.on('click', 'forecast-selected-timestep-halo', handleHaloClick);
      } else {
        (m.getSource('forecast-selected-timestep-source') as maplibregl.GeoJSONSource).setData(haloGeoJson as any);
      }

      const visibility = hasHaloGeom ? 'visible' : 'none';
      if (m.getLayer('forecast-selected-timestep-halo')) {
        m.setLayoutProperty('forecast-selected-timestep-halo', 'visibility', visibility);
      }
    };

    if (m.isStyleLoaded()) updateHalo();
    else m.once('load', updateHalo);
  }, [selectedForecast, forecast, forecastVisible]);

  // 4. Threat Assessment WebGIS Registry
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;

    const updateThreatLayers = () => {
      if (!m.isStyleLoaded()) return;

      const activeThreat = selectedThreat || threatAssessment;
      const hasAssetGeometries = activeThreat && (activeThreat.status === 'succeeded' || activeThreat.status === 'partial') && activeThreat.assets?.length;
      const hasIntersectionGeometries = activeThreat && activeThreat.threat_geometries?.features?.length;

      if (hasAssetGeometries || hasIntersectionGeometries) {
        // 4A. Sensitive Asset Boundaries Layer
        if (hasAssetGeometries && threatAssessment?.assets) {
          const assetFeatures = threatAssessment.assets.map((ast) => ({
            type: 'Feature',
            geometry: ast.geometry,
            properties: {
              asset_id: ast.asset_id,
              name: ast.name,
              asset_type: ast.asset_type,
              sensitivity_class: ast.sensitivity?.class || 'unknown',
              threat_level: ast.threat?.threat_level || 'unknown',
              color: ast.sensitivity?.class === 'very_high' ? '#ef4444' : ast.sensitivity?.class === 'high' ? '#f97316' : '#eab308',
            },
          }));

          const assetsGeoJson = { type: 'FeatureCollection', features: assetFeatures };

          if (!m.getSource('threat-assets-source')) {
            m.addSource('threat-assets-source', { type: 'geojson', data: assetsGeoJson as any });

            m.addLayer({
              id: 'threat-assets-fill',
              type: 'fill',
              source: 'threat-assets-source',
              paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.22 },
            });

            m.addLayer({
              id: 'threat-assets-outline',
              type: 'line',
              source: 'threat-assets-source',
              paint: { 'line-color': ['get', 'color'], 'line-width': 2, 'line-dasharray': [4, 2] },
            });

            m.addLayer({
              id: 'threat-assets-label',
              type: 'symbol',
              source: 'threat-assets-source',
              layout: { 'text-field': ['get', 'name'], 'text-size': 11, 'text-anchor': 'center' },
              paint: { 'text-color': '#fca5a5', 'text-halo-color': '#0f172a', 'text-halo-width': 1.5 },
            });

            m.on('click', 'threat-assets-fill', (e) => {
              if (threatAssessment) onThreatSelectRef.current?.(threatAssessment);
              if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8.5, essential: true });
            });
          } else {
            (m.getSource('threat-assets-source') as maplibregl.GeoJSONSource).setData(assetsGeoJson as any);
          }
        }

        // 4B. Threat Intersection Geometries Layer
        if (hasIntersectionGeometries && threatAssessment?.threat_geometries) {
          if (!m.getSource('threat-intersections-source')) {
            m.addSource('threat-intersections-source', { type: 'geojson', data: threatAssessment.threat_geometries as any });

            m.addLayer({
              id: 'threat-intersections-fill',
              type: 'fill',
              source: 'threat-intersections-source',
              paint: { 'fill-color': 'rgba(245, 158, 11, 0.35)', 'fill-outline-color': '#f59e0b' },
            });

            m.addLayer({
              id: 'threat-intersections-outline',
              type: 'line',
              source: 'threat-intersections-source',
              paint: { 'line-color': '#f59e0b', 'line-width': 2.5 },
            });

            m.on('click', 'threat-intersections-fill', (e) => {
              if (threatAssessment) onThreatSelectRef.current?.(threatAssessment);
              if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8.5, essential: true });
            });
          } else {
            (m.getSource('threat-intersections-source') as maplibregl.GeoJSONSource).setData(threatAssessment.threat_geometries as any);
          }
        }

        const vis = threatVisible ? 'visible' : 'none';
        ['threat-assets-fill', 'threat-assets-outline', 'threat-assets-label', 'threat-intersections-fill', 'threat-intersections-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', vis);
        });
      } else {
        ['threat-assets-fill', 'threat-assets-outline', 'threat-assets-label', 'threat-intersections-fill', 'threat-intersections-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', 'none');
        });
      }
    };

    if (m.isStyleLoaded()) updateThreatLayers();
    else m.once('load', updateThreatLayers);
  }, [threatVisible, threatAssessment]);

  // 5. Vessel Layers
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;
    const circleLayerId = 'vessels-circle-layer';
    const labelLayerId = 'vessels-label-layer';

    const updateVesselLayers = () => {
      if (!m.isStyleLoaded()) return;

      const features: any[] = [];
      const vesselDataMap = new Map<string, SelectedVesselData>();

      vesselMatches.forEach((match) => {
        const sarDet = sarDetections.find((d) => d.detection_id === match.sar_detection_id);
        const aisObs = aisObservations.find((a) => a.mmsi === match.matched_mmsi);
        const vesselMeta = mockVesselMetadataMap[match.matched_mmsi];

        const lon = sarDet ? sarDet.centroid_lon : (aisObs ? aisObs.longitude : 73.2);
        const lat = sarDet ? sarDet.centroid_lat : (aisObs ? aisObs.latitude : 18.5);

        const vesselData: SelectedVesselData = {
          id: match.match_id,
          category: 'MATCHED',
          mmsi: match.matched_mmsi,
          vessel_name: vesselMeta?.vessel_name || `MMSI: ${match.matched_mmsi}`,
          ship_type: vesselMeta?.ship_type,
          coordinates: [lon, lat],
          timestamp: sarDet?.detection_timestamp || aisObs?.timestamp,
          ais_obs: aisObs || null,
          sar_det: sarDet || null,
          match,
          anomalies: anomalies.filter((an) => an.mmsi === match.matched_mmsi),
        };

        vesselDataMap.set(match.match_id, vesselData);

        features.push({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [lon, lat] },
          properties: {
            vessel_id: match.match_id,
            label: vesselData.vessel_name || `MMSI ${match.matched_mmsi}`,
            category: 'MATCHED',
            color: '#10b981',
          },
        });
      });

      unmatchedVessels.forEach((unmatched) => {
        const sarDet = sarDetections.find((d) => d.detection_id === unmatched.sar_detection_id);
        const lon = unmatched.centroid_lon ?? sarDet?.centroid_lon ?? 73.55;
        const lat = unmatched.centroid_lat ?? sarDet?.centroid_lat ?? 18.85;

        const vesselData: SelectedVesselData = {
          id: unmatched.unmatched_id,
          category: 'UNMATCHED',
          mmsi: null,
          vessel_name: 'Unmatched SAR Detection',
          coordinates: [lon, lat],
          timestamp: unmatched.detection_timestamp,
          sar_det: sarDet || null,
          unmatched,
        };

        vesselDataMap.set(unmatched.unmatched_id, vesselData);

        features.push({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [lon, lat] },
          properties: {
            vessel_id: unmatched.unmatched_id,
            label: 'Unmatched SAR Det',
            category: 'UNMATCHED',
            color: '#f59e0b',
          },
        });
      });

      const matchedMmsis = new Set(vesselMatches.map((m) => m.matched_mmsi));
      aisObservations.forEach((ais) => {
        if (matchedMmsis.has(ais.mmsi)) return;

        const vesselMeta = mockVesselMetadataMap[ais.mmsi];
        const vesselData: SelectedVesselData = {
          id: ais.observation_id,
          category: 'AIS_ONLY',
          mmsi: ais.mmsi,
          vessel_name: vesselMeta?.vessel_name || `AIS Candidate (${ais.mmsi})`,
          ship_type: vesselMeta?.ship_type,
          coordinates: [ais.longitude, ais.latitude],
          timestamp: ais.timestamp,
          ais_obs: ais,
          anomalies: anomalies.filter((an) => an.mmsi === ais.mmsi),
        };

        vesselDataMap.set(ais.observation_id, vesselData);

        features.push({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [ais.longitude, ais.latitude] },
          properties: {
            vessel_id: ais.observation_id,
            label: `MMSI ${ais.mmsi}`,
            category: 'AIS_ONLY',
            color: '#3b82f6',
          },
        });
      });

      const geojsonCollection = {
        type: 'FeatureCollection',
        features,
      };

      if (!m.getSource('vessels-source')) {
        m.addSource('vessels-source', {
          type: 'geojson',
          data: geojsonCollection as any,
        });

        m.addLayer({
          id: circleLayerId,
          type: 'circle',
          source: 'vessels-source',
          paint: {
            'circle-color': ['get', 'color'],
            'circle-radius': 8,
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
          },
        });

        m.addLayer({
          id: labelLayerId,
          type: 'symbol',
          source: 'vessels-source',
          layout: {
            'text-field': ['get', 'label'],
            'text-size': 11,
            'text-offset': [0, 1.4],
            'text-anchor': 'top',
          },
          paint: {
            'text-color': '#e2e8f0',
            'text-halo-color': '#0f172a',
            'text-halo-width': 1.5,
          },
        });

        m.on('click', circleLayerId, (e) => {
          const feat = e.features?.[0];
          const vesselId = feat?.properties?.vessel_id;
          if (vesselId && vesselDataMap.has(vesselId)) {
            onVesselSelectRef.current?.(vesselDataMap.get(vesselId)!);
            if (e.lngLat) {
              m.flyTo({ center: e.lngLat, zoom: 9, essential: true });
            }
          }
        });

        m.on('mouseenter', circleLayerId, () => { m.getCanvas().style.cursor = 'pointer'; });
        m.on('mouseleave', circleLayerId, () => { m.getCanvas().style.cursor = ''; });
      } else {
        (m.getSource('vessels-source') as maplibregl.GeoJSONSource).setData(geojsonCollection as any);
      }

      const visibility = vesselsVisible ? 'visible' : 'none';
      if (m.getLayer(circleLayerId)) m.setLayoutProperty(circleLayerId, 'visibility', visibility);
      if (m.getLayer(labelLayerId)) m.setLayoutProperty(labelLayerId, 'visibility', visibility);
    };

    if (m.isStyleLoaded()) {
      updateVesselLayers();
    } else {
      m.once('load', updateVesselLayers);
    }
  }, [vesselsVisible, aisObservations, sarDetections, vesselMatches, unmatchedVessels, anomalies]);

  useEffect(() => {
    if (!map.current || !mapTarget) return;
    map.current.flyTo({
      center: mapTarget.center,
      zoom: mapTarget.zoom || 9,
      essential: true,
    });
  }, [mapTarget]);

  const hasVesselData = aisObservations.length > 0 || sarDetections.length > 0 || unmatchedVessels.length > 0;
  const activeFcForGeo = selectedForecast || forecast;
  const activeThForGeo = selectedThreat || threatAssessment;
  const hasForecastGeometry = Boolean(activeFcForGeo && (activeFcForGeo.status === 'succeeded' || activeFcForGeo.status === 'partial') && activeFcForGeo.trajectory?.features?.length);
  const hasThreatGeometry = Boolean(activeThForGeo && (activeThForGeo.status === 'succeeded' || activeThForGeo.status === 'partial') && (activeThForGeo.assets?.length || activeThForGeo.threat_geometries?.features?.length));

  return (
    <div className={`relative w-full h-full ${className}`}>
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 text-red-500 z-10">
          <p>{error}</p>
        </div>
      )}

      {/* Map Layer Control Overlay */}
      <div className="absolute top-4 right-14 z-10 flex flex-col gap-1.5 pointer-events-auto">
        <button
          type="button"
          className="flex items-center justify-between gap-2.5 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 hover:border-amber-500/60 active:scale-95 rounded-lg px-3 py-1.5 shadow-xl transition-all text-xs font-semibold text-slate-200 cursor-pointer min-w-[130px]"
          onClick={() => {
            setThreatVisible((v) => {
              const next = !v;
              if (map.current && map.current.isStyleLoaded()) {
                const vis = next ? 'visible' : 'none';
                ['threat-assets-fill', 'threat-assets-outline', 'threat-assets-label', 'threat-intersections-fill', 'threat-intersections-outline'].forEach((id) => {
                  if (map.current?.getLayer(id)) map.current.setLayoutProperty(id, 'visibility', vis);
                });
              }
              return next;
            });
            if (activeThForGeo) onThreatSelectRef.current?.(activeThForGeo);
          }}
        >
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${threatVisible ? 'bg-amber-400 shadow-sm shadow-amber-400/80 animate-pulse' : 'bg-slate-500'}`} />
            <span>Threat</span>
          </div>
          <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded ${threatVisible ? 'bg-amber-950 text-amber-300 border border-amber-800/60' : 'bg-slate-800 text-slate-400'}`}>
            {threatVisible ? 'ON' : 'OFF'}
          </span>
        </button>

        <button
          type="button"
          className="flex items-center justify-between gap-2.5 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 hover:border-blue-500/60 active:scale-95 rounded-lg px-3 py-1.5 shadow-xl transition-all text-xs font-semibold text-slate-200 cursor-pointer min-w-[130px]"
          onClick={() => {
            setForecastVisible((v) => {
              const next = !v;
              if (map.current && map.current.isStyleLoaded()) {
                const vis = next ? 'visible' : 'none';
                ['forecast-trajectory-layer', 'forecast-timesteps-layer', 'forecast-timesteps-label-layer', 'forecast-uncertainty-fill', 'forecast-uncertainty-outline', 'forecast-selected-timestep-halo'].forEach((id) => {
                  if (map.current?.getLayer(id)) map.current.setLayoutProperty(id, 'visibility', vis);
                });
              }
              return next;
            });
            if (activeFcForGeo) onForecastSelectRef.current?.(activeFcForGeo);
          }}
        >
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${forecastVisible ? 'bg-blue-400 shadow-sm shadow-blue-400/80 animate-pulse' : 'bg-slate-500'}`} />
            <span>Forecast</span>
          </div>
          <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded ${forecastVisible ? 'bg-blue-950 text-blue-300 border border-blue-800/60' : 'bg-slate-800 text-slate-400'}`}>
            {forecastVisible ? 'ON' : 'OFF'}
          </span>
        </button>

        <button
          type="button"
          className="flex items-center justify-between gap-2.5 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 hover:border-emerald-500/60 active:scale-95 rounded-lg px-3 py-1.5 shadow-xl transition-all text-xs font-semibold text-slate-200 cursor-pointer min-w-[130px]"
          onClick={() => {
            setVesselsVisible((v) => {
              const next = !v;
              if (map.current && map.current.isStyleLoaded()) {
                const vis = next ? 'visible' : 'none';
                if (map.current.getLayer('vessels-circle-layer')) map.current.setLayoutProperty('vessels-circle-layer', 'visibility', vis);
                if (map.current.getLayer('vessels-label-layer')) map.current.setLayoutProperty('vessels-label-layer', 'visibility', vis);
              }
              return next;
            });
          }}
        >
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${vesselsVisible ? 'bg-emerald-400 shadow-sm shadow-emerald-400/80 animate-pulse' : 'bg-slate-500'}`} />
            <span>Vessels</span>
          </div>
          <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded ${vesselsVisible ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/60' : 'bg-slate-800 text-slate-400'}`}>
            {vesselsVisible ? 'ON' : 'OFF'}
          </span>
        </button>

        <button
          type="button"
          className="flex items-center justify-between gap-2.5 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 hover:border-cyan-500/60 active:scale-95 rounded-lg px-3 py-1.5 shadow-xl transition-all text-xs font-semibold text-slate-200 cursor-pointer min-w-[130px]"
          onClick={() => {
            setSarVisible((v) => {
              const next = !v;
              if (map.current && map.current.isStyleLoaded()) {
                const vis = next ? 'visible' : 'none';
                ['sar-fill-layer', 'sar-outline-layer', 'person1-spill-detection-fill', 'person1-spill-detection-line'].forEach((id) => {
                  if (map.current?.getLayer(id)) map.current.setLayoutProperty(id, 'visibility', vis);
                });
              }
              return next;
            });
            if (sarScenes.length > 0) onSarSelectRef.current?.(sarScenes[0]);
          }}
        >
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${sarVisible ? 'bg-cyan-400 shadow-sm shadow-cyan-400/80 animate-pulse' : 'bg-slate-500'}`} />
            <span>SAR Layer</span>
          </div>
          <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded ${sarVisible ? 'bg-cyan-950 text-cyan-300 border border-cyan-800/60' : 'bg-slate-800 text-slate-400'}`}>
            {sarVisible ? 'ON' : 'OFF'}
          </span>
        </button>
      </div>

      <div className="absolute top-4 left-88 z-10 flex flex-col gap-2 pointer-events-none">
        {vesselsVisible && !hasVesselData && (
          <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/50 rounded-full px-3.5 py-1 shadow-lg flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
            <span className="text-[11px] font-medium text-slate-300">Vessel geometry unavailable</span>
          </div>
        )}

        {forecastVisible && !hasForecastGeometry && (
          <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/50 rounded-full px-3.5 py-1 shadow-lg flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
            <span className="text-[11px] font-medium text-slate-300">Forecast contract unapproved / geometry unavailable</span>
          </div>
        )}

        {threatVisible && !hasThreatGeometry && (
          <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/50 rounded-full px-3.5 py-1 shadow-lg flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
            <span className="text-[11px] font-medium text-slate-300">Threat contract unapproved / geometry unavailable</span>
          </div>
        )}
      </div>

      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
};
