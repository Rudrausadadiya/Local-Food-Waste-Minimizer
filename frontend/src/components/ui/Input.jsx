import React from 'react';
import { cn } from '../../lib/utils';

export const Input = React.forwardRef(
  ({ label, error, hint, prefixIcon, suffixIcon, className, id, ...props }, ref) => {
    const inputId = id ?? `input-${Math.random().toString(36).slice(2)}`;
    const errorId = `${inputId}-error`;
    const hintId = `${inputId}-hint`;

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-slate-700 dark:text-slate-300">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {prefixIcon && (
            <span className="absolute left-3 text-slate-400 pointer-events-none">{prefixIcon}</span>
          )}
          <input
            ref={ref}
            id={inputId}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : hint ? hintId : undefined}
            className={cn(
              'w-full rounded-lg border bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-slate-100',
              'placeholder:text-slate-400 transition-colors duration-150',
              'focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              error
                ? 'border-red-400 focus:ring-red-500 focus:border-red-500'
                : 'border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600',
              prefixIcon && 'pl-9',
              suffixIcon && 'pr-9',
              className
            )}
            {...props}
          />
          {suffixIcon && (
            <span className="absolute right-3 text-slate-400 pointer-events-none">{suffixIcon}</span>
          )}
        </div>
        {error && (
          <p id={errorId} className="text-xs text-red-500 flex items-center gap-1">
            {error}
          </p>
        )}
        {hint && !error && (
          <p id={hintId} className="text-xs text-slate-500 dark:text-slate-400">
            {hint}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';

export const PasswordInput = React.forwardRef((props, ref) => {
  const [show, setShow] = React.useState(false);
  return (
    <Input
      ref={ref}
      type={show ? 'text' : 'password'}
      suffixIcon={
        <button
          type="button"
          className="pointer-events-auto text-slate-400 hover:text-slate-600"
          onClick={() => setShow((s) => !s)}
          aria-label={show ? 'Hide password' : 'Show password'}
        >
          {show ? (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
          )}
        </button>
      }
      {...props}
    />
  );
});
PasswordInput.displayName = 'PasswordInput';
