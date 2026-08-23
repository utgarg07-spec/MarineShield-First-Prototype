import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { FileSearch, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../api';
import type { SARSceneMetadata } from '../api/types/sar';
import type { InvestigationResult } from '../api/types/investigation';
import type { SelectedVesselData } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';
import { Panel, PanelHeader, Badge } from '../components/ui';
import { LoadingState } from '../components/feedback/LoadingState';

export const EvidencePage: React.FC = () => {
  const { setSelectedSar } = useOutletContext<{
    setSelectedSar: (sar: SARSceneMetadata | null) => void;
    setSelectedVessel: (vessel: SelectedVesselData | null) => void;
    setSelectedForecast: (forecast: Forecast | null) => void;
    setSelectedThreat: (threat: ThreatAssessment | null) => void;
  }>();

  const [sarScenes, setSarScenes] = useState<SARSceneMetadata[]>([]);
  const [investigationResult, setInvestigationResult] = useState<InvestigationResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const incidentId = 'MS-PHASE6-DEV-001';
    Promise.all([
      api.getSARScenes(incidentId),
      api.reconstructRelease({ incident_id: incidentId, t_observation_utc: '2024-01-20T00:55:41Z', spill_centroid_lon_lat: [73.2015, 18.5012] }),
    ])
      .then(([sarRes, reconRes]) => {
        setSarScenes(sarRes.data);
        setInvestigationResult(reconRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <FileSearch className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl font-bold text-slate-100">Evidence & SAR Imagery</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative Person 1 Evidence + Contradiction Engine & SAR Acquisition
          </p>
        </div>
        <Badge className="bg-cyan-950 text-cyan-400 border-cyan-800/60 font-mono text-xs">
          SYNTHETIC_DEVELOPMENT_FIXTURE
        </Badge>
      </div>

      {loading ? (
        <LoadingState message="Loading evidence and SAR metadata..." />
      ) : (
        <div className="space-y-6">
          {/* SAR Imagery Metadata Panel */}
          <Panel className="space-y-3">
            <PanelHeader title="Sentinel-1 SAR Acquisition" />
            {sarScenes.map((scene) => (
              <div
                key={scene.scene_identifier.granule_id}
                onClick={() => setSelectedSar(scene)}
                className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-cyan-500/60 transition-all cursor-pointer space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-200">{scene.scene_identifier.mission} GRD Scene</span>
                  <Badge className="bg-cyan-950 text-cyan-300 border-cyan-800/60 text-[10px] font-mono">
                    FOOTPRINT EPSG:4326
                  </Badge>
                </div>
                <div className="text-xs text-slate-400 font-mono truncate" title={scene.scene_identifier.granule_id}>
                  Granule: {scene.scene_identifier.granule_id}
                </div>
              </div>
            ))}
          </Panel>

          {/* Person 1 Candidate Evidence Panel */}
          {investigationResult && (
            <Panel className="space-y-3">
              <PanelHeader title="Evaluated Source Hypotheses & Evidence" />
              <div className="space-y-3">
                {investigationResult.evaluated_candidates?.map((cand) => (
                  <div key={cand.candidate_id} className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-200">{cand.hypothesis_label}: {cand.candidate_entity?.vessel_name || cand.candidate_id}</span>
                      <Badge className="bg-emerald-950 text-emerald-400 border-emerald-800/60 font-mono text-xs">
                        Spatial Score: {cand.component_scores.spatial} / 100
                      </Badge>
                    </div>

                    {/* Supporting Evidence */}
                    <div className="space-y-1 pt-1">
                      <div className="text-[10px] uppercase font-bold text-emerald-400">Supporting Evidence</div>
                      {cand.supporting_evidence?.map((ev, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs text-emerald-300">
                          <CheckCircle className="w-3.5 h-3.5 shrink-0" />
                          <span>{ev.summary}</span>
                        </div>
                      ))}
                    </div>

                    {/* Contradictory Evidence */}
                    <div className="space-y-1 pt-1 border-t border-slate-800/60">
                      <div className="text-[10px] uppercase font-bold text-red-400">Contradictory Evidence</div>
                      {cand.contradictory_evidence?.map((ev, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs text-red-300">
                          <XCircle className="w-3.5 h-3.5 shrink-0" />
                          <span>{ev.summary}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Legal Non-Guilt Disclaimer */}
              <div className="p-3 rounded bg-slate-900/90 border border-slate-800 text-xs text-slate-300 italic">
                {investigationResult.non_guilt_clause}
              </div>
            </Panel>
          )}
        </div>
      )}
    </div>
  );
};
