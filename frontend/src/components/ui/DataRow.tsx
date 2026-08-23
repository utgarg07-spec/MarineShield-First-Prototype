import type { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface DataRowProps {
  label: string;
  value?: ReactNode;
  className?: string;
}

export const DataRow: React.FC<DataRowProps> = ({ label, value, className }) => {
  return (
    <div className={cn('flex items-center justify-between py-1.5 border-b border-slate-800/50 last:border-0', className)}>
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-xs text-slate-200 font-medium">{value ?? '—'}</span>
    </div>
  );
};
