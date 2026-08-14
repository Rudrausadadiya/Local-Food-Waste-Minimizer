import React, { useState, useEffect } from 'react';
import { useBranchStore } from '../../../stores/useBranchStore';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../../../stores/useAuthStore';
import { businessApi } from '../api/businessApi';
import { GitBranch, ChevronDown } from 'lucide-react';
import { cn } from '../../../lib/utils';

// Component: BranchSwitcher
export const BranchSwitcher = () => {
  const { user } = useAuthStore();
  const { activeBusinessId, activeBranchId, branches, setBranches, setActiveBranch, setBusiness } = useBranchStore();
  const [open, setOpen] = useState(false);

  const { data: businesses } = useQuery({
    queryKey: ['business', 'mine'],
    queryFn: businessApi.getMyBusiness,
    enabled: !!user && (user.role === 'VENDOR' || user.role === 'NGO'),
  });

  const businessId = activeBusinessId ?? businesses?.[0]?.id;

  // Set the active business ID when we get businesses
  useEffect(() => {
    if (businesses?.[0]?.id && !activeBusinessId) {
      setBusiness(businesses[0].id);
    }
  }, [businesses, activeBusinessId, setBusiness]);

  const { data: fetchedBranches } = useQuery({
    queryKey: ['business', businessId, 'branches'],
    queryFn: () => businessApi.getBranches(businessId),
    enabled: !!businessId,
  });

  // Update the branch store when data arrives
  useEffect(() => {
    if (fetchedBranches && fetchedBranches.length > 0) {
      setBranches(fetchedBranches);
    }
  }, [fetchedBranches, setBranches]);

  const activeBranch = branches.find((b) => b.id === activeBranchId);

  if (!branches.length) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm"
        aria-label="Switch branch"
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <GitBranch className="w-3.5 h-3.5 text-slate-400" />
        <span className="text-slate-700 dark:text-slate-300 font-medium max-w-32 truncate">
          {activeBranch?.branch_name ?? 'Select Branch'}
        </span>
        <ChevronDown className={cn('w-3.5 h-3.5 text-slate-400 transition-transform duration-150', open && 'rotate-180')} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div
            role="listbox"
            aria-label="Branch list"
            className="absolute top-full left-0 mt-1 z-20 min-w-48 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-lg overflow-hidden"
          >
            {branches.map((branch) => (
              <button
                key={branch.id}
                role="option"
                aria-selected={branch.id === activeBranchId}
                onClick={() => { setActiveBranch(branch.id); setOpen(false); }}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors',
                  branch.id === activeBranchId
                    ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400'
                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                )}
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{branch.branch_name}</p>
                  <p className="text-xs text-slate-400 dark:text-slate-500 truncate">{branch.branch_code}</p>
                </div>
                {branch.is_main_branch && (
                  <span className="text-xs text-emerald-500 font-medium">Main</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
