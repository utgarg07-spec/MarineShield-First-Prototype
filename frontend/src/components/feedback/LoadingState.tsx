import React from 'react';
import { Loader2 } from 'lucide-react';

interface Props {
  message?: string;
  fullScreen?: boolean;
}

export const LoadingState: React.FC<Props> = ({ message = 'Loading...', fullScreen = false }) => {
  const containerClass = fullScreen 
    ? "flex flex-col items-center justify-center min-h-screen bg-[var(--color-marine-navy-dark)] text-[var(--color-marine-cyan)]"
    : "flex flex-col items-center justify-center p-8 text-[var(--color-marine-cyan)] w-full h-full";

  return (
    <div className={containerClass}>
      <Loader2 className="w-8 h-8 animate-spin mb-4" />
      <p className="text-sm font-medium tracking-wider uppercase">{message}</p>
    </div>
  );
};
