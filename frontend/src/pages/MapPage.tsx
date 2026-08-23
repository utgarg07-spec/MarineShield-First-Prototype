import { useOutletContext } from 'react-router-dom';
import { MapWorkspace } from '../layouts/MapWorkspace';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';

export const MapPage: React.FC = () => {
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

  const handleClear = () => {
    setSelectedSar(null);
    setSelectedVessel(null);
    setSelectedForecast(null);
    setSelectedThreat(null);
  };

  return (
    <MapWorkspace
      selectedSar={selectedSar}
      selectedVessel={selectedVessel}
      selectedForecast={selectedForecast}
      selectedThreat={selectedThreat}
      onSarSelect={setSelectedSar}
      onVesselSelect={setSelectedVessel}
      onForecastSelect={setSelectedForecast}
      onThreatSelect={setSelectedThreat}
      onClearSelection={handleClear}
    />
  );
};
