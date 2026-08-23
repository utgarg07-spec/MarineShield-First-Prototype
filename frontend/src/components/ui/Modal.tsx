import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { IconButton } from './IconButton';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  className?: string;
}

export const Modal: React.FC<ModalProps> = ({ open, onClose, title, children, className }) => {
  useEffect(() => {
    if (!open) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div
        className={cn(
          'relative z-10 w-full max-w-lg bg-slate-900 border border-slate-700/50 rounded-lg shadow-2xl',
          className
        )}
      >
        {title && (
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-700/50">
            <h2 className="text-sm font-semibold text-slate-200">{title}</h2>
            <IconButton label="Close modal" onClick={onClose}>
              <X />
            </IconButton>
          </div>
        )}
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
};
