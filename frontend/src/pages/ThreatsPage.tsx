import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { ShieldAlert, AlertTriangle } from 'lucide-react';
import { api } from '../api';
import type { ThreatAssessment } from '../api/types/threat';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import { Panel, PanelHeader, Badge } from '../components/ui';
import { LoadingState } from '../components/feedback/LoadingState';

export const ThreatsPage: React.FC = () => {
  const { setSelectedThreat } = useOutletContext<{
    setSelectedSar: (sar: SARSceneMetadata | null) => void;
    setSelectedVessel: (vessel: SelectedVesselData | null) => void;
    setSelectedForecast: (forecast: Forecast | null) => void;
    setSelectedThreat: (threat: ThreatAssessment | null) => void;
  }>();

  const [threat, setThreat] = useState<ThreatAssessment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const incidentId = 'MS-PHASE6-DEV-001';
    api.getThreatAssessment(incidentId, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then((res) => setThreat(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-500" />
            <h1 className="text-xl font-bold text-slate-100">Threat Assessment & Asset Exposure</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Marine Shield Response Priority & Ecological Exposure Risk Assessment
          </p>
        </div>
        <Badge className="bg-amber-950 text-amber-400 border-amber-800/60 font-mono text-xs">
          MOCK_HYBRID
        </Badge>
      </div>

      {loading ? (
        <LoadingState message="Loading threat assessment data..." />
      ) : threat ? (
        <div className="space-y-6">
          <Panel className="space-y-3">
            <PanelHeader title="Threat Summary & Sensitivity Intersections" />
            <div
              onClick={() => setSelectedThreat(threat)}
              className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-amber-500/60 transition-all cursor-pointer space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-200">
                  Overall Threat Level: {threat.summary?.overall_threat_level || 'HIGH'}
                </span>
                <Badge className="bg-amber-950 text-amber-300 border-amber-800/60 text-[10px] uppercase">
                  STATUS: {threat.status}
                </Badge>
              </div>

              {threat.summary?.highest_threat_asset_id && (
                <div className="text-xs text-slate-300 font-mono">
                  Highest Threat Asset ID: <span className="font-semibold text-slate-100">{threat.summary.highest_threat_asset_id}</span>
                </div>
              )}
            </div>
          </Panel>

          <div className="p-3.5 rounded bg-amber-950/20 border border-amber-800/40 text-xs text-amber-300 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              <div className="font-bold">Contract Limitation Notice</div>
              <div>Authoritative Person 3 threat assessment contract remains unapproved. This display presents development mock objects only.</div>
            </div>
          </div>
        </div>
      ) : (
        <Panel><div className="text-sm text-slate-400">No threat assessment data available</div></Panel>
      )}
    </div>
  );
};
