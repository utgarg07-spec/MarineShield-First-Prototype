import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapWorkspace } from '../layouts/MapWorkspace';
import { Panel, PanelHeader, Badge } from '../components/ui';
import {
  AlertTriangle,
  Ship,
  ShieldAlert,
  CloudRain,
  FileSearch,
  Radar,
  ArrowRight,
  Activity,
  Anchor,
  Clock,
} from 'lucide-react';
import { api } from '../api';
import type { Incident } from '../api/types/incident';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);

  useEffect(() => {
    api.getIncidents()
      .then((res) => setIncidents(res.data))
      .catch(console.error);
  }, []);

  const activeIncident = incidents[0];

  return (
    <MapWorkspace>
      <div className="absolute top-4 left-4 max-w-4xl z-10 pointer-events-auto space-y-4">
        {/* Command Center Overview Header Strip */}
        <Panel className="!bg-slate-950/90 backdrop-blur shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <PanelHeader title="Command Center Operational Overview" />
              <p className="text-[11px] text-slate-400 mt-0.5">
                Real-Time Spill Intelligence & Multi-Subsystem Incident Status
              </p>
            </div>
            <Badge className="bg-amber-950 text-amber-400 border-amber-800/60 font-mono text-xs">
              SYNTHETIC_DEVELOPMENT_FIXTURE
            </Badge>
          </div>
        </Panel>

        {/* Module Status Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <button
            type="button"
            onClick={() => navigate('/incidents')}
            className="bg-slate-950/90 backdrop-blur border border-slate-800/80 hover:border-cyan-500/60 rounded-lg p-3 text-left transition-all cursor-pointer space-y-1 shadow-lg"
          >
            <div className="flex items-center gap-1.5 text-cyan-400 font-bold text-xs">
              <AlertTriangle className="w-4 h-4" />
              <span>Incidents</span>
            </div>
            <div className="text-lg font-bold text-slate-100 tabular-nums">1 Active</div>
            <div className="text-[10px] text-slate-400">Phase 5A Ready</div>
          </button>

          <button
            type="button"
            onClick={() => navigate('/vessels')}
            className="bg-slate-950/90 backdrop-blur border border-slate-800/80 hover:border-emerald-500/60 rounded-lg p-3 text-left transition-all cursor-pointer space-y-1 shadow-lg"
          >
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-xs">
              <Ship className="w-4 h-4" />
              <span>Vessel Tracks</span>
            </div>
            <div className="text-lg font-bold text-slate-100 tabular-nums">2 Matched</div>
            <div className="text-[10px] text-slate-400">Person 2 AIS/SAR</div>
          </button>

          <button
            type="button"
            onClick={() => navigate('/evidence')}
            className="bg-slate-950/90 backdrop-blur border border-slate-800/80 hover:border-cyan-500/60 rounded-lg p-3 text-left transition-all cursor-pointer space-y-1 shadow-lg"
          >
            <div className="flex items-center gap-1.5 text-cyan-400 font-bold text-xs">
              <FileSearch className="w-4 h-4" />
              <span>Evidence</span>
            </div>
            <div className="text-lg font-bold text-slate-100 tabular-nums">1 Run</div>
            <div className="text-[10px] text-slate-400">Person 1 Engine</div>
          </button>

          <button
            type="button"
            onClick={() => navigate('/map')}
            className="bg-slate-950/90 backdrop-blur border border-slate-800/80 hover:border-indigo-500/60 rounded-lg p-3 text-left transition-all cursor-pointer space-y-1 shadow-lg"
          >
            <div className="flex items-center gap-1.5 text-indigo-400 font-bold text-xs">
              <Radar className="w-4 h-4" />
              <span>SAR Coverage</span>
            </div>
            <div className="text-lg font-bold text-slate-100 tabular-nums">Sentinel-1</div>
            <div className="text-[10px] text-slate-400">Footprint Active</div>
          </button>

          <button
            type="button"
            onClick={() => navigate('/forecast')}
            className="bg-slate-950/90 backdrop-blur border border-slate-800/80 hover:border-blue-500/60 rounded-lg p-3 text-left transition-all cursor-pointer space-y-1 shadow-lg"
          >
            <div className="flex items-center gap-1.5 text-blue-400 font-bold text-xs">
              <CloudRain className="w-4 h-4" />
              <span>Forecast</span>
            </div>
            <div className="text-lg font-bold text-slate-100 tabular-nums">+48h</div>
            <div className="text-[10px] text-amber-400">Mock Hybrid</div>
          </button>

          <button
            type="button"
            onClick={() => navigate('/threats')}
            className="bg-slate-950/90 backdrop-blur border border-slate-800/80 hover:border-amber-500/60 rounded-lg p-3 text-left transition-all cursor-pointer space-y-1 shadow-lg"
          >
            <div className="flex items-center gap-1.5 text-amber-400 font-bold text-xs">
              <ShieldAlert className="w-4 h-4" />
              <span>Threats</span>
            </div>
            <div className="text-lg font-bold text-slate-100 tabular-nums">HIGH</div>
            <div className="text-[10px] text-amber-400">Mock Hybrid</div>
          </button>
        </div>

        {/* Active Incident Summary Card */}
        {activeIncident && (
          <Panel className="!bg-slate-950/90 backdrop-blur space-y-3 shadow-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs">
                <Activity className="w-4 h-4" />
                <span className="uppercase tracking-wider">Active Incident Briefing</span>
              </div>
              <button
                type="button"
                onClick={() => navigate(`/incidents/${activeIncident.id}`)}
                className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1 cursor-pointer"
              >
                <span>Inspect Incident</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-slate-100">{activeIncident.title}</span>
                <Badge className="bg-emerald-950 text-emerald-400 border-emerald-800/60 font-mono text-[10px]">
                  {activeIncident.reference}
                </Badge>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300 font-mono pt-1">
                <div className="flex items-center gap-1.5">
                  <Anchor className="w-3.5 h-3.5 text-slate-500" />
                  <span>Location: [{activeIncident.location?.geometry?.coordinates?.[0] ?? 73.2}, {activeIncident.location?.geometry?.coordinates?.[1] ?? 18.5}]</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-slate-500" />
                  <span>Reported: {new Date(activeIncident.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </Panel>
        )}
      </div>
    </MapWorkspace>
  );
};
