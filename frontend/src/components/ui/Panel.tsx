import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface PanelProps {
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const Panel: React.FC<PanelProps> = ({ children, className, noPadding = false }) => {
  return (
    <div
      className={cn(
        'bg-slate-900/70 border border-slate-700/50 rounded-lg backdrop-blur-sm',
        !noPadding && 'p-4',
        className
      )}
    >
      {children}
    </div>
  );
};
