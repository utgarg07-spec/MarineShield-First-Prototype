import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface PanelHeaderProps {
  title: string;
  children?: ReactNode;
  className?: string;
}

export const PanelHeader: React.FC<PanelHeaderProps> = ({ title, children, className }) => {
  return (
    <div
      className={cn(
        'flex items-center justify-between pb-3 mb-3 border-b border-slate-700/50',
        className
      )}
    >
      <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</h3>
      {children && <div className="flex items-center gap-1">{children}</div>}
    </div>
  );
};
