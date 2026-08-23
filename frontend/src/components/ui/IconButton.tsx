import { forwardRef } from 'react';
import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/utils';

type IconButtonSize = 'sm' | 'md' | 'lg';

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  size?: IconButtonSize;
  children: ReactNode;
  label: string;
}

const sizeClasses: Record<IconButtonSize, string> = {
  sm: 'w-7 h-7 [&>svg]:w-3.5 [&>svg]:h-3.5',
  md: 'w-8 h-8 [&>svg]:w-4 [&>svg]:h-4',
  lg: 'w-10 h-10 [&>svg]:w-5 [&>svg]:h-5',
};

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ size = 'md', className, children, label, ...props }, ref) => {
    return (
      <button
        ref={ref}
        aria-label={label}
        title={label}
        className={cn(
          'inline-flex items-center justify-center rounded border border-transparent',
          'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50',
          'transition-colors duration-150',
          'focus:outline-none focus:ring-1 focus:ring-cyan-500/50',
          'disabled:opacity-40 disabled:cursor-not-allowed',
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

IconButton.displayName = 'IconButton';
