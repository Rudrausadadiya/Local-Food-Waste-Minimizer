import React from 'react';
import { cn } from '../../lib/utils';

const variants = {
  primary: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm dark:bg-emerald-500 dark:hover:bg-emerald-600',
  secondary: 'bg-slate-100 hover:bg-slate-200 text-slate-900 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-100',
  ngo: 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm',
  destructive: 'bg-red-600 hover:bg-red-700 text-white shadow-sm',
  outline: 'border border-slate-300 hover:bg-slate-50 text-slate-700 dark:border-slate-700 dark:hover:bg-slate-800 dark:text-slate-300',
  ghost: 'hover:bg-slate-100 text-slate-700 dark:hover:bg-slate-800 dark:text-slate-300',
};

const sizes = {
  xs: 'h-7 px-2.5 text-xs gap-1',
  sm: 'h-8 px-3 text-sm gap-1.5',
  md: 'h-9 px-4 text-sm gap-2',
  lg: 'h-10 px-5 text-base gap-2',
};

export const Button = React.forwardRef((
  { variant = 'primary', size = 'md', loading, leftIcon, rightIcon, children, className, disabled, ...props },
  ref
) => {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      aria-busy={loading}
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2',
        'active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : (
        leftIcon
      )}
      {children}
      {!loading && rightIcon}
    </button>
  );
});

Button.displayName = 'Button';
