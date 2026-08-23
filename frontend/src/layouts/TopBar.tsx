import { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, Shield, ChevronDown, BellOff, LogOut, CheckCheck, X, Compass, Ship, FileSearch } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { IconButton } from '../components/ui/IconButton';
import { useApp } from '../context/AppContext';
import { mockIncidents } from '../mocks/fixtures/incidents';
import { mockAISObservations, mockVesselMetadataMap, mockSARDetections, mockUnmatchedDetections } from '../mocks/fixtures/vessels';

interface SearchResultItem {
  id: string;
  category: 'INCIDENT' | 'VESSEL' | 'COORDINATE';
  title: string;
  subtitle: string;
  action: () => void;
}

export const TopBar: React.FC = () => {
  const navigate = useNavigate();
  const {
    user,
    logout,
    notifications,
    unreadCount,
    markAllAsRead,
    clearNotifications,
    flyToCoordinate,
  } = useApp();

  const [utc, setUtc] = useState('');
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setUtc(
        now.toISOString().slice(0, 19).replace('T', ' ') + ' UTC'
      );
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, []);

  // Global keyboard shortcuts (⌘K or / to focus search)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        setSearchOpen(true);
      } else if (e.key === 'Escape') {
        setSearchOpen(false);
        setNotifOpen(false);
        setProfileOpen(false);
        inputRef.current?.blur();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Click-outside listener for dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setNotifOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Parse coordinate input format (Lat, Lon or Lon, Lat)
  const parseCoordinates = (query: string): { lat: number; lon: number } | null => {
    const trimmed = query.trim();
    const parts = trimmed.split(/[\s,]+/);
    if (parts.length !== 2) return null;
    const n1 = parseFloat(parts[0]);
    const n2 = parseFloat(parts[1]);
    if (isNaN(n1) || isNaN(n2)) return null;

    // Check Case A: n1 is Lat [-90, 90], n2 is Lon [-180, 180]
    if (n1 >= -90 && n1 <= 90 && n2 >= -180 && n2 <= 180) {
      return { lat: n1, lon: n2 };
    }
    // Check Case B: n1 is Lon [-180, 180], n2 is Lat [-90, 90]
    if (n1 >= -180 && n1 <= 180 && n2 >= -90 && n2 <= 90) {
      return { lat: n2, lon: n1 };
    }
    return null;
  };

  // Perform search matching across Incidents, Vessels, and Coordinates
  const searchResults = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return [];

    const items: SearchResultItem[] = [];

    // 1. INCIDENTS SEARCH
    mockIncidents.forEach((inc) => {
      const matchId = inc.id.toLowerCase().includes(q);
      const matchRef = inc.reference.toLowerCase().includes(q);
      const matchStatus = inc.status.toLowerCase().includes(q);
      const matchSource = inc.provenance.created_from.toLowerCase().includes(q);

      if (matchId || matchRef || matchStatus || matchSource) {
        const coordsStr = inc.location.geometry?.coordinates
          ? `Coords: [${inc.location.geometry.coordinates.join(', ')}]`
          : `CRS: ${inc.location.crs}`;
        items.push({
          id: `inc-${inc.id}`,
          category: 'INCIDENT',
          title: inc.reference,
          subtitle: `Status: ${inc.status} | Source: ${inc.provenance.created_from} | ${coordsStr}`,
          action: () => {
            navigate(`/incidents/${inc.id}`);
            setSearchOpen(false);
          },
        });
      }
    });

    // 2. VESSEL / AIS SEARCH
    // AIS Observations
    mockAISObservations.forEach((obs) => {
      const meta = mockVesselMetadataMap[obs.mmsi];
      const matchMmsi = obs.mmsi.toString().includes(q);
      const matchName = meta?.vessel_name?.toLowerCase().includes(q);
      const matchType = meta?.ship_type?.toLowerCase().includes(q);

      if (matchMmsi || matchName || matchType) {
        const vName = meta?.vessel_name || `Vessel MMSI ${obs.mmsi}`;
        const itemKey = `vessel-ais-${obs.observation_id}`;
        if (!items.some((i) => i.id === itemKey)) {
          items.push({
            id: itemKey,
            category: 'VESSEL',
            title: `${vName} (MMSI: ${obs.mmsi})`,
            subtitle: `Status: ${obs.navigational_status} | Speed: ${obs.speed_over_ground_knots} kts | Coords: [${obs.longitude}, ${obs.latitude}]`,
            action: () => {
              flyToCoordinate(obs.latitude, obs.longitude, 12);
              navigate('/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da');
              setSearchOpen(false);
            },
          });
        }
      }
    });

    // SAR Detections
    mockSARDetections.forEach((det) => {
      const matchDet = det.detection_id.toLowerCase().includes(q);
      if (matchDet) {
        items.push({
          id: `vessel-sar-${det.detection_id}`,
          category: 'VESSEL',
          title: `SAR Detection (${det.detection_id})`,
          subtitle: `Length: ${det.estimated_length_meters}m | Confidence: ${(det.detection_confidence * 100).toFixed(0)}% | Coords: [${det.centroid_lon}, ${det.centroid_lat}]`,
          action: () => {
            flyToCoordinate(det.centroid_lat, det.centroid_lon, 12);
            navigate('/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da');
            setSearchOpen(false);
          },
        });
      }
    });

    // Unmatched Vessels
    mockUnmatchedDetections.forEach((unm) => {
      const matchUnm = unm.unmatched_id.toLowerCase().includes(q);
      if (matchUnm) {
        items.push({
          id: `vessel-unm-${unm.unmatched_id}`,
          category: 'VESSEL',
          title: `Unmatched Dark Vessel (${unm.unmatched_id})`,
          subtitle: `Length: ${unm.estimated_length_meters}m | ${unm.description || 'Unmatched AIS'} | Coords: [${unm.centroid_lon}, ${unm.centroid_lat}]`,
          action: () => {
            flyToCoordinate(unm.centroid_lat, unm.centroid_lon, 12);
            navigate('/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da');
            setSearchOpen(false);
          },
        });
      }
    });

    // 3. COORDINATE SEARCH
    const parsedCoords = parseCoordinates(q);
    if (parsedCoords) {
      items.push({
        id: `coord-${parsedCoords.lat}-${parsedCoords.lon}`,
        category: 'COORDINATE',
        title: `${parsedCoords.lat.toFixed(4)}°N, ${parsedCoords.lon.toFixed(4)}°E`,
        subtitle: `Navigate map camera to coordinates [Lon: ${parsedCoords.lon}, Lat: ${parsedCoords.lat}]`,
        action: () => {
          flyToCoordinate(parsedCoords.lat, parsedCoords.lon, 9);
          setSearchOpen(false);
        },
      });
    }

    return items;
  }, [searchQuery, flyToCoordinate, navigate]);

  // Group search results by category
  const groupedResults = useMemo(() => {
    const incidents = searchResults.filter((i) => i.category === 'INCIDENT');
    const vessels = searchResults.filter((i) => i.category === 'VESSEL');
    const coordinates = searchResults.filter((i) => i.category === 'COORDINATE');
    return { incidents, vessels, coordinates };
  }, [searchResults]);

  const handleKeyDownSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchResults.length > 0) {
      e.preventDefault();
      searchResults[0].action();
    }
  };

  const handleToggleNotif = () => {
    if (!notifOpen) {
      markAllAsRead();
    }
    setNotifOpen((prev) => !prev);
    setProfileOpen(false);
    setSearchOpen(false);
  };

  const handleToggleProfile = () => {
    setProfileOpen((prev) => !prev);
    setNotifOpen(false);
    setSearchOpen(false);
  };

  const handleLogout = () => {
    logout();
    setProfileOpen(false);
    navigate('/');
  };

  const userInitial = user ? user.userName.slice(0, 2).toUpperCase() : 'OP';

  return (
    <header className="flex items-center justify-between h-11 px-4 bg-slate-950/90 border-b border-slate-800/70 backdrop-blur-sm shrink-0 z-20">
      {/* Left: Identity & Clickable Logo Navigation */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 cursor-pointer hover:opacity-85 active:scale-98 transition-all group border-0 bg-transparent p-0"
          title="Return to Command Center Overview"
        >
          <Shield className="w-4 h-4 text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(6,182,212,0.6)] transition-all" />
          <span className="text-sm font-bold tracking-wider text-white group-hover:text-cyan-300 transition-colors">
            MARINESHIELD
          </span>
        </button>
        <div className="h-4 w-px bg-slate-700" />
        <StatusBadge status="online" label="Operational" />
      </div>

      {/* Center: Interactive Global Search Component */}
      <div className="flex-1 max-w-xl mx-6 relative" ref={searchRef}>
        <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-700/50 rounded px-3 py-1 text-sm text-slate-300 hover:border-slate-600 focus-within:border-cyan-500/70 transition-colors cursor-text">
          <Search className="w-3.5 h-3.5 shrink-0 text-slate-400" />
          <input
            ref={inputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setSearchOpen(true);
            }}
            onFocus={() => setSearchOpen(true)}
            onKeyDown={handleKeyDownSearch}
            placeholder="Search incidents, vessels, coordinates…"
            className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          {searchQuery ? (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="text-slate-500 hover:text-slate-300 p-0.5"
            >
              <X className="w-3 h-3" />
            </button>
          ) : (
            <kbd className="ml-auto text-[10px] bg-slate-800 border border-slate-700 rounded px-1 py-0.5 text-slate-500 font-mono">
              ⌘K
            </kbd>
          )}
        </div>

        {/* Global Search Dropdown Results */}
        {searchOpen && searchQuery.trim().length > 0 && (
          <div className="absolute left-0 right-0 top-full mt-2 bg-slate-950/95 border border-slate-800 rounded-lg shadow-2xl z-50 overflow-hidden backdrop-blur-md max-h-96 overflow-y-auto">
            {searchResults.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-400">
                No matching incidents, vessels, or coordinates
              </div>
            ) : (
              <div className="divide-y divide-slate-800/60 p-1.5">
                {/* INCIDENTS SECTION */}
                {groupedResults.incidents.length > 0 && (
                  <div className="py-1">
                    <div className="px-2.5 py-1 text-[9px] font-mono font-bold tracking-wider text-cyan-400 uppercase flex items-center gap-1.5">
                      <FileSearch className="w-3 h-3" />
                      INCIDENT
                    </div>
                    {groupedResults.incidents.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={item.action}
                        className="w-full text-left px-2.5 py-1.5 rounded hover:bg-slate-900/80 transition-colors cursor-pointer group block"
                      >
                        <div className="text-xs font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors">
                          {item.title}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate mt-0.5">
                          {item.subtitle}
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* VESSELS SECTION */}
                {groupedResults.vessels.length > 0 && (
                  <div className="py-1">
                    <div className="px-2.5 py-1 text-[9px] font-mono font-bold tracking-wider text-emerald-400 uppercase flex items-center gap-1.5">
                      <Ship className="w-3 h-3" />
                      VESSEL
                    </div>
                    {groupedResults.vessels.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={item.action}
                        className="w-full text-left px-2.5 py-1.5 rounded hover:bg-slate-900/80 transition-colors cursor-pointer group block"
                      >
                        <div className="text-xs font-semibold text-slate-100 group-hover:text-emerald-300 transition-colors">
                          {item.title}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate mt-0.5">
                          {item.subtitle}
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* COORDINATES SECTION */}
                {groupedResults.coordinates.length > 0 && (
                  <div className="py-1">
                    <div className="px-2.5 py-1 text-[9px] font-mono font-bold tracking-wider text-amber-400 uppercase flex items-center gap-1.5">
                      <Compass className="w-3 h-3" />
                      COORDINATE
                    </div>
                    {groupedResults.coordinates.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={item.action}
                        className="w-full text-left px-2.5 py-1.5 rounded hover:bg-slate-900/80 transition-colors cursor-pointer group block"
                      >
                        <div className="text-xs font-semibold text-slate-100 group-hover:text-amber-300 transition-colors">
                          {item.title}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate mt-0.5">
                          {item.subtitle}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right: Status / Clock / Notifications / Operator Dropdown */}
      <div className="flex items-center gap-3">
        <span className="text-[11px] font-mono text-slate-400 tabular-nums">{utc}</span>
        <div className="h-4 w-px bg-slate-700" />

        {/* Notification Bell + Dropdown */}
        <div className="relative" ref={notifRef}>
          <IconButton
            label="Notifications"
            onClick={handleToggleNotif}
            className="relative"
          >
            <Bell />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500 ring-2 ring-slate-950 animate-pulse" />
            )}
          </IconButton>

          {notifOpen && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-slate-950/95 border border-slate-800 rounded-lg shadow-2xl z-50 overflow-hidden backdrop-blur-md max-h-[calc(100vh-4rem)] flex flex-col">
              <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-slate-800/80 bg-slate-900/80 shrink-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-100 uppercase tracking-wider">
                    Notifications
                  </span>
                  {unreadCount > 0 && (
                    <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-red-950 text-red-400 border border-red-800">
                      {unreadCount} NEW
                    </span>
                  )}
                </div>
                {notifications.length > 0 && (
                  <button
                    type="button"
                    onClick={clearNotifications}
                    className="text-[10px] text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <CheckCheck className="w-3 h-3 text-slate-500" />
                    <span>Clear all</span>
                  </button>
                )}
              </div>

              <div className="max-h-72 overflow-y-auto divide-y divide-slate-800/60 flex-1">
                {notifications.length === 0 ? (
                  <div className="p-5 text-center space-y-1.5">
                    <BellOff className="w-6 h-6 text-slate-600 mx-auto mb-1" />
                    <div className="text-xs font-semibold text-slate-300">No new notifications</div>
                    <div className="text-[10px] text-slate-500 leading-relaxed">
                      No intelligence requiring attention.
                    </div>
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`p-3 transition-colors space-y-1 ${
                        !n.read ? 'bg-slate-900/70 border-l-2 border-l-cyan-400' : 'hover:bg-slate-900/30'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-semibold text-slate-100 flex items-center gap-1.5">
                          <span
                            className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                              n.type === 'warning'
                                ? 'bg-amber-400 shadow-sm shadow-amber-400/80'
                                : n.type === 'error'
                                ? 'bg-red-500 shadow-sm shadow-red-500/80'
                                : 'bg-cyan-400 shadow-sm shadow-cyan-400/80'
                            }`}
                          />
                          {n.title}
                        </span>
                        <span className="text-[9px] font-mono text-slate-500 shrink-0">
                          {new Date(n.createdAt).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300 leading-snug pl-3">{n.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="h-4 w-px bg-slate-700" />

        {/* User Profile Dropdown & Logout */}
        <div className="relative" ref={profileRef}>
          <button
            type="button"
            onClick={handleToggleProfile}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
          >
            <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-semibold text-cyan-400">
              {userInitial}
            </div>
            <span className="hidden xl:inline">{user ? user.userName : 'Operator'}</span>
            <ChevronDown className="w-3 h-3" />
          </button>

          {profileOpen && (
            <div className="absolute right-0 top-full mt-2 w-60 bg-slate-950/95 border border-slate-800 rounded-lg shadow-2xl z-50 p-3 space-y-3 backdrop-blur-md">
              <div className="flex items-center gap-3 border-b border-slate-800/80 pb-2.5">
                <div className="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-800/80 flex items-center justify-center text-xs font-bold text-cyan-400">
                  {userInitial}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-bold text-slate-100 truncate">
                    {user ? user.userName : 'Operator'}
                  </div>
                  <div className="text-[10px] font-mono text-cyan-400">
                    ID: {user ? user.userId : 'OP-8492'}
                  </div>
                  <div className="text-[10px] text-slate-500 truncate">
                    {user ? user.role : 'Command Operator'}
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <button
                  type="button"
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded hover:bg-red-950/40 text-red-400 hover:text-red-300 text-xs font-medium transition-colors cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};


