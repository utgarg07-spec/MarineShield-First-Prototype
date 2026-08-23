import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';
import { RightInspector } from './RightInspector';
import { BottomTimeline } from './BottomTimeline';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';

export const AppShell: React.FC = () => {
  const [timelineExpanded, setTimelineExpanded] = useState(false);
  const [selectedSar, setSelectedSar] = useState<SARSceneMetadata | null>(null);
  const [selectedVessel, setSelectedVessel] = useState<SelectedVesselData | null>(null);
  const [selectedForecast, setSelectedForecast] = useState<Forecast | null>(null);
  const [selectedThreat, setSelectedThreat] = useState<ThreatAssessment | null>(null);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[var(--color-marine-navy-dark)]">
      {/* Top bar */}
      <TopBar />

      {/* Main body: sidebar + center + inspector */}
      <div className="flex flex-1 min-h-0">
        {/* Sidebar */}
        <Sidebar />

        {/* Center workspace: content + bottom timeline */}
        <div className="flex flex-col flex-1 min-h-0 min-w-0">
          {/* Page content area */}
          <div className="flex-1 min-h-0 flex flex-col">
            <Outlet context={{ selectedSar, setSelectedSar, selectedVessel, setSelectedVessel, selectedForecast, setSelectedForecast, selectedThreat, setSelectedThreat }} />
          </div>

          {/* Bottom timeline */}
          <BottomTimeline
            expanded={timelineExpanded}
            onToggle={() => setTimelineExpanded((prev) => !prev)}
          />
        </div>

        {/* Right inspector */}
        <RightInspector selectedSar={selectedSar} selectedVessel={selectedVessel} selectedForecast={selectedForecast} selectedThreat={selectedThreat} />
      </div>
    </div>
  );
};
