import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

type BadgeVariant = 'default' | 'info' | 'success' | 'warning' | 'danger' | 'cyan';

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-slate-700/60 text-slate-300 border-slate-600/40',
  info: 'bg-blue-900/40 text-blue-300 border-blue-700/40',
  success: 'bg-emerald-900/40 text-emerald-300 border-emerald-700/40',
  warning: 'bg-amber-900/40 text-amber-300 border-amber-700/40',
  danger: 'bg-red-900/40 text-red-300 border-red-700/40',
  cyan: 'bg-cyan-900/40 text-cyan-300 border-cyan-700/40',
};

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', children, className }) => {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded border',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
};
