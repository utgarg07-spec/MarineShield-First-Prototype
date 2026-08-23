import React from 'react';
import { FileText, AlertTriangle } from 'lucide-react';
import { Panel, PanelHeader, Badge } from '../components/ui';

export const ReportsPage: React.FC = () => {
  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <h1 className="text-xl font-bold text-slate-100">Incident Reports & Export Workspace</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative Incident Briefings & Legal Evidence Dossier Generator
          </p>
        </div>
        <Badge className="bg-indigo-950 text-indigo-400 border-indigo-800/60 font-mono text-xs">
          DEVELOPMENT / AWAITING CONTRACT
        </Badge>
      </div>

      <Panel className="space-y-4">
        <PanelHeader title="Incident Summary Dossier (MS-PHASE6-DEV-001)" />
        <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-slate-200">Incident Investigation Report #MS-PHASE6-DEV-001</span>
            <span className="text-xs text-slate-400 font-mono">Date: 2024-01-20</span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded border border-slate-800/80">
            SAR acquisition confirmed slick footprint near vessel transit corridor in Strait of Malacca. Candidate hypotheses evaluated with non-guilt spatio-temporal evidence scoring. Release reconstruction polygon computed.
          </p>

          <div className="p-3 rounded bg-amber-950/20 border border-amber-800/40 text-xs text-amber-300 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              <div className="font-bold">Prototype Demonstration View</div>
              <div>No authoritative PDF export backend has been provisioned. Report generation algorithms execute in fixture-backed demonstration mode.</div>
            </div>
          </div>
        </div>
      </Panel>
    </div>
  );
};
