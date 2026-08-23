import { cn } from '../../lib/utils';

interface MetricProps {
  label: string;
  value: string;
  unit?: string;
  className?: string;
}

export const Metric: React.FC<MetricProps> = ({ label, value, unit, className }) => {
  return (
    <div className={cn('flex flex-col gap-0.5', className)}>
      <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">{label}</span>
      <div className="flex items-baseline gap-1">
        <span className="text-lg font-semibold text-slate-100 tabular-nums">{value}</span>
        {unit && <span className="text-xs text-slate-500">{unit}</span>}
      </div>
    </div>
  );
};
