import type { ReactNode } from 'react';
import { MapContainer } from '../map/MapContainer';
import type { Incident } from '../api/types/incident';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';
import type { SpillDetectionResponse } from '../api/types/oil_intelligence';
import type { InvestigationResult } from '../api/types/investigation';
import type { MapTarget } from '../context/AppContext';
import { X, Crosshair, Navigation, FileText, ShieldAlert } from 'lucide-react';

interface MapWorkspaceProps {
  children?: ReactNode;
  incident?: Incident | null;
  spillDetection?: SpillDetectionResponse | null;
  investigationResult?: InvestigationResult | null;
  selectedSar?: SARSceneMetadata | null;
  selectedVessel?: SelectedVesselData | null;
  selectedForecast?: Forecast | null;
  selectedThreat?: ThreatAssessment | null;
  onSarSelect?: (sar: SARSceneMetadata | null) => void;
  onVesselSelect?: (vessel: SelectedVesselData | null) => void;
  onForecastSelect?: (forecast: Forecast | null) => void;
  onThreatSelect?: (threat: ThreatAssessment | null) => void;
  onClearSelection?: () => void;
  mapTarget?: MapTarget | null;
}

export const MapWorkspace: React.FC<MapWorkspaceProps> = ({
  children,
  incident,
  spillDetection,
  investigationResult,
  selectedSar,
  selectedVessel,
  selectedForecast,
  selectedThreat,
  onSarSelect,
  onVesselSelect,
  onForecastSelect,
  onThreatSelect,
  onClearSelection,
  mapTarget,
}) => {
  const hasSelection = Boolean(selectedSar || selectedVessel || selectedForecast || selectedThreat);

  return (
    <div className="relative flex-1 min-h-0 min-w-0">
      <MapContainer
        className="absolute inset-0"
        incident={incident}
        spillDetection={spillDetection}
        investigationResult={investigationResult}
        selectedSar={selectedSar}
        selectedVessel={selectedVessel}
        selectedForecast={selectedForecast}
        selectedThreat={selectedThreat}
        onSarSelect={onSarSelect}
        onVesselSelect={onVesselSelect}
        onForecastSelect={onForecastSelect}
        onThreatSelect={onThreatSelect}
        mapTarget={mapTarget}
      />

      {/* Selected Intelligence Banner */}
      {hasSelection && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 pointer-events-auto">
          <div className="bg-slate-950/95 backdrop-blur-md border border-cyan-500/60 rounded-xl px-4 py-2 shadow-2xl flex items-center gap-3">
            <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs">
              {selectedVessel && <Navigation className="w-4 h-4 text-emerald-400" />}
              {selectedSar && <Crosshair className="w-4 h-4 text-indigo-400" />}
              {selectedForecast && <FileText className="w-4 h-4 text-blue-400" />}
              {selectedThreat && <ShieldAlert className="w-4 h-4 text-amber-400" />}
              <span className="uppercase tracking-wider">
                Selected Intelligence:
              </span>
            </div>

            <div className="text-xs font-mono font-semibold text-slate-100 max-w-[200px] truncate">
              {selectedVessel && (selectedVessel.vessel_name || selectedVessel.id)}
              {selectedSar && (selectedSar.scene_identifier.granule_id.slice(0, 16) + '...')}
              {selectedForecast && (
                selectedForecast.activeTimestep
                  ? `Forecast (+${selectedForecast.activeTimestep.horizon_hours}h)`
                  : `Forecast ${selectedForecast.forecast_id.slice(0, 8)}`
              )}
              {selectedThreat && (`Threat ${selectedThreat.summary?.overall_threat_level || 'HIGH'}`)}
            </div>

            <button
              type="button"
              onClick={onClearSelection}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors cursor-pointer"
              title="Clear Current Selection"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {children && (
        <div className="absolute inset-0 pointer-events-none [&>*]:pointer-events-auto">
          {children}
        </div>
      )}
    </div>
  );
};
