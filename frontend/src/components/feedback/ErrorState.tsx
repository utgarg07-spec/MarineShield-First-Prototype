import React from 'react';
import { AlertCircle } from 'lucide-react';

interface Props {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<Props> = ({ 
  title = 'Error Loading Data', 
  message = 'An error occurred while fetching the requested information.',
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-[var(--color-marine-red)] w-full h-full text-center">
      <AlertCircle className="w-12 h-12 mb-4" />
      <h3 className="text-lg font-medium mb-1">{title}</h3>
      <p className="text-sm text-gray-400 max-w-sm mb-4">{message}</p>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="px-4 py-2 border border-[var(--color-marine-red)] rounded hover:bg-[var(--color-marine-red)] hover:text-white transition-colors text-sm"
        >
          Try Again
        </button>
      )}
    </div>
  );
};
