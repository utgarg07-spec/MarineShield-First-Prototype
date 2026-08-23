import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { IncidentSummary } from '../api/types/incident';
import { Panel, PanelHeader, Badge } from '../components/ui';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { EmptyState } from '../components/feedback/EmptyState';
import { Search, Database, Clock, Anchor, Activity } from 'lucide-react';

const renderDate = (dateStr?: string) => {
  if (!dateStr || dateStr === 'Not provided') return 'Date unavailable';
  const d = new Date(dateStr);
  return isNaN(d.getTime()) ? 'Date unavailable' : d.toLocaleDateString();
};

export const IncidentListPage: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const loadIncidents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getIncidents(searchQuery);
      setIncidents(response.data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load incidents'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      loadIncidents();
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const handleIncidentClick = (id: string) => {
    navigate(`/incidents/${id}`);
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4 overflow-y-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-xl font-bold tracking-tight">Incidents</h1>
        
        <div className="relative w-full sm:w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-slate-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-md text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500"
            placeholder="Search incidents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="flex-1 min-h-0">
        {loading ? (
          <LoadingState message="Loading incidents..." />
        ) : error ? (
          <ErrorState message={error.message} onRetry={loadIncidents} />
        ) : incidents.length === 0 ? (
          <EmptyState title="No Incidents Found" message="No incidents match your search criteria." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {incidents.map((incident) => (
              <Panel key={incident.id} className="flex flex-col cursor-pointer hover:border-cyan-500/50 transition-colors" noPadding>
                <div onClick={() => handleIncidentClick(incident.id)} className="p-4 flex-1 flex flex-col">
                  <PanelHeader title={incident.reference}>
                    <Badge variant="warning">AWAITING CONTRACT</Badge>
                  </PanelHeader>

                  <div className="flex-1 space-y-3 mt-4">
                    <div className="flex items-start gap-2">
                      <Anchor className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                      <div>
                        <div className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Location</div>
                        <div className="text-sm text-slate-200">
                          {incident.location?.source_ref ? `Source Ref: ${incident.location.source_ref}` : 'Location unavailable'}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <Database className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                      <div>
                        <div className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Source</div>
                        <div className="text-sm text-slate-200">{incident.provenance?.created_from || 'Source unavailable'}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-2">
                      <Activity className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                      <div>
                        <div className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Status</div>
                        <div className="text-sm text-slate-200">{incident.status_label || incident.status}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center mt-6 pt-3 border-t border-slate-800/50">
                    <div className="flex flex-col">
                      <span className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Severity</span>
                      <span className="text-xs text-slate-400">{incident.severity?.class || 'Not provided'}</span>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] uppercase text-slate-500 font-semibold tracking-wider">Date</span>
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {renderDate(incident.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
              </Panel>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
