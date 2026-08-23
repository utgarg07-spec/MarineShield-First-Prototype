import React from 'react';
import { PackageOpen } from 'lucide-react';

interface Props {
  title?: string;
  message?: string;
}

export const EmptyState: React.FC<Props> = ({ 
  title = 'No Data Available', 
  message = 'There is currently no data to display in this view.' 
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-gray-400 w-full h-full text-center">
      <PackageOpen className="w-12 h-12 mb-4 opacity-50" />
      <h3 className="text-lg font-medium text-gray-300 mb-1">{title}</h3>
      <p className="text-sm max-w-sm">{message}</p>
    </div>
  );
};
