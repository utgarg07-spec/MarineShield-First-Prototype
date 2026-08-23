import { useState } from 'react';
import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface TooltipProps {
  content: string;
  children: ReactNode;
  side?: 'top' | 'bottom' | 'left' | 'right';
}

export const Tooltip: React.FC<TooltipProps> = ({ content, children, side = 'top' }) => {
  const [visible, setVisible] = useState(false);

  const positionClasses: Record<string, string> = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-1.5',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-1.5',
    left: 'right-full top-1/2 -translate-y-1/2 mr-1.5',
    right: 'left-full top-1/2 -translate-y-1/2 ml-1.5',
  };

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      <div
        className={cn(
          'absolute z-50 px-2 py-1 text-[10px] font-medium text-white bg-slate-800 border border-slate-700 rounded shadow-lg whitespace-nowrap',
          'transition-opacity duration-150',
          visible ? 'opacity-100' : 'opacity-0 pointer-events-none',
          positionClasses[side]
        )}
      >
        {content}
      </div>
    </div>
  );
};
