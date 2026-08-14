import React from 'react';
import { cn } from '../../lib/utils';

const variantClasses = {
  success: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
  warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  danger: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  info: 'bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-400',
  neutral: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400',
  ngo: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-400',
};

const dotColors = {
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  danger: 'bg-red-500',
  info: 'bg-sky-500',
  neutral: 'bg-slate-400',
  ngo: 'bg-indigo-500',
};

export const statusVariantMap = {
  PENDING: { variant: 'warning', label: 'Pending Approval' },
  APPROVED: { variant: 'success', label: 'Approved' },
  REJECTED: { variant: 'danger', label: 'Rejected' },
  SUSPENDED: { variant: 'danger', label: 'Suspended' },
  DRAFT: { variant: 'neutral', label: 'Draft' },
  PUBLISHED: { variant: 'success', label: 'Published' },
  PAUSED: { variant: 'warning', label: 'Paused' },
  UNPUBLISHED: { variant: 'danger', label: 'Taken Down' },
  CLOSED: { variant: 'neutral', label: 'Closed' },
  EXPIRED: { variant: 'danger', label: 'Expired' },
  COMPLETED: { variant: 'success', label: 'Completed' },
  CANCELLED: { variant: 'danger', label: 'Cancelled' },
  IN_STOCK: { variant: 'success', label: 'In Stock' },
  LOW_STOCK: { variant: 'warning', label: 'Low Stock' },
  OUT_OF_STOCK: { variant: 'neutral', label: 'Out of Stock' },
  EXPIRING_SOON: { variant: 'danger', label: 'Expiring Soon' },
  ACTIVE: { variant: 'success', label: 'Active' },
  INACTIVE: { variant: 'neutral', label: 'Inactive' },
};

// Component: Badge
export const Badge = ({ variant = 'neutral', label, dot, className }) => (
  <span
    className={cn(
      'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
      variantClasses[variant],
      className
    )}
  >
    {dot && <span className={cn('w-1.5 h-1.5 rounded-full', dotColors[variant])} />}
    {label}
  </span>
);

// Component: StatusBadge
export const StatusBadge = ({ status, className }) => {
  const config = statusVariantMap[status] ?? { variant: 'neutral', label: status };
  return <Badge variant={config.variant} label={config.label} dot className={className} />;
};
