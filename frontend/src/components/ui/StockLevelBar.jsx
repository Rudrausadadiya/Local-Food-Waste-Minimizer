import React from 'react';
import { cn } from '../../lib/utils';

export const StockLevelBar = ({
  available = 0, reserved = 0, damaged = 0, expired = 0, showLabels = true
}) => {
  const total = available + reserved + damaged + expired;
  if (total === 0) return <span className="text-sm text-slate-400">No stock</span>;

  // Function: pct
  const pct = (n) => `${Math.round((n / total) * 100)}%`;

  const segments = [
    { key: 'available', value: available, color: 'bg-emerald-500', label: 'Available' },
    { key: 'reserved', value: reserved, color: 'bg-amber-400', label: 'Reserved' },
    { key: 'damaged', value: damaged, color: 'bg-red-400', label: 'Damaged' },
    { key: 'expired', value: expired, color: 'bg-slate-400', label: 'Expired' },
  ].filter((s) => s.value > 0);

  return (
    <div>
      <div
        className="flex h-2 w-full rounded-full overflow-hidden gap-0.5"
        role="meter"
        aria-label={`Stock: ${available} available, ${reserved} reserved, ${damaged} damaged, ${expired} expired`}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={available}
      >
        {segments.map((s) => (
          <div key={s.key} className={cn(s.color, 'transition-all duration-500')} style={{ width: pct(s.value) }} />
        ))}
      </div>

      {showLabels && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
          {segments.map((s) => (
            <span key={s.key} className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
              <span className={cn('w-2 h-2 rounded-full', s.color)} />
              {s.label}: <strong className="tabular-nums text-slate-700 dark:text-slate-300">{s.value}</strong>
            </span>
          ))}
          <span className="text-xs text-slate-400">of {total} total</span>
        </div>
      )}
    </div>
  );
};
