import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { GitBranch, Plus, MapPin, Phone, Mail, Clock, Calendar } from 'lucide-react';
import { useBranchStore } from '../../../stores/useBranchStore';
import { businessApi } from '../api/businessApi';
import { Button } from '../../../components/ui/Button';
import { StatusBadge } from '../../../components/ui/Badge';
import { SkeletonCardGrid } from '../../../components/ui/Skeleton';
import { useToastStore } from '../../../stores/useToastStore';

// Component: BranchManagementPage
const BranchManagementPage = () => {
  const { activeBusinessId, branches } = useBranchStore();
  const { addToast } = useToastStore();

  const { isLoading } = useQuery({
    queryKey: ['business', activeBusinessId, 'branches'],
    queryFn: () => businessApi.getBranches(activeBusinessId),
    enabled: !!activeBusinessId,
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Multi-Branch Locations & Operating Hours</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage operational branches, pickup time windows, and store addresses</p>
        </div>
        <Button
          variant="primary"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => addToast({ title: 'Branch Onboarding', description: 'Fill in new store details to register branch location.', variant: 'info' })}
        >
          Add New Branch
        </Button>
      </div>

      {isLoading ? (
        <SkeletonCardGrid count={3} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {branches.map((branch) => (
            <div key={branch.id} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">{branch.branch_name}</h3>
                  <span className="font-mono text-xs text-slate-400 font-semibold">{branch.branch_code}</span>
                </div>
                <StatusBadge status={branch.branch_status} />
              </div>

              {/* Feature 1: Pickup Window & Operating Hours Banner */}
              <div className="p-3.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 space-y-1">
                <p className="text-xs font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-emerald-600" /> Surplus Pickup Window
                </p>
                <p className="text-xs text-emerald-700 dark:text-emerald-400 font-mono font-semibold">
                  7:30 PM – 9:30 PM Daily (Pre-Closing)
                </p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400">Store Hours: Mon–Sun 8:00 AM – 10:00 PM</p>
              </div>

              <div className="space-y-2 text-xs text-slate-500 dark:text-slate-400 pt-3 border-t border-slate-100 dark:border-slate-800">
                <p className="flex items-center gap-2"><Phone className="w-3.5 h-3.5 text-slate-400" /> {branch.phone}</p>
                <p className="flex items-center gap-2"><Mail className="w-3.5 h-3.5 text-slate-400" /> {branch.email}</p>
                {branch.address && (
                  <p className="flex items-start gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
                    <span>{branch.address.address_line_1}, {branch.address.city}</span>
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BranchManagementPage;
