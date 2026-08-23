import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Ship, AlertTriangle } from 'lucide-react';
import { api } from '../api';
import type { AISObservation, SARVesselDetection, VesselMatch, UnmatchedVessel, SelectedVesselData } from '../api/types/vessel';
import type { SARSceneMetadata } from '../api/types/sar';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';
import { Panel, PanelHeader, Badge } from '../components/ui';
import { LoadingState } from '../components/feedback/LoadingState';
import { mockVesselMetadataMap } from '../mocks/fixtures/vessels';

export const VesselsPage: React.FC = () => {
  const { setSelectedVessel } = useOutletContext<{
    setSelectedSar: (sar: SARSceneMetadata | null) => void;
    setSelectedVessel: (vessel: SelectedVesselData | null) => void;
    setSelectedForecast: (forecast: Forecast | null) => void;
    setSelectedThreat: (threat: ThreatAssessment | null) => void;
  }>();

  const [aisObservations, setAisObservations] = useState<AISObservation[]>([]);
  const [sarDetections, setSarDetections] = useState<SARVesselDetection[]>([]);
  const [vesselMatches, setVesselMatches] = useState<VesselMatch[]>([]);
  const [unmatchedVessels, setUnmatchedVessels] = useState<UnmatchedVessel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const incidentId = 'MS-PHASE6-DEV-001';
    Promise.all([
      api.getVessels(incidentId),
      api.getSARDetections(incidentId),
      api.getVesselMatches(incidentId),
      api.getUnmatchedVessels(incidentId),
    ])
      .then(([vesselsRes, sarDetRes, matchesRes, unmatchedRes]) => {
        setAisObservations(vesselsRes.data);
        setSarDetections(sarDetRes.data);
        setVesselMatches(matchesRes.data);
        setUnmatchedVessels(unmatchedRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSelectMatched = (match: VesselMatch) => {
    const sarDet = sarDetections.find((d) => d.detection_id === match.sar_detection_id);
    const aisObs = aisObservations.find((a) => a.mmsi === match.matched_mmsi);
    const vesselMeta = mockVesselMetadataMap[match.matched_mmsi];
    const lon = sarDet ? sarDet.centroid_lon : (aisObs ? aisObs.longitude : 73.2);
    const lat = sarDet ? sarDet.centroid_lat : (aisObs ? aisObs.latitude : 18.5);

    setSelectedVessel({
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
    });
  };

  const handleSelectUnmatched = (unmatched: UnmatchedVessel) => {
    const sarDet = sarDetections.find((d) => d.detection_id === unmatched.sar_detection_id);
    const lon = unmatched.centroid_lon ?? sarDet?.centroid_lon ?? 73.55;
    const lat = unmatched.centroid_lat ?? sarDet?.centroid_lat ?? 18.85;

    setSelectedVessel({
      id: unmatched.unmatched_id,
      category: 'UNMATCHED',
      mmsi: null,
      vessel_name: 'Unmatched SAR Detection',
      coordinates: [lon, lat],
      timestamp: unmatched.detection_timestamp,
      sar_det: sarDet || null,
      unmatched,
    });
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Ship className="w-5 h-5 text-emerald-400" />
            <h1 className="text-xl font-bold text-slate-100">Vessel Intelligence Workspace</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic AIS Telemetry & SAR Radar Vessel Correlation (Person 2 Handoff)
          </p>
        </div>
        <Badge className="bg-emerald-950 text-emerald-400 border-emerald-800/60 font-mono text-xs">
          SYNTHETIC_DEVELOPMENT_FIXTURE
        </Badge>
      </div>

      {loading ? (
        <LoadingState message="Loading vessel telemetry..." />
      ) : (
        <div className="space-y-6">
          {/* Matched Vessels Section */}
          <Panel className="space-y-3">
            <PanelHeader title="Correlated Vessels (AIS + SAR)" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {vesselMatches.map((m) => {
                const meta = mockVesselMetadataMap[m.matched_mmsi];
                return (
                  <div
                    key={m.match_id}
                    onClick={() => handleSelectMatched(m)}
                    className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-emerald-500/60 transition-all cursor-pointer space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-200">{meta?.vessel_name || `MMSI ${m.matched_mmsi}`}</span>
                      <Badge className="bg-emerald-950 text-emerald-400 border-emerald-800/60 text-[10px] uppercase">
                        MATCHED ({(m.match_confidence * 100).toFixed(0)}%)
                      </Badge>
                    </div>
                    <div className="text-xs text-slate-400 space-y-1 font-mono">
                      <div>MMSI: {m.matched_mmsi}</div>
                      <div>Spatial Offset: {m.distance_offset_meters} m</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Panel>

          {/* Dark Vessel Anomalies Section */}
          <Panel className="space-y-3">
            <PanelHeader title="Unmatched Dark Vessel Detections" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {unmatchedVessels.map((u) => (
                <div
                  key={u.unmatched_id}
                  onClick={() => handleSelectUnmatched(u)}
                  className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-amber-500/60 transition-all cursor-pointer space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-amber-400 font-bold text-xs">
                      <AlertTriangle className="w-4 h-4" />
                      <span>Unmatched SAR Detection</span>
                    </div>
                    <Badge className="bg-amber-950 text-amber-400 border-amber-800/60 text-[10px] uppercase">
                      UNMATCHED
                    </Badge>
                  </div>
                  <div className="text-xs text-slate-400 space-y-1 font-mono">
                    <div>Dark Vessel Confidence: {(u.dark_vessel_confidence * 100).toFixed(0)}%</div>
                    <div>Search Radius: {u.ais_search_radius_km} km</div>
                  </div>
                  <p className="text-[11px] text-slate-400 italic pt-1">{u.description}</p>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
};
