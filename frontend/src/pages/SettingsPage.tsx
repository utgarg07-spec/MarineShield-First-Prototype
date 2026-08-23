import React, { useEffect, useState } from 'react';
import { Settings, RefreshCw, Monitor, Database, Layers, CheckCircle2 } from 'lucide-react';
import { Panel, PanelHeader, Badge } from '../components/ui';

export const SettingsPage: React.FC = () => {
  const [mapLabelsEnabled, setMapLabelsEnabled] = useState<boolean>(() => {
    return localStorage.getItem('ms_map_labels') !== 'false';
  });

  const [compactViewEnabled, setCompactViewEnabled] = useState<boolean>(() => {
    return localStorage.getItem('ms_compact_view') === 'true';
  });

  const [resetConfirmed, setResetConfirmed] = useState(false);

  useEffect(() => {
    localStorage.setItem('ms_map_labels', mapLabelsEnabled ? 'true' : 'false');
  }, [mapLabelsEnabled]);

  useEffect(() => {
    localStorage.setItem('ms_compact_view', compactViewEnabled ? 'true' : 'false');
  }, [compactViewEnabled]);

  const handleReset = () => {
    localStorage.removeItem('ms_map_labels');
    localStorage.removeItem('ms_compact_view');
    setMapLabelsEnabled(true);
    setCompactViewEnabled(false);
    setResetConfirmed(true);
    setTimeout(() => setResetConfirmed(false), 3000);
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-cyan-400" />
            <h1 className="text-xl font-bold text-slate-100">System & Prototype Settings</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Configure local UI demonstration preferences and review subsystem integration status
          </p>
        </div>
        <Badge className="bg-cyan-950 text-cyan-400 border-cyan-800/60 font-mono text-xs">
          SYNTHETIC_DEVELOPMENT_FIXTURE
        </Badge>
      </div>

      <div className="space-y-6">
        {/* Demonstration Data Mode Status */}
        <Panel className="space-y-3">
          <PanelHeader title="Demonstration Environment & Data Mode" />
          <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-200">Active Data Mode</span>
              <span className="text-xs font-mono font-bold text-cyan-400 px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800/60">
                SYNTHETIC_DEVELOPMENT_FIXTURE / MOCK_HYBRID
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              All displayed telemetry, SAR footprints, vessel matches, and investigation candidate scores originate from approved, deterministic phase fixtures. Live API requests are unmounted.
            </p>

            <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <Database className="w-4 h-4 text-slate-400" />
                <span>Backend Connection Mode</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-slate-500">Live API Disabled (501 Preserved)</span>
                <button
                  type="button"
                  disabled
                  className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-500 text-xs font-semibold cursor-not-allowed"
                  title="Live FastAPI backend is unmounted / returning HTTP 501 Not Implemented"
                >
                  Mock Fixture Mode
                </button>
              </div>
            </div>
          </div>
        </Panel>

        {/* Local UI Preferences */}
        <Panel className="space-y-4">
          <PanelHeader title="User Interface Preferences" />
          <div className="space-y-3">
            {/* Map Labels Toggle */}
            <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-200 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  <span>WebGIS Vessel & SAR Map Labels</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  Toggle on-map text overlays for vessels and SAR detections
                </div>
              </div>
              <button
                type="button"
                onClick={() => setMapLabelsEnabled(!mapLabelsEnabled)}
                className={`px-3 py-1 rounded text-xs font-bold font-mono transition-all cursor-pointer ${
                  mapLabelsEnabled
                    ? 'bg-cyan-950 text-cyan-300 border border-cyan-800/80'
                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                }`}
              >
                {mapLabelsEnabled ? 'ENABLED' : 'DISABLED'}
              </button>
            </div>

            {/* Compact View Toggle */}
            <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-200 flex items-center gap-2">
                  <Monitor className="w-4 h-4 text-emerald-400" />
                  <span>Compact Panel Density</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">
                  Reduce padding and font scaling across intelligence inspectors
                </div>
              </div>
              <button
                type="button"
                onClick={() => setCompactViewEnabled(!compactViewEnabled)}
                className={`px-3 py-1 rounded text-xs font-bold font-mono transition-all cursor-pointer ${
                  compactViewEnabled
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/80'
                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                }`}
              >
                {compactViewEnabled ? 'ENABLED' : 'DISABLED'}
              </button>
            </div>

            {/* Reset Preferences Button */}
            <div className="pt-2 flex items-center justify-between">
              <button
                type="button"
                onClick={handleReset}
                className="px-3.5 py-1.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition-all cursor-pointer flex items-center gap-2"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reset UI Preferences</span>
              </button>

              {resetConfirmed && (
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Preferences Reset to Default</span>
                </span>
              )}
            </div>
          </div>
        </Panel>

        {/* Subsystem Integration Status */}
        <Panel className="space-y-3">
          <PanelHeader title="Subsystem Integration Status Dashboard" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded bg-slate-900/90 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">Person 1 Oil Intelligence</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                  AUTHORITATIVE
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Segmentation, look-alike rejection, evidence engine complete.</p>
            </div>

            <div className="p-3 rounded bg-slate-900/90 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">Person 2 SAR & Vessels</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                  AUTHORITATIVE
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Sentinel-1 granule ingestion & AIS-SAR matching complete.</p>
            </div>

            <div className="p-3 rounded bg-slate-900/90 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">Person 3 PyGNOME Forecast</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/60">
                  UNAPPROVED
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Forecast contract unapproved; returning 501 / mock fallback.</p>
            </div>

            <div className="p-3 rounded bg-slate-900/90 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">Person 3 Threat Assessment</span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800/60">
                  UNAPPROVED
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Threat contract unapproved; returning 501 / mock fallback.</p>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
};
