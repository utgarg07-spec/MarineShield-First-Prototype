import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, ChevronDown, ChevronUp, Anchor, Radar, Ship, FileSearch, CloudRain, ShieldAlert, ListOrdered, FileText } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useApp } from '../context/AppContext';
import { RegisterModal } from '../components/auth/RegisterModal';
import { LoginModal } from '../components/auth/LoginModal';

const capabilities = [
  {
    icon: <Radar className="w-5 h-5 text-cyan-400" />,
    title: 'SAR Spill Detection',
    description: 'Automated detection of potential oil spills from Sentinel-1 Synthetic Aperture Radar imagery, leveraging dark-spot analysis on VV/VH channels.',
  },
  {
    icon: <Ship className="w-5 h-5 text-cyan-400" />,
    title: 'Vessel Intelligence',
    description: 'Correlation of AIS vessel tracking data with detected anomalies to identify potential sources of maritime pollution.',
  },
  {
    icon: <FileSearch className="w-5 h-5 text-cyan-400" />,
    title: 'Source Investigation',
    description: 'Systematic investigation workflow linking detected spills to nearby vessels using spatial-temporal analysis and evidence scoring.',
  },
  {
    icon: <Anchor className="w-5 h-5 text-cyan-400" />,
    title: 'Evidence & Verification',
    description: 'Multi-layer evidence collection combining SAR imagery, vessel tracks, environmental data, and optical confirmation for incident verification.',
  },
  {
    icon: <CloudRain className="w-5 h-5 text-cyan-400" />,
    title: 'Oil Spill Forecasting',
    description: 'Forward trajectory modeling of detected oil spills incorporating ocean current, wind, and weathering factors for response planning.',
  },
  {
    icon: <ShieldAlert className="w-5 h-5 text-cyan-400" />,
    title: 'Threat Assessment',
    description: 'Quantified environmental risk scoring based on spill characteristics, proximity to protected areas, and ecological sensitivity mapping.',
  },
  {
    icon: <ListOrdered className="w-5 h-5 text-cyan-400" />,
    title: 'Response Prioritization',
    description: 'Decision-support framework ranking incidents by severity, ecological impact, and response feasibility to optimize resource allocation.',
  },
  {
    icon: <FileText className="w-5 h-5 text-cyan-400" />,
    title: 'Incident Reporting',
    description: 'Structured incident report generation aggregating all detection, investigation, and assessment outputs into actionable intelligence reports.',
  },
];

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginDemo } = useApp();
  const [aboutOpen, setAboutOpen] = useState(false);

  const [registerOpen, setRegisterOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);

  const handleEnterClick = () => {
    setLoginOpen(false);
    setRegisterOpen(true);
  };

  const handleLoginClick = () => {
    setRegisterOpen(false);
    setLoginOpen(true);
  };

  const handleAuthSuccess = () => {
    setRegisterOpen(false);
    setLoginOpen(false);
    navigate('/dashboard');
  };

  const handleDemoMode = () => {
    loginDemo();
    setRegisterOpen(false);
    setLoginOpen(false);
    navigate('/dashboard');
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen bg-[var(--color-marine-navy-dark)] overflow-hidden">
      {/* Atmospheric background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950 via-slate-900/80 to-[#0a1628]" />
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-cyan-900/10 rounded-full blur-3xl" />
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0,229,255,0.3) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0,229,255,0.3) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
        />
        <div className="absolute bottom-[35%] left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-800/20 to-transparent" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center px-6 max-w-2xl">
        <div className="w-16 h-16 rounded-2xl bg-slate-800/50 border border-slate-700/50 flex items-center justify-center mb-8 backdrop-blur-sm">
          <Shield className="w-8 h-8 text-cyan-400" />
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-3">
          MARINE<span className="text-cyan-400">SHIELD</span>
        </h1>

        <p className="text-sm sm:text-base text-slate-400 font-medium tracking-widest uppercase mb-10">
          Maritime Intelligence Platform
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-3 mb-12">
          <Button size="lg" onClick={handleEnterClick}>
            Enter Command Center
          </Button>
          <Button variant="outline" size="lg" onClick={handleLoginClick}>
            Login
          </Button>
        </div>
      </div>

      {/* Modals */}
      <RegisterModal
        isOpen={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onSuccess={handleAuthSuccess}
        onSwitchToLogin={() => { setRegisterOpen(false); setLoginOpen(true); }}
        onDemoMode={handleDemoMode}
      />

      <LoginModal
        isOpen={loginOpen}
        onClose={() => setLoginOpen(false)}
        onSuccess={handleAuthSuccess}
        onSwitchToRegister={() => { setLoginOpen(false); setRegisterOpen(true); }}
        onDemoMode={handleDemoMode}
      />

      {/* Bottom information panel */}
      <div className="relative z-10 w-full max-w-4xl mx-auto px-6 mb-8">
        <div className="bg-slate-900/60 border border-slate-700/40 rounded-lg backdrop-blur-sm overflow-hidden">
          <button
            onClick={() => setAboutOpen(!aboutOpen)}
            className="flex items-center justify-between w-full px-5 py-3.5 text-left transition-colors hover:bg-slate-800/30 cursor-pointer"
          >
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              About MarineShield
            </span>
            {aboutOpen ? (
              <ChevronUp className="w-4 h-4 text-slate-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-500" />
            )}
          </button>

          {aboutOpen && (
            <div className="px-5 pb-5 border-t border-slate-800/50">
              <p className="text-xs text-slate-400 leading-relaxed mt-4 mb-6">
                MarineShield is an operational maritime intelligence and decision-support system. It integrates
                satellite-based spill detection, vessel tracking, environmental forecasting, and threat assessment
                into a unified command center for maritime environmental protection.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {capabilities.map((cap) => (
                  <div
                    key={cap.title}
                    className="flex gap-3 p-3 rounded border border-slate-800/50 bg-slate-900/40"
                  >
                    <div className="shrink-0 mt-0.5">{cap.icon}</div>
                    <div>
                      <h3 className="text-xs font-semibold text-slate-200 mb-1">{cap.title}</h3>
                      <p className="text-[11px] text-slate-500 leading-relaxed">{cap.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
