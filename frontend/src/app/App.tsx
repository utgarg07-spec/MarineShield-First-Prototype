import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from '../components/feedback/ErrorBoundary';
import { AppProvider } from '../context/AppContext';
import { AppShell } from '../layouts/AppShell';
import { LandingPage } from '../pages/LandingPage';
import { DashboardPage } from '../pages/DashboardPage';
import { IncidentListPage } from '../pages/IncidentListPage';
import { IncidentDetailPage } from '../pages/IncidentDetailPage';
import { MapPage } from '../pages/MapPage';
import { VesselsPage } from '../pages/VesselsPage';
import { EvidencePage } from '../pages/EvidencePage';
import { ForecastPage } from '../pages/ForecastPage';
import { ThreatsPage } from '../pages/ThreatsPage';
import { ReportsPage } from '../pages/ReportsPage';
import { ReplayPage } from '../pages/ReplayPage';
import { PlaceholderPage } from '../pages/PlaceholderPage';
import { LoginPage } from '../pages/LoginPage';
import { DesignSystemPage } from '../pages/DesignSystemPage';
import { SettingsPage } from '../pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AppProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/design-system" element={<DesignSystemPage />} />

            {/* Application shell routes */}
            <Route element={<AppShell />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/incidents" element={<IncidentListPage />} />
              <Route path="/incidents/:incidentId" element={<IncidentDetailPage />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/vessels" element={<VesselsPage />} />
              <Route path="/evidence" element={<EvidencePage />} />
              <Route path="/forecast" element={<ForecastPage />} />
              <Route path="/threats" element={<ThreatsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/replay" element={<ReplayPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>

            {/* Catch-all */}
            <Route
              path="*"
              element={
                <PlaceholderPage
                  title="404 — Page Not Found"
                  description="The requested page does not exist within the MarineShield platform."
                />
              }
            />
          </Routes>
        </BrowserRouter>
      </AppProvider>
    </ErrorBoundary>
  );
};
