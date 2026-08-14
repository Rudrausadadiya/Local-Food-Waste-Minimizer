import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Check, X, ShieldAlert, ShieldCheck, Trash2, Ban, Search, Building2, RotateCcw } from 'lucide-react';
import { businessApi } from '../../business/api/businessApi';
import { Button } from '../../../components/ui/Button';
import { StatusBadge } from '../../../components/ui/Badge';
import { SkeletonTable } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { useToastStore } from '../../../stores/useToastStore';

// Component: AdminBusinessesPage
export const AdminBusinessesPage = () => {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const { addToast } = useToastStore();
  const qc = useQueryClient();

  const { data: businesses, isLoading } = useQuery({
    queryKey: ['admin', 'businesses', statusFilter],
    queryFn: () => businessApi.getAllBusinesses({}),
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }) => businessApi.updateBusinessStatus(id, status),
    onSuccess: (_, variables) => {
      const isSus = variables.status === 'SUSPENDED';
      const isApp = variables.status === 'APPROVED';
      addToast({
        title: isSus ? 'Store Suspended!' : isApp ? 'Store Reactivated & Approved!' : `Status Updated to ${variables.status}`,
        description: isSus
          ? 'Store listings have been hidden from Customer & NGO feeds.'
          : isApp
          ? 'Store listings are now visible on public marketplace.'
          : `Business status changed to ${variables.status}.`,
        variant: isSus ? 'error' : 'success'
      });
      qc.invalidateQueries({ queryKey: ['admin', 'businesses'] });
      qc.invalidateQueries({ queryKey: ['marketplace'] });
    },
  });

  const toggleVerifyMutation = useMutation({
    mutationFn: ({ id, isVerified }) => businessApi.toggleVerifyBusiness(id, isVerified),
    onMutate: async ({ id, isVerified }) => {
      await qc.cancelQueries({ queryKey: ['admin', 'businesses'] });
      qc.setQueriesData({ queryKey: ['admin', 'businesses'] }, (old) => {
        if (!Array.isArray(old)) return old;
        return old.map((b) => (b.id === id ? { ...b, is_verified: isVerified } : b));
      });
    },
    onSuccess: (_, variables) => {
      addToast({
        title: variables.isVerified ? 'Verified Badge Assigned!' : 'Verification Revoked',
        description: variables.isVerified ? 'Merchant verified badge is now active.' : 'Verified badge removed from store.',
        variant: 'success'
      });
      qc.invalidateQueries({ queryKey: ['admin', 'businesses'] });
      qc.invalidateQueries({ queryKey: ['marketplace'] });
      qc.invalidateQueries({ queryKey: ['auth', 'profile'] });
    },
    onError: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'businesses'] });
      addToast({ title: 'Update failed', description: 'Could not update verification status.', variant: 'error' });
    }
  });

  const deleteBusinessMutation = useMutation({
    mutationFn: businessApi.deleteBusiness,
    onSuccess: () => {
      addToast({ title: 'Business Profile Removed', description: 'Store deleted from system.', variant: 'info' });
      qc.invalidateQueries({ queryKey: ['admin', 'businesses'] });
      qc.invalidateQueries({ queryKey: ['marketplace'] });
    },
  });

  const filteredBusinesses = (Array.isArray(businesses) ? businesses : []).filter((b) => {
    const matchesStatus = statusFilter === 'ALL' || b.business_status === statusFilter;
    const matchesQuery = (b.business_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (b.business_email || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesQuery;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Building2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            Merchant & Business Operations Queue
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Approve onboarding applications, grant verified store badges, or suspend non-compliant merchants.
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search store name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      <div className="border-b border-slate-200 dark:border-slate-800 flex gap-6">
        {['ALL', 'PENDING', 'APPROVED', 'SUSPENDED', 'REJECTED'].map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            className={`pb-3 text-sm font-semibold border-b-2 transition-colors ${
              statusFilter === st
                ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {isLoading ? (
        <SkeletonTable rows={5} cols={6} />
      ) : !filteredBusinesses.length ? (
        <EmptyState
          icon={<ShieldAlert className="w-8 h-8 text-amber-500" />}
          title={`No ${statusFilter.toLowerCase()} stores found`}
          description="Merchant applications and registered businesses will appear here."
        />
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
          <table className="w-full text-sm" aria-label="Business applications">
            <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                {['Store / Organisation Name', 'Category', 'FSSAI / License Proof', 'Contact Email', 'Verification', 'Status', 'Moderation Actions'].map((h) => (
                  <th key={h} className="text-left px-4 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {filteredBusinesses.map((biz) => {
                const isSuspended = biz.business_status === 'SUSPENDED';
                const isApproved = biz.business_status === 'APPROVED';
                const isTogglingThis = toggleVerifyMutation.isPending && toggleVerifyMutation.variables?.id === biz.id;

                return (
                  <tr key={biz.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3.5 font-bold text-slate-900 dark:text-slate-100">{biz.business_name}</td>
                    <td className="px-4 py-3.5 text-xs text-slate-500">{biz.business_type}</td>
                    <td className="px-4 py-3.5 text-xs">
                      <div className="space-y-0.5">
                        <p className="font-mono text-[11px] font-bold text-indigo-600 dark:text-indigo-400">
                          {biz.registration_number ? `LIC: ${biz.registration_number}` : 'FSSAI: Pending Upload'}
                        </p>
                        {biz.gst_number && (
                          <p className="font-mono text-[10px] text-slate-400">GST: {biz.gst_number}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-600 dark:text-slate-400">{biz.business_email}</td>
                    <td className="px-4 py-3.5">
                      <button
                        disabled={isTogglingThis}
                        onClick={() => toggleVerifyMutation.mutate({ id: biz.id, isVerified: !biz.is_verified })}
                        className={`inline-flex items-center gap-1.5 text-[10px] font-bold px-3 py-1.5 rounded-full border transition-all active:scale-95 cursor-pointer shadow-sm ${
                          biz.is_verified
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-300 hover:bg-emerald-100 dark:bg-emerald-950/80 dark:text-emerald-300'
                            : 'bg-slate-100 text-slate-600 border-slate-300 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400'
                        } ${isTogglingThis ? 'opacity-60 cursor-wait' : ''}`}
                      >
                        <ShieldCheck className={`w-3.5 h-3.5 ${biz.is_verified ? 'text-emerald-600' : 'text-slate-400'} ${isTogglingThis ? 'animate-spin' : ''}`} />
                        <span>{isTogglingThis ? 'Updating...' : biz.is_verified ? 'VERIFIED MERCHANT' : 'UNVERIFIED'}</span>
                      </button>
                    </td>
                    <td className="px-4 py-3.5">
                      <StatusBadge status={biz.business_status} />
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-2">
                        {isSuspended ? (
                          <Button
                            variant="primary"
                            size="xs"
                            className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold"
                            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
                            onClick={() => updateStatusMutation.mutate({ id: biz.id, status: 'APPROVED' })}
                          >
                            Reactivate Store
                          </Button>
                        ) : isApproved ? (
                          <Button
                            variant="outline"
                            size="xs"
                            className="text-red-600 hover:bg-red-50 border-red-200 dark:border-red-800 font-bold"
                            leftIcon={<Ban className="w-3.5 h-3.5" />}
                            onClick={() => updateStatusMutation.mutate({ id: biz.id, status: 'SUSPENDED' })}
                          >
                            Suspend Store
                          </Button>
                        ) : (
                          <div className="flex gap-1.5">
                            <Button
                              variant="primary"
                              size="xs"
                              leftIcon={<Check className="w-3.5 h-3.5" />}
                              onClick={() => updateStatusMutation.mutate({ id: biz.id, status: 'APPROVED' })}
                            >
                              Approve
                            </Button>
                            <Button
                              variant="destructive"
                              size="xs"
                              leftIcon={<X className="w-3.5 h-3.5" />}
                              onClick={() => updateStatusMutation.mutate({ id: biz.id, status: 'REJECTED' })}
                            >
                              Reject
                            </Button>
                          </div>
                        )}

                        <button
                          onClick={() => {
                            if (confirm(`Are you sure you want to delete ${biz.business_name}?`)) {
                              deleteBusinessMutation.mutate(biz.id);
                            }
                          }}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/50 transition-colors"
                          title="Delete Business Profile"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminBusinessesPage;
