import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  AlertTriangle,
  Map,
  Ship,
  FileSearch,
  CloudRain,
  ShieldAlert,
  FileText,
  Play,
  Settings,
} from 'lucide-react';
import { cn } from '../lib/utils';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { path: '/dashboard', label: 'Command Center', icon: <LayoutDashboard className="w-4 h-4" /> },
  { path: '/incidents', label: 'Incidents', icon: <AlertTriangle className="w-4 h-4" /> },
  { path: '/map', label: 'Map', icon: <Map className="w-4 h-4" /> },
  { path: '/vessels', label: 'Vessels', icon: <Ship className="w-4 h-4" /> },
  { path: '/evidence', label: 'Evidence', icon: <FileSearch className="w-4 h-4" /> },
  { path: '/forecast', label: 'Forecast', icon: <CloudRain className="w-4 h-4" /> },
  { path: '/threats', label: 'Threats', icon: <ShieldAlert className="w-4 h-4" /> },
  { path: '/reports', label: 'Reports', icon: <FileText className="w-4 h-4" /> },
  { path: '/replay', label: 'Replay', icon: <Play className="w-4 h-4" /> },
];

const bottomNavItems: NavItem[] = [
  { path: '/settings', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();

  const renderLink = (item: NavItem) => {
    const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
    return (
      <NavLink
        key={item.path}
        to={item.path}
        className={cn(
          'flex items-center gap-2.5 px-3 py-2 rounded text-xs font-medium transition-colors duration-150',
          isActive
            ? 'bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-400 -ml-px'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
        )}
      >
        {item.icon}
        <span className="hidden lg:inline">{item.label}</span>
      </NavLink>
    );
  };

  return (
    <aside className="flex flex-col w-12 lg:w-48 bg-slate-950/80 border-r border-slate-800/70 shrink-0 z-10">
      <nav className="flex-1 flex flex-col gap-0.5 p-2 pt-3 overflow-y-auto">
        {navItems.map(renderLink)}
      </nav>
      <div className="border-t border-slate-800/70 p-2">
        {bottomNavItems.map(renderLink)}
      </div>
    </aside>
  );
};
