import React from 'react';
import { cn } from '../../lib/utils';

// Component: Skeleton
export const Skeleton = ({ className }) => (
  <div className={cn('animate-pulse rounded-md bg-slate-200 dark:bg-slate-800', className)} />
);

// Component: SkeletonText
export const SkeletonText = ({ lines = 3, className }) => (
  <div className={cn('space-y-2', className)}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton key={i} className={cn('h-3', i === lines - 1 ? 'w-3/4' : 'w-full')} />
    ))}
  </div>
);

// Component: SkeletonCardGrid
export const SkeletonCardGrid = ({ count = 6 }) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <Skeleton className="h-48 rounded-none" />
        <div className="p-4 space-y-3">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
          <div className="flex justify-between items-center pt-1">
            <Skeleton className="h-6 w-20" />
            <Skeleton className="h-8 w-24 rounded-lg" />
          </div>
        </div>
      </div>
    ))}
  </div>
);

// Component: SkeletonTable
export const SkeletonTable = ({ rows = 5, cols = 5 }) => (
  <div className="space-y-0 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
    <div
      className="grid gap-4 px-4 py-3 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800"
      style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
    >
      {Array.from({ length: cols }).map((_, i) => (
        <Skeleton key={i} className="h-3 w-3/4" />
      ))}
    </div>
    {Array.from({ length: rows }).map((_, ri) => (
      <div
        key={ri}
        className="grid gap-4 px-4 py-3.5 border-b last:border-b-0 border-slate-100 dark:border-slate-800"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
      >
        {Array.from({ length: cols }).map((_, ci) => (
          <Skeleton key={ci} className="h-3" />
        ))}
      </div>
    ))}
  </div>
);

// Component: SkeletonDetail
export const SkeletonDetail = () => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
    <Skeleton className="h-80 rounded-xl" />
    <div className="space-y-4">
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-5 w-1/2" />
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-3/4" />
      </div>
      <Skeleton className="h-10 w-36 rounded-lg" />
    </div>
  </div>
);
