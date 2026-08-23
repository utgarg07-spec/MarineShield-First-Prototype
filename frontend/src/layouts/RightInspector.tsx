import React, { useEffect, useState } from 'react';
import { useMatch } from 'react-router-dom';
import { Crosshair, ShieldAlert, FileText, Anchor, Activity, Clock, Navigation, AlertTriangle } from 'lucide-react';
import { api } from '../api';
import type { Incident } from '../api/types/incident';
import { LoadingState } from '../components/feedback/LoadingState';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';

interface RightInspectorProps {
  selectedSar?: SARSceneMetadata | null;
  selectedVessel?: SelectedVesselData | null;
  selectedForecast?: Forecast | null;
  selectedThreat?: ThreatAssessment | null;
}

export const RightInspector: React.FC<RightInspectorProps> = ({ selectedSar, selectedVessel, selectedForecast, selectedThreat }) => {
  const match = useMatch('/incidents/:incidentId');
  const incidentId = match?.params.incidentId;
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!incidentId) {
      setIncident(null);
      return;
    }
    setLoading(true);
    api.getIncident(incidentId)
      .then(response => setIncident(response.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [incidentId]);

  return (
    <aside className="hidden xl:flex flex-col w-80 bg-slate-950/80 border-l border-slate-800/70 shrink-0 z-10 overflow-y-auto">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-800/70 shrink-0 flex items-center justify-between">
        <h2 className="text-[10px] font-bold uppercase tracking-widest text-cyan-400">
          Intelligence Inspector
        </h2>
        <span className="text-[9px] font-mono text-slate-500 uppercase">Phase 5A</span>
      </div>

      {loading ? (
        <div className="flex-1 p-4"><LoadingState /></div>
      ) : (
        <div className="flex-1 flex flex-col p-4 gap-6">
          
          {incident && (
            <div>
              <div className="text-xs text-cyan-500 font-medium tracking-widest uppercase mb-1">{incident.reference}</div>
              <div className="text-sm font-semibold text-slate-200 truncate" title={incident.title || undefined}>{incident.title}</div>
            </div>
          )}

          {incident && (
            <div className="space-y-4">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Status</span>
                <div className="flex items-center gap-2">
                  <Activity className="w-3 h-3 text-slate-400" />
                  <span className="text-xs text-slate-300">{incident.status}</span>
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Location</span>
                <div className="flex items-center gap-2">
                  <Anchor className="w-3 h-3 text-slate-400" />
                  <span className="text-xs text-slate-300 truncate" title={incident.location?.source || undefined}>{incident.location?.source || 'Unknown Location'}</span>
                </div>
              </div>
              
              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Reported</span>
                <div className="flex items-center gap-2">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <span className="text-xs text-slate-300">{new Date(incident.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {/* Selected Vessel Intelligence Card */}
          {selectedVessel && (
            <div className="border-t border-slate-800/60 pt-4 space-y-4">
              <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-700/60 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-cyan-400 font-bold">
                    <Navigation className="w-4 h-4" />
                    <span className="text-xs uppercase tracking-wider">Vessel Intelligence</span>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                    selectedVessel.category === 'MATCHED'
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
                      : selectedVessel.category === 'UNMATCHED'
                      ? 'bg-amber-950 text-amber-400 border border-amber-800/60'
                      : 'bg-blue-950 text-blue-400 border border-blue-800/60'
                  }`}>
                    {selectedVessel.category}
                  </span>
                </div>

                {/* Primary Identifiers */}
                <div className="space-y-1.5 pt-1 border-t border-slate-800/60">
                  <div className="text-xs font-bold text-slate-100 truncate" title={selectedVessel.vessel_name || undefined}>
                    {selectedVessel.vessel_name || (selectedVessel.mmsi ? `MMSI: ${selectedVessel.mmsi}` : 'Unidentified Vessel')}
                  </div>
                  {selectedVessel.mmsi && selectedVessel.vessel_name && (
                    <div className="text-[11px] text-slate-400 font-mono">MMSI: {selectedVessel.mmsi}</div>
                  )}
                  <div className="text-[11px] text-slate-400">
                    Position: <span className="font-mono text-slate-300">[{selectedVessel.coordinates[0]}, {selectedVessel.coordinates[1]}]</span>
                  </div>
                </div>

                {/* AIS Observation Details */}
                {selectedVessel.ais_obs && (
                  <div className="pt-2 border-t border-slate-800/60 space-y-1 text-xs">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">AIS Observation</div>
                    <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-300">
                      <div>Speed: <span className="font-mono text-slate-200">{selectedVessel.ais_obs.speed_over_ground_knots} kts</span></div>
                      <div>Heading: <span className="font-mono text-slate-200">{selectedVessel.ais_obs.heading_deg ?? selectedVessel.ais_obs.course_over_ground_deg}°</span></div>
                    </div>
                    <div className="text-[11px] text-slate-400 truncate" title={selectedVessel.ais_obs.navigational_status}>Status: {selectedVessel.ais_obs.navigational_status}</div>
                    <div className="text-[10px] text-slate-500">Provider: {selectedVessel.ais_obs.source_provider}</div>
                  </div>
                )}

                {/* SAR Detection Details */}
                {selectedVessel.sar_det && (
                  <div className="pt-2 border-t border-slate-800/60 space-y-1 text-xs">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">SAR Radar Signature</div>
                    <div className="text-[11px] text-slate-300 font-mono truncate" title={selectedVessel.sar_det.detection_id}>{selectedVessel.sar_det.detection_id}</div>
                    <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-300">
                      <div>Dimensions: <span className="font-mono">{selectedVessel.sar_det.estimated_length_meters}m × {selectedVessel.sar_det.estimated_width_meters}m</span></div>
                      <div>Confidence: <span className="font-mono text-emerald-400">{(selectedVessel.sar_det.detection_confidence * 100).toFixed(0)}%</span></div>
                    </div>
                  </div>
                )}

                {/* Match Details */}
                {selectedVessel.match && (
                  <div className="pt-2 border-t border-slate-800/60 space-y-1 text-xs bg-emerald-950/20 p-2 rounded border border-emerald-800/30">
                    <div className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">AIS-SAR Correlation</div>
                    <div className="text-[11px] text-slate-300">Match Confidence: <span className="font-mono font-bold text-emerald-300">{(selectedVessel.match.match_confidence * 100).toFixed(2)}%</span></div>
                    <div className="text-[11px] text-slate-400">Spatial Offset: <span className="font-mono">{selectedVessel.match.distance_offset_meters} m</span></div>
                  </div>
                )}

                {/* Unmatched Details */}
                {selectedVessel.unmatched && (
                  <div className="pt-2 border-t border-slate-800/60 space-y-1.5 text-xs bg-amber-950/20 p-2 rounded border border-amber-800/30">
                    <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-amber-400 tracking-wider">
                      <AlertTriangle className="w-3 h-3" />
                      <span>Transponder Correlation Unavailable</span>
                    </div>
                    <div className="text-[11px] text-slate-300">Dark Vessel Confidence: <span className="font-mono font-bold text-amber-300">{(selectedVessel.unmatched.dark_vessel_confidence * 100).toFixed(0)}%</span></div>
                  </div>
                )}

              </div>
            </div>
          )}

          {/* Selected SAR Scene Card */}
          {selectedSar && (
            <div className="border-t border-slate-800/50 pt-4 space-y-4">
              <div className="flex flex-col gap-1.5 p-3 rounded bg-slate-900/50 border border-slate-800/50">
                <div className="flex items-center gap-2 text-indigo-400 mb-1">
                  <Crosshair className="w-3.5 h-3.5" />
                  <span className="text-[10px] uppercase font-bold tracking-wider">SAR Metadata</span>
                </div>
                <div className="text-xs text-slate-300">
                  <span className="text-slate-500 block text-[10px] uppercase">Granule ID</span>
                  <span className="font-mono text-[11px] block truncate" title={selectedSar.scene_identifier.granule_id}>
                    {selectedSar.scene_identifier.granule_id}
                  </span>
                </div>
                <div className="text-xs text-slate-300">
                  <span className="text-slate-500 block text-[10px] uppercase">Acquisition Start</span>
                  {new Date(selectedSar.acquisition_time.start_time).toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {/* Selected Forecast Card */}
          {selectedForecast && (
            <div className="border-t border-slate-800/60 pt-4 space-y-4">
              <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-700/60 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-blue-400 font-bold">
                    <FileText className="w-4 h-4" />
                    <span className="text-xs uppercase tracking-wider">Forecast WebGIS</span>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider bg-blue-950 text-blue-400 border border-blue-800/60">
                    {selectedForecast.status}
                  </span>
                </div>

                {/* Active Timestep Details */}
                {selectedForecast.activeTimestep ? (
                  <div className="space-y-2 pt-2 border-t border-slate-800/60">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] text-slate-400 font-medium">Selected Horizon:</span>
                      <span className="text-xs font-mono font-bold text-blue-300 bg-blue-950/80 border border-blue-800/60 px-2 py-0.5 rounded">
                        +{selectedForecast.activeTimestep.horizon_hours}h
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-300">
                      Valid Time: <span className="font-mono text-slate-200">{new Date(selectedForecast.activeTimestep.valid_time).toLocaleString()}</span>
                    </div>
                    {selectedForecast.activeTimestep.position?.coordinates && (
                      <div className="text-[11px] text-slate-400">
                        Position: <span className="font-mono text-slate-300">[{selectedForecast.activeTimestep.position.coordinates[0]}, {selectedForecast.activeTimestep.position.coordinates[1]}]</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-[11px] text-slate-400 italic pt-1 border-t border-slate-800/60">
                    Select a timestep dot (+6h, +12h, +24h, +48h) on the map to inspect details.
                  </div>
                )}

                {/* Provenance & Data Mode */}
                <div className="pt-2 border-t border-slate-800/60 space-y-1.5 text-[11px]">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Engine / Model:</span>
                    <span className="font-mono text-slate-200">{selectedForecast.provenance?.forecast_engine || 'PyGNOME'}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Reference Time:</span>
                    <span className="font-mono text-slate-200">{new Date(selectedForecast.forecast_reference_time).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Data Mode:</span>
                    <span className="font-mono text-cyan-400 font-semibold">MOCK_HYBRID</span>
                  </div>
                </div>

                {selectedForecast.response_priority?.requires_human_review && (
                  <div className="p-2 rounded bg-amber-950/30 border border-amber-800/50 text-[10px] text-amber-300 flex items-start gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-400 mt-0.5" />
                    <span>Human Review Required — Material uncertainty region.</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Selected Threat Assessment Card */}
          {selectedThreat && (
            <div className="border-t border-slate-800/60 pt-4 space-y-4">
              <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-700/60 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-amber-500 font-bold">
                    <ShieldAlert className="w-4 h-4" />
                    <span className="text-xs uppercase tracking-wider">Threat Assessment</span>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider bg-amber-950 text-amber-400 border border-amber-800/60">
                    {selectedThreat.status}
                  </span>
                </div>
                <div className="text-xs text-slate-300">
                  Overall Level: <span className="font-bold text-amber-400 uppercase">{selectedThreat.summary?.overall_threat_level || 'HIGH'}</span>
                </div>
              </div>
            </div>
          )}

          {!selectedVessel && !selectedSar && !selectedForecast && !selectedThreat && !incident && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-slate-500">
              <Crosshair className="w-8 h-8 mb-2 stroke-[1.5] text-slate-600" />
              <p className="text-xs font-medium text-slate-400">No intelligence selected</p>
              <p className="text-[10px] text-slate-600 mt-1 max-w-[180px]">
                Click on a vessel, SAR footprint, or incident feature to inspect details.
              </p>
            </div>
          )}

        </div>
      )}
    </aside>
  );
};
