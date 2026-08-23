import { cn } from '../../lib/utils';

type StatusBadgeStatus = 'online' | 'offline' | 'warning' | 'danger' | 'unknown';

interface StatusBadgeProps {
  status: StatusBadgeStatus;
  label?: string;
  className?: string;
}

const statusConfig: Record<StatusBadgeStatus, { dot: string; text: string; defaultLabel: string }> = {
  online: { dot: 'bg-emerald-400', text: 'text-emerald-300', defaultLabel: 'Online' },
  offline: { dot: 'bg-slate-500', text: 'text-slate-400', defaultLabel: 'Offline' },
  warning: { dot: 'bg-amber-400', text: 'text-amber-300', defaultLabel: 'Warning' },
  danger: { dot: 'bg-red-400', text: 'text-red-300', defaultLabel: 'Danger' },
  unknown: { dot: 'bg-slate-500', text: 'text-slate-400', defaultLabel: 'Unknown' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, className }) => {
  const config = statusConfig[status];
  return (
    <span className={cn('inline-flex items-center gap-1.5 text-[11px] font-medium', config.text, className)}>
      <span className={cn('w-1.5 h-1.5 rounded-full', config.dot)} />
      {label ?? config.defaultLabel}
    </span>
  );
};
