import React from 'react';
import { cn, getDiscountPercent } from '../../lib/utils';

export const PriceBadge = ({
  originalPrice, discountedPrice, pricingStrategy, currency = 'INR', size = 'md'
}) => {
  const discount = getDiscountPercent(originalPrice, discountedPrice);
  // Function: fmt
  const fmt = (n) =>
    new Intl.NumberFormat('en-IN', { style: 'currency', currency }).format(n || 0);

  return (
    <div className="flex flex-col gap-0.5">
      <div className={cn('flex items-baseline gap-2', size === 'sm' ? 'flex-wrap gap-1' : '')}>
        <span
          className={cn(
            'font-bold tabular-nums text-emerald-700 dark:text-emerald-400',
            size === 'sm' ? 'text-base' : 'text-xl'
          )}
        >
          {fmt(discountedPrice)}
        </span>
        <span className={cn('line-through text-slate-400 tabular-nums', size === 'sm' ? 'text-xs' : 'text-sm')}>
          {fmt(originalPrice)}
        </span>
        {discount > 0 && (
          <span className="text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 px-2 py-0.5 rounded-full">
            {discount}% OFF
          </span>
        )}
      </div>
      {pricingStrategy === 'AI_RECOMMENDED' && (
        <span className="inline-flex items-center gap-1 text-xs text-violet-600 dark:text-violet-400 font-medium">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a.75.75 0 01.692.462l1.41 3.393 3.664.337a.75.75 0 01.428 1.317l-2.796 2.43.858 3.578a.75.75 0 01-1.12.814L10 12.796l-3.136 1.535a.75.75 0 01-1.12-.814l.858-3.578-2.796-2.43a.75.75 0 01.428-1.317l3.664-.337L9.308 2.462A.75.75 0 0110 2z" />
          </svg>
          AI-Recommended price
        </span>
      )}
    </div>
  );
};
