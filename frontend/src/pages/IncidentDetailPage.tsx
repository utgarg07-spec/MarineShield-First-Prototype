import React, { useEffect, useState } from 'react';
import { useParams, useOutletContext } from 'react-router-dom';
import { MapWorkspace } from '../layouts/MapWorkspace';
import { api } from '../api';
import type { Incident } from '../api/types/incident';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData, AISObservation, SARVesselDetection, VesselMatch, UnmatchedVessel, AnomalyEvent } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';
import type { SpillDetectionResponse } from '../api/types/oil_intelligence';
import type { InvestigationResult } from '../api/types/investigation';
import { Panel, PanelHeader, Badge } from '../components/ui';
import { ShieldAlert, FileText, FileSearch, Database, Activity, Anchor, Crosshair, Layers } from 'lucide-react';
import { LoadingState } from '../components/feedback/LoadingState';
import { mockVesselMetadataMap } from '../mocks/fixtures/vessels';
import { useApp } from '../context/AppContext';

export const IncidentDetailPage: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const { addNotification } = useApp();
  const {
    selectedSar,
    setSelectedSar,
    selectedVessel,
    setSelectedVessel,
    selectedForecast,
    setSelectedForecast,
    selectedThreat,
    setSelectedThreat,
  } = useOutletContext<{
    selectedSar: SARSceneMetadata | null;
    setSelectedSar: (sar: SARSceneMetadata | null) => void;
    selectedVessel: SelectedVesselData | null;
    setSelectedVessel: (vessel: SelectedVesselData | null) => void;
    selectedForecast: Forecast | null;
    setSelectedForecast: (forecast: Forecast | null) => void;
    selectedThreat: ThreatAssessment | null;
    setSelectedThreat: (threat: ThreatAssessment | null) => void;
  }>();

  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);

  const [sarScenes, setSarScenes] = useState<SARSceneMetadata[]>([]);
  const [aisObservations, setAisObservations] = useState<AISObservation[]>([]);
  const [sarDetections, setSarDetections] = useState<SARVesselDetection[]>([]);
  const [vesselMatches, setVesselMatches] = useState<VesselMatch[]>([]);
  const [unmatchedVessels, setUnmatchedVessels] = useState<UnmatchedVessel[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyEvent[]>([]);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [threat, setThreat] = useState<ThreatAssessment | null>(null);

  const [spillDetection, setSpillDetection] = useState<SpillDetectionResponse | null>(null);
  const [investigationResult, setInvestigationResult] = useState<InvestigationResult | null>(null);

  useEffect(() => {
    if (!incidentId) return;
    setLoading(true);
    api.getIncident(incidentId)
      .then(response => setIncident(response.data))
      .catch(console.error)
      .finally(() => setLoading(false));

    api.getSARScenes(incidentId)
      .then(res => setSarScenes(res.data))
      .catch(console.error);

    Promise.all([
      api.getVessels(incidentId),
      api.getSARDetections(incidentId),
      api.getVesselMatches(incidentId),
      api.getUnmatchedVessels(incidentId),
      api.getAnomalies(incidentId),
    ])
      .then(([vesselsRes, sarDetRes, matchesRes, unmatchedRes, anomaliesRes]) => {
        setAisObservations(vesselsRes.data);
        setSarDetections(sarDetRes.data);
        setVesselMatches(matchesRes.data);
        setUnmatchedVessels(unmatchedRes.data);
        setAnomalies(anomaliesRes.data);
      })
      .catch(console.error);

    api.getForecast(incidentId, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then(res => setForecast(res.data))
      .catch(console.error);

    api.getThreatAssessment(incidentId, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then(res => setThreat(res.data))
      .catch(console.error);

    // Fetch Person 1 canonical presentation outputs
    api.detectSpill({ incident_id: incidentId, sar_granule_id: 'S1A_IW_GRDH_1SDV' })
      .then(res => setSpillDetection(res.data))
      .catch(console.error);

    api.reconstructRelease({
      incident_id: incidentId,
      t_observation_utc: '2024-01-20T00:55:41Z',
      spill_centroid_lon_lat: [73.2015, 18.5012],
    })
      .then(res => setInvestigationResult(res.data))
      .catch(console.error);
  }, [incidentId]);

  useEffect(() => {
    if (!incidentId) return;

    if (threat?.summary?.overall_threat_level === 'high') {
      addNotification({
        id: `notif-threat-high-${incidentId}`,
        title: 'High Threat Assessment',
        message: 'Threat assessment requires operator attention.',
        type: 'warning',
        source: 'threat',
      });
    }

    if (unmatchedVessels && unmatchedVessels.length > 0) {
      addNotification({
        id: `notif-vessel-unmatched-${incidentId}`,
        title: 'Unmatched Vessel Detected',
        message: 'An SAR detection could not be correlated with AIS.',
        type: 'warning',
        source: 'vessel',
      });
    }

    if (forecast?.response_priority?.requires_human_review) {
      addNotification({
        id: `notif-forecast-review-${incidentId}`,
        title: 'Forecast Requires Review',
        message: 'Forecast priority indicates human review is required.',
        type: 'info',
        source: 'forecast',
      });
    }
  }, [incidentId, threat, unmatchedVessels, forecast, addNotification]);

  const clearAllSelections = () => {
    setSelectedSar(null);
    setSelectedVessel(null);
    setSelectedForecast(null);
    setSelectedThreat(null);
  };

  const focusDomain = (domain: 'sar' | 'vessels' | 'forecast' | 'threat') => {
    clearAllSelections();
    if (domain === 'sar' && sarScenes.length > 0) {
      setSelectedSar(sarScenes[0]);
    } else if (domain === 'vessels') {
      if (aisObservations.length > 0) {
        const obs = aisObservations[0];
        const match = vesselMatches.find(m => m.matched_mmsi === obs.mmsi);
        const meta = mockVesselMetadataMap[obs.mmsi];
        setSelectedVessel({
          id: obs.observation_id,
          category: match ? 'MATCHED' : 'AIS_ONLY',
          mmsi: obs.mmsi,
          vessel_name: meta?.vessel_name || 'MV OCEAN TRADER',
          ship_type: meta?.ship_type || 'TANKER_CRUDE_OIL',
          coordinates: [obs.longitude, obs.latitude],
          timestamp: obs.timestamp,
          ais_obs: obs,
          match: match || null,
        });
      } else if (unmatchedVessels.length > 0) {
        const unmatch = unmatchedVessels[0];
        setSelectedVessel({
          id: unmatch.unmatched_id,
          category: 'UNMATCHED',
          coordinates: [unmatch.centroid_lon, unmatch.centroid_lat],
          timestamp: unmatch.detection_timestamp,
          unmatched: unmatch,
        });
      }
    } else if (domain === 'forecast' && forecast) {
      const defaultTs = forecast.timesteps?.[0] || null;
      setSelectedForecast({
        ...forecast,
        activeTimestep: defaultTs,
      });
    } else if (domain === 'threat' && threat) {
      setSelectedThreat(threat);
    }
  };

  const selectForecastHorizon = (horizonHours: number) => {
    clearAllSelections();
    if (forecast && forecast.timesteps) {
      const matchedTs = forecast.timesteps.find((ts) => ts.horizon_hours === horizonHours) || forecast.timesteps[0];
      setSelectedForecast({
        ...forecast,
        activeTimestep: matchedTs,
      });
    } else if (forecast) {
      setSelectedForecast(forecast);
    }
  };

  const totalVesselItems = aisObservations.length + sarDetections.length + unmatchedVessels.length + anomalies.length;

  const { mapTarget } = useApp();

  return (
    <MapWorkspace
      incident={incident}
      spillDetection={spillDetection}
      investigationResult={investigationResult}
      selectedSar={selectedSar}
      selectedVessel={selectedVessel}
      selectedForecast={selectedForecast}
      selectedThreat={selectedThreat}
      onSarSelect={setSelectedSar}
      onVesselSelect={setSelectedVessel}
      onForecastSelect={setSelectedForecast}
      onThreatSelect={setSelectedThreat}
      onClearSelection={clearAllSelections}
      mapTarget={mapTarget}
    >
      {/* Zone 3: Selected Intelligence Context Strip */}
      <div className="absolute top-44 right-4 z-10 pointer-events-auto max-w-md">
        <div className="bg-slate-950/90 backdrop-blur-md border border-slate-800/90 rounded-xl px-3.5 py-1.5 shadow-2xl flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className={`p-1 rounded-lg border shrink-0 ${
              selectedSar ? 'bg-cyan-950 text-cyan-400 border-cyan-800/80' :
              selectedVessel ? 'bg-emerald-950 text-emerald-400 border-emerald-800/80' :
              selectedForecast ? 'bg-blue-950 text-blue-400 border-blue-800/80' :
              selectedThreat ? 'bg-amber-950 text-amber-400 border-amber-800/80' :
              'bg-slate-900 text-slate-500 border-slate-800'
            }`}>
              {selectedSar ? <FileSearch className="w-3.5 h-3.5" /> :
               selectedVessel ? <Anchor className="w-3.5 h-3.5" /> :
               selectedForecast ? <FileText className="w-3.5 h-3.5" /> :
               selectedThreat ? <ShieldAlert className="w-3.5 h-3.5" /> :
               <Crosshair className="w-3.5 h-3.5" />}
            </div>

            <div className="min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-[8px] font-mono font-bold uppercase tracking-widest text-slate-400">
                  SELECTED INTELLIGENCE
                </span>
                {selectedSar && <span className="text-[8px] font-bold px-1 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60 uppercase">SAR</span>}
                {selectedVessel && <span className="text-[8px] font-bold px-1 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60 uppercase">VESSEL ({selectedVessel.category})</span>}
                {selectedForecast && <span className="text-[8px] font-bold px-1 py-0.2 rounded bg-blue-950 text-blue-300 border border-blue-800/60 uppercase">FORECAST</span>}
                {selectedThreat && <span className="text-[8px] font-bold px-1 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-800/60 uppercase">THREAT</span>}
              </div>

              <div className="text-xs font-semibold text-slate-200 truncate mt-0.5 max-w-[240px]">
                {selectedSar ? `${selectedSar.scene_identifier.mission} (${selectedSar.scene_identifier.granule_id.slice(0, 14)}...)` :
                 selectedVessel ? `${selectedVessel.vessel_name || selectedVessel.id} (MMSI: ${selectedVessel.mmsi || 'N/A'})` :
                 selectedForecast ? `${selectedForecast.provenance?.forecast_engine || 'PyGNOME Model'} — Status: ${selectedForecast.status}` :
                 selectedThreat ? `Overall Threat: ${selectedThreat.summary?.overall_threat_level || 'HIGH'}` :
                 'None selected'}
              </div>
            </div>
          </div>

          {(selectedSar || selectedVessel || selectedForecast || selectedThreat) && (
            <button
              type="button"
              onClick={clearAllSelections}
              className="shrink-0 px-2 py-0.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-[9px] font-semibold text-slate-300 hover:text-white transition-all cursor-pointer"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Left Overlay Sidebar: Integrated Investigation Workspace */}
      <div className="absolute top-4 left-4 bottom-4 w-80 flex flex-col gap-4 overflow-y-auto pointer-events-auto pr-2">
        {loading ? (
          <Panel><LoadingState message="Loading incident data..." /></Panel>
        ) : incident ? (
          <>
            {/* 1. Investigation Overview & Header */}
            <Panel className="shrink-0 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                <div>
                  <div className="text-[10px] font-bold uppercase tracking-widest text-cyan-400">Incident Investigation</div>
                  <div className="text-base font-bold text-slate-100 flex items-center gap-2 mt-0.5">
                    {incident.reference}
                    <Badge className="bg-emerald-950 text-emerald-400 border-emerald-800/60 text-[10px] font-mono uppercase">
                      {incident.status}
                    </Badge>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase font-semibold text-slate-500 block">Reported</span>
                  <span className="text-[11px] font-mono text-slate-300">{new Date(incident.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="text-xs text-slate-300">
                <span className="text-slate-500 text-[10px] font-semibold uppercase block mb-0.5">Location & Source</span>
                <span className="font-medium text-slate-200">{incident.location?.source || 'Strait of Malacca'}</span>
              </div>

              {/* Intelligence Domain Status Grid */}
              <div className="pt-2 border-t border-slate-800/60 space-y-1.5">
                <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center justify-between">
                  <span>Intelligence Domains</span>
                  <span className="text-[9px] text-cyan-400 font-mono">4/4 ACTIVE</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div
                    onClick={() => focusDomain('sar')}
                    className="p-2 rounded bg-slate-900/90 border border-cyan-800/40 space-y-0.5 cursor-pointer hover:border-cyan-500/60 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-cyan-400">SAR</span>
                      <span className="text-[9px] font-bold px-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/60">
                        {sarScenes.length > 0 ? 'AVAILABLE' : 'AWAITING'}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-300 font-mono">{sarScenes.length} Scene(s)</div>
                  </div>

                  <div
                    onClick={() => focusDomain('vessels')}
                    className="p-2 rounded bg-slate-900/90 border border-emerald-800/40 space-y-0.5 cursor-pointer hover:border-emerald-500/60 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-emerald-400">Vessels</span>
                      <span className="text-[9px] font-bold px-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60">
                        {totalVesselItems > 0 ? 'AVAILABLE' : 'AWAITING'}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-300 font-mono">{totalVesselItems} Detections</div>
                  </div>

                  <div
                    onClick={() => focusDomain('forecast')}
                    className="p-2 rounded bg-slate-900/90 border border-blue-800/40 space-y-0.5 cursor-pointer hover:border-blue-500/60 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-blue-400">Forecast</span>
                      <span className="text-[9px] font-bold px-1 rounded bg-blue-950 text-blue-300 border border-blue-800/60">
                        {forecast?.status === 'succeeded' ? 'SUCCEEDED' : forecast?.status?.toUpperCase() || 'AWAITING'}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-300 font-mono">PyGNOME +48h</div>
                  </div>

                  <div
                    onClick={() => focusDomain('threat')}
                    className="p-2 rounded bg-slate-900/90 border border-amber-800/40 space-y-0.5 cursor-pointer hover:border-amber-500/60 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase text-amber-400">Threat</span>
                      <span className="text-[9px] font-bold px-1 rounded bg-red-950 text-red-300 border border-red-800/60">
                        {threat?.summary?.overall_threat_level || 'HIGH'}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-300 font-mono">Priority 86/100</div>
                  </div>
                </div>
              </div>
            </Panel>

            {/* 2. Integrated Intelligence Summary */}
            <Panel className="shrink-0 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-cyan-400">
                  <Activity className="w-4 h-4" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Intelligence Picture</h3>
                </div>
                <span className="text-[9px] font-mono text-slate-500 uppercase">Cross-Domain</span>
              </div>

              <p className="text-[11px] text-slate-300 leading-relaxed bg-slate-900/60 p-2.5 rounded border border-slate-800/60">
                SAR acquisition confirmed slick footprint near vessel transit corridor. 1 AIS match identified (<span className="text-emerald-400 font-semibold">MV OCEAN TRADER</span>) alongside 1 dark vessel anomaly (<span className="text-amber-400 font-semibold">UNMATCHED-SAR-001</span>). PyGNOME drift trajectory models movement east-northeast over +48h toward 2 sensitive marine protected areas.
              </p>

              <div className="space-y-1.5 pt-1 text-[11px]">
                <div className="flex items-center justify-between text-slate-400 border-b border-slate-800/40 pb-1">
                  <span>SAR Scene:</span>
                  <span className="font-mono text-slate-200">Sentinel-1A GRD</span>
                </div>
                <div className="flex items-center justify-between text-slate-400 border-b border-slate-800/40 pb-1">
                  <span>Vessel Detections:</span>
                  <span className="font-mono text-emerald-400 font-semibold">1 Match / 1 Anomaly</span>
                </div>
                <div className="flex items-center justify-between text-slate-400 border-b border-slate-800/40 pb-1">
                  <span>Drift Horizons:</span>
                  <div className="flex items-center gap-1 font-mono text-[10px]">
                    {[6, 12, 24, 48].map((h) => (
                      <button
                        key={h}
                        type="button"
                        onClick={() => selectForecastHorizon(h)}
                        className={`px-1.5 py-0.5 rounded border transition-colors cursor-pointer ${
                          selectedForecast?.activeTimestep?.horizon_hours === h
                            ? 'bg-blue-600 text-white border-blue-400 font-bold'
                            : 'bg-slate-900 text-blue-300 border-blue-800/60 hover:bg-slate-800'
                        }`}
                      >
                        +{h}h
                      </button>
                    ))}
                  </div>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Threatened Assets:</span>
                  <span className="font-mono text-red-400 font-bold">2 Sensitive Areas (Critical)</span>
                </div>
              </div>
            </Panel>

            {/* 3. Person 1 Canonical Source Investigation Panel */}
            {investigationResult && (
              <Panel className="shrink-0 space-y-2 border border-cyan-800/60 bg-slate-950/80">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-cyan-400">
                    <FileSearch className="w-4 h-4" />
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Source Attribution</h3>
                  </div>
                  <Badge className="bg-amber-950 text-amber-400 border-amber-800/60 text-[9px] font-mono uppercase">
                    {investigationResult.attribution_status}
                  </Badge>
                </div>

                <div className="text-[10px] text-slate-400">
                  Reason: <span className="font-mono text-slate-200">{investigationResult.unknown_trigger_reason || 'N/A'}</span>
                </div>

                {investigationResult.evaluated_candidates?.map(cand => (
                  <div key={cand.candidate_id} className="p-2 rounded bg-slate-900 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
                      <span>{cand.hypothesis_label}: {cand.candidate_entity?.vessel_name || cand.candidate_id}</span>
                      <span className="text-[10px] text-emerald-400 font-mono">{cand.component_scores.spatial} / 100</span>
                    </div>
                    {cand.supporting_evidence?.map((ev, i) => (
                      <div key={i} className="text-[10px] text-emerald-400/90 flex items-center gap-1">
                        <span>+</span> <span>{ev.summary}</span>
                      </div>
                    ))}
                    {cand.contradictory_evidence?.map((ev, i) => (
                      <div key={i} className="text-[10px] text-red-400/90 flex items-center gap-1">
                        <span>-</span> <span>{ev.summary}</span>
                      </div>
                    ))}
                  </div>
                ))}

                <div className="text-[9px] text-slate-400 leading-tight bg-slate-900/90 p-2 rounded border border-slate-800 italic">
                  {investigationResult.non_guilt_clause}
                </div>
              </Panel>
            )}

            {/* 4. Investigation Actions & Domain Selection */}
            <Panel className="shrink-0 space-y-2">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-cyan-400" />
                <span>Investigation Actions</span>
              </div>
              <div className="grid grid-cols-2 gap-1.5 text-xs">
                <button
                  type="button"
                  onClick={() => focusDomain('sar')}
                  className="p-2 rounded bg-slate-900 border border-slate-800 hover:border-cyan-500/60 active:scale-95 text-slate-200 font-medium flex items-center justify-between transition-all cursor-pointer"
                >
                  <span className="text-[11px] text-cyan-400 font-semibold">View SAR</span>
                  <span className="text-[10px] text-slate-500 font-mono">Domain 1</span>
                </button>

                <button
                  type="button"
                  onClick={() => focusDomain('vessels')}
                  className="p-2 rounded bg-slate-900 border border-slate-800 hover:border-emerald-500/60 active:scale-95 text-slate-200 font-medium flex items-center justify-between transition-all cursor-pointer"
                >
                  <span className="text-[11px] text-emerald-400 font-semibold">View Vessels</span>
                  <span className="text-[10px] text-slate-500 font-mono">Domain 2</span>
                </button>

                <button
                  type="button"
                  onClick={() => focusDomain('forecast')}
                  className="p-2 rounded bg-slate-900 border border-slate-800 hover:border-blue-500/60 active:scale-95 text-slate-200 font-medium flex items-center justify-between transition-all cursor-pointer"
                >
                  <span className="text-[11px] text-blue-400 font-semibold">View Forecast</span>
                  <span className="text-[10px] text-slate-500 font-mono">Domain 3</span>
                </button>

                <button
                  type="button"
                  onClick={() => focusDomain('threat')}
                  className="p-2 rounded bg-slate-900 border border-slate-800 hover:border-amber-500/60 active:scale-95 text-slate-200 font-medium flex items-center justify-between transition-all cursor-pointer"
                >
                  <span className="text-[11px] text-amber-400 font-semibold">View Threat</span>
                  <span className="text-[10px] text-slate-500 font-mono">Domain 4</span>
                </button>

                <button
                  type="button"
                  onClick={clearAllSelections}
                  className="col-span-2 p-1.5 rounded bg-slate-900/80 border border-slate-800 hover:border-red-500/60 active:scale-95 text-slate-400 hover:text-slate-200 text-center text-[11px] font-medium transition-all cursor-pointer"
                >
                  Clear Current Selection
                </button>
              </div>
            </Panel>

            {/* 5. Source & Provenance */}
            <Panel className="shrink-0">
              <PanelHeader title="Source & Provenance" />
              <div className="flex items-start gap-3 mt-2">
                <Database className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                <div>
                  <div className="text-xs text-slate-300">Sentinel-1 GRD & AIS Data Stream</div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    Data Mode: <span className="font-mono text-cyan-400">{spillDetection?.provenance?.training_dataset?.dataset_version_id ? 'SYNTHETIC_DEVELOPMENT_FIXTURE' : 'MOCK_HYBRID'}</span>
                  </div>
                </div>
              </div>
            </Panel>
          </>
        ) : (
          <Panel>
            <div className="text-sm text-slate-400">Incident not found</div>
          </Panel>
        )}
      </div>
    </MapWorkspace>
  );
};
