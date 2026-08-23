import { cn } from '../../lib/utils';

interface ProgressBarProps {
  value: number; // 0-100
  variant?: 'default' | 'success' | 'warning' | 'danger';
  className?: string;
}

const barColors: Record<string, string> = {
  default: 'bg-cyan-500',
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  danger: 'bg-red-500',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({ value, variant = 'default', className }) => {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className={cn('w-full h-1.5 bg-slate-800 rounded-full overflow-hidden', className)}>
      <div
        className={cn('h-full rounded-full transition-all duration-300', barColors[variant])}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
};
