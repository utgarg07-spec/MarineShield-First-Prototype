import { useState, useEffect, useCallback } from 'react';
import { ChevronUp, ChevronDown, Clock, X } from 'lucide-react';
import { cn } from '../lib/utils';
import { IconButton } from '../components/ui/IconButton';

interface BottomTimelineProps {
  expanded: boolean;
  onToggle: () => void;
}

export const BottomTimeline: React.FC<BottomTimelineProps> = ({ expanded, onToggle }) => {
  const [isMobileOverlay, setIsMobileOverlay] = useState(false);

  const checkBreakpoint = useCallback(() => {
    setIsMobileOverlay(window.innerWidth < 1024);
  }, []);

  useEffect(() => {
    checkBreakpoint();
    window.addEventListener('resize', checkBreakpoint);
    return () => window.removeEventListener('resize', checkBreakpoint);
  }, [checkBreakpoint]);

  // Mobile overlay mode (< 1024px)
  if (isMobileOverlay) {
    return (
      <>
        {/* Collapsed strip - always visible */}
        <div className="h-8 bg-slate-950/90 border-t border-slate-800/70 flex items-center justify-between px-4 shrink-0 z-10">
          <div className="flex items-center gap-2">
            <Clock className="w-3 h-3 text-slate-600" />
            <span className="text-[10px] uppercase tracking-wider text-slate-600 font-semibold">Intelligence Timeline</span>
          </div>
          <IconButton label="Open timeline" size="sm" onClick={onToggle}>
            <ChevronUp />
          </IconButton>
        </div>

        {/* Overlay drawer for mobile */}
        {expanded && (
          <>
            <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-30" onClick={onToggle} />
            <div className="fixed bottom-0 left-0 right-0 h-64 bg-slate-950 border-t border-slate-800/70 z-40 flex flex-col">
              <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800/70">
                <div className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-cyan-500" />
                  <span className="text-xs uppercase tracking-wider text-slate-300 font-semibold">Intelligence Timeline</span>
                </div>
                <IconButton label="Close timeline" size="sm" onClick={onToggle}>
                  <X />
                </IconButton>
              </div>
              <div className="flex-1 flex flex-col items-center justify-center px-6 text-center">
                <p className="text-sm font-medium text-slate-400 mb-1">Timeline unavailable</p>
                <p className="text-xs text-slate-600">
                  No authoritative timeline events have been provided.
                </p>
              </div>
            </div>
          </>
        )}
      </>
    );
  }

  // Desktop mode — inline collapsible
  return (
    <div
      className={cn(
        'bg-slate-950/90 border-t border-slate-800/70 shrink-0 z-10 transition-all duration-200',
        expanded ? 'h-44' : 'h-8'
      )}
    >
      {/* Header strip */}
      <div className="flex items-center justify-between px-4 h-8">
        <div className="flex items-center gap-2">
          <Clock className={cn('w-3 h-3', expanded ? 'text-cyan-500' : 'text-slate-600')} />
          <span
            className={cn(
              'text-[10px] uppercase tracking-wider font-semibold',
              expanded ? 'text-slate-300' : 'text-slate-600'
            )}
          >
            Intelligence Timeline
          </span>
        </div>
        <IconButton label={expanded ? 'Collapse timeline' : 'Expand timeline'} size="sm" onClick={onToggle}>
          {expanded ? <ChevronDown /> : <ChevronUp />}
        </IconButton>
      </div>

      {expanded && (
        <div className="flex flex-col items-center justify-center h-36 px-6 text-center">
          <p className="text-sm font-medium text-slate-400 mb-1">Timeline unavailable</p>
          <p className="text-xs text-slate-600 max-w-md">
            No authoritative timeline events have been provided.
          </p>
        </div>
      )}
    </div>
  );
};
