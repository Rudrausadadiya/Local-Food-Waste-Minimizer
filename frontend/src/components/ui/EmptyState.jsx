import React from 'react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

// Component: EmptyState
export const EmptyState = ({ icon, title, description, action, className }) => (
  <div className={cn('flex flex-col items-center justify-center text-center py-16 px-8', className)}>
    <div className="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 dark:text-slate-500 mb-5">
      {icon}
    </div>
    <h3 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-2">{title}</h3>
    <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm mb-6">{description}</p>
    {action && (
      <Button variant={action.variant ?? 'primary'} onClick={action.onClick}>
        {action.label}
      </Button>
    )}
  </div>
);
