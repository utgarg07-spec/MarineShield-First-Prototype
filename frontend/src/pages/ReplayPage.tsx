import React from 'react';
import { Play, AlertTriangle } from 'lucide-react';
import { Panel, PanelHeader, Badge } from '../components/ui';

export const ReplayPage: React.FC = () => {
  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Play className="w-5 h-5 text-emerald-400" />
            <h1 className="text-xl font-bold text-slate-100">Historical Incident Time Machine</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic Historical Replay Engine with No-Future-Data Strict Temporal Slicing
          </p>
        </div>
        <Badge className="bg-emerald-950 text-emerald-400 border-emerald-800/60 font-mono text-xs">
          HISTORICAL_REPLAY
        </Badge>
      </div>

      <Panel className="space-y-4">
        <PanelHeader title="Temporal Slicing & Historical Playback (MS-PHASE6-DEV-001)" />
        <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-slate-200">Replay Observation Time: 2024-01-20T00:55:41Z</span>
            <span className="text-xs text-emerald-400 font-mono font-bold">t &lt;= t_observation ENFORCED</span>
          </div>

          <div className="p-3 rounded bg-slate-950/80 border border-slate-800 space-y-2">
            <div className="text-xs font-semibold text-slate-300">No-Future-Data Safeguard Rule</div>
            <p className="text-xs text-slate-400 leading-relaxed">
              In accordance with Person 1 scientific constraints, historical replay models strictly isolate telemetry up to the observation timestamp. No future AIS points or weather data leak into historic incident evaluation.
            </p>
          </div>

          <div className="p-3.5 rounded bg-amber-950/20 border border-amber-800/40 text-xs text-amber-300 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              <div className="font-bold">Prototype Demonstration View</div>
              <div>Authoritative replay timeline service is running in fixture-backed demonstration mode. Live playback controls are awaiting backend state mounting.</div>
            </div>
          </div>
        </div>
      </Panel>
    </div>
  );
};
