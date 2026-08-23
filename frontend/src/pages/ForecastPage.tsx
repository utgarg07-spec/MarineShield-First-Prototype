import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { CloudRain, AlertTriangle } from 'lucide-react';
import { api } from '../api';
import type { Forecast } from '../api/types/forecast';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData } from '../api/types/vessel';
import type { ThreatAssessment } from '../api/types/threat';
import { Panel, PanelHeader, Badge } from '../components/ui';
import { LoadingState } from '../components/feedback/LoadingState';

export const ForecastPage: React.FC = () => {
  const { setSelectedForecast } = useOutletContext<{
    setSelectedSar: (sar: SARSceneMetadata | null) => void;
    setSelectedVessel: (vessel: SelectedVesselData | null) => void;
    setSelectedForecast: (forecast: Forecast | null) => void;
    setSelectedThreat: (threat: ThreatAssessment | null) => void;
  }>();

  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const incidentId = 'MS-PHASE6-DEV-001';
    api.getForecast(incidentId, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then((res) => setForecast(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <CloudRain className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold text-slate-100">Oil Spill Forecasting Workspace</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Hydrodynamic Ensemble Trajectory Simulation & Forecast Timesteps
          </p>
        </div>
        <Badge className="bg-blue-950 text-blue-400 border-blue-800/60 font-mono text-xs">
          MOCK_HYBRID
        </Badge>
      </div>

      {loading ? (
        <LoadingState message="Loading forecast data..." />
      ) : forecast ? (
        <div className="space-y-6">
          <Panel className="space-y-3">
            <PanelHeader title="Forecast Engine & Initialization" />
            <div
              onClick={() => setSelectedForecast(forecast)}
              className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-blue-500/60 transition-all cursor-pointer space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-200">
                  {forecast.provenance?.forecast_engine || 'PyGNOME Engine'} ({forecast.forecast_id.slice(0, 8)})
                </span>
                <Badge className="bg-blue-950 text-blue-300 border-blue-800/60 text-[10px] uppercase">
                  STATUS: {forecast.status}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300">
                <div>Reference Time: {new Date(forecast.forecast_reference_time).toLocaleString()}</div>
                <div>Status Msg: {forecast.status_message}</div>
              </div>

              <div className="space-y-1 pt-2 border-t border-slate-800">
                <div className="text-[10px] uppercase font-bold text-slate-400">Available Horizons</div>
                <div className="flex gap-2">
                  {forecast.available_horizons_hours?.map((h) => (
                    <span key={h} className="px-2 py-0.5 rounded bg-blue-950/80 border border-blue-800/60 text-blue-300 font-mono text-xs font-bold">
                      +{h}h
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Panel>

          <div className="p-3.5 rounded bg-amber-950/20 border border-amber-800/40 text-xs text-amber-300 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              <div className="font-bold">Contract Limitation Notice</div>
              <div>Authoritative Person 3 PyGNOME forecast contract remains unapproved. This display presents bounded development mock objects only.</div>
            </div>
          </div>
        </div>
      ) : (
        <Panel><div className="text-sm text-slate-400">No forecast data available</div></Panel>
      )}
    </div>
  );
};
