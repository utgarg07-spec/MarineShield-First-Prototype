import type { ReactNode } from 'react';
import { Badge } from '../components/ui';

interface Props {
  title: string;
  subtitle?: string;
  description?: string;
  icon?: ReactNode;
}

export const PlaceholderPage: React.FC<Props> = ({ title, subtitle, description, icon }) => {
  return (
    <div className="flex flex-col items-center justify-center flex-1 min-h-0 p-6 text-center">
      {icon && (
        <div className="w-14 h-14 rounded-xl bg-slate-800/60 border border-slate-700/50 flex items-center justify-center mb-5">
          {icon}
        </div>
      )}
      <h1 className="text-lg font-semibold text-slate-200 mb-2">{title}</h1>
      {subtitle && (
        <Badge variant="warning" className="mb-4">{subtitle}</Badge>
      )}
      {description && (
        <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
};
