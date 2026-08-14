import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ShoppingBag, Search, Trash2, CheckCircle, Heart, AlertTriangle, Ban, X, ChevronDown } from 'lucide-react';
import { marketplaceApi } from '../../marketplace/api/marketplaceApi';
import { Button } from '../../../components/ui/Button';
import { StatusBadge } from '../../../components/ui/Badge';
import { SkeletonTable } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { formatCurrency, formatDateTime } from '../../../lib/utils';
import { useToastStore } from '../../../stores/useToastStore';

const TAKEDOWN_REASONS = [
  { value: 'safety', label: '⚠️ Safety / Hygiene Concern' },
  { value: 'policy', label: '🚫 Policy Violation' },
  { value: 'misleading', label: '📝 Misleading Description or Pricing' },
  { value: 'expired', label: '⏰ Expired or Unsafe Product' },
  { value: 'fraud', label: '🔍 Suspected Fraud or Misuse' },
  { value: 'quality', label: '❌ Quality Standards Not Met' },
  { value: 'other', label: '📋 Other (specify below)' },
];

// ── Takedown Reason Modal ──────────────────────────────────────────────────
// Component: TakedownModal
const TakedownModal = ({ listing, onConfirm, onClose, isPending }) => {
  const [selectedReason, setSelectedReason] = useState('');
  const [customReason, setCustomReason] = useState('');

  const finalReason = selectedReason === 'other' ? customReason : (TAKEDOWN_REASONS.find(r => r.value === selectedReason)?.label || '');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-red-100 dark:bg-red-950/60 flex items-center justify-center">
              <Ban className="w-5 h-5 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <h2 className="font-bold text-slate-900 dark:text-slate-100 text-base">Takedown Listing</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Provide a reason for vendor transparency</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Listing Preview */}
        <div className="mx-5 mt-5 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900">
          <p className="font-semibold text-sm text-red-900 dark:text-red-200">{listing.listing_title}</p>
          <p className="text-xs text-red-600 dark:text-red-400 mt-0.5">{listing.business?.business_name || 'Unknown Merchant'}</p>
        </div>

        {/* Reason Selection */}
        <div className="p-5 space-y-3">
          <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide">Select Takedown Reason</p>
          <div className="space-y-2">
            {TAKEDOWN_REASONS.map((reason) => (
              <label
                key={reason.value}
                className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all text-sm ${
                  selectedReason === reason.value
                    ? 'border-red-400 bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300'
                    : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300'
                }`}
              >
                <input
                  type="radio"
                  name="takedown_reason"
                  value={reason.value}
                  checked={selectedReason === reason.value}
                  onChange={() => setSelectedReason(reason.value)}
                  className="accent-red-600"
                />
                {reason.label}
              </label>
            ))}
          </div>

          {selectedReason === 'other' && (
            <textarea
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              placeholder="Describe the reason for takedown..."
              rows={3}
              className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"
            />
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3 px-5 pb-5">
          <Button variant="ghost" className="flex-1" onClick={onClose} disabled={isPending}>Cancel</Button>
          <Button
            variant="destructive"
            className="flex-1 font-bold"
            disabled={!selectedReason || (selectedReason === 'other' && !customReason.trim()) || isPending}
            onClick={() => onConfirm(finalReason)}
          >
            {isPending ? 'Taking Down...' : 'Confirm Takedown'}
          </Button>
        </div>
      </div>
    </div>
  );
};

// ── Main Page ──────────────────────────────────────────────────────────────
// Component: AdminListingsPage
export const AdminListingsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [takedownTarget, setTakedownTarget] = useState(null); // listing to take down
  const { addToast } = useToastStore();
  const qc = useQueryClient();

  const { data: listings, isLoading, error } = useQuery({
    queryKey: ['admin', 'listings', 'all'],
    queryFn: () => marketplaceApi.getAllListingsAdmin(),
    retry: 1,
  });

  const takedownMutation = useMutation({
    mutationFn: ({ id, reason }) => marketplaceApi.takedownListing(id, reason),
    onSuccess: (_, variables) => {
      addToast({
        title: 'Listing Taken Down',
        description: `Reason: ${variables.reason}. The vendor has been notified.`,
        variant: 'error',
      });
      setTakedownTarget(null);
      qc.invalidateQueries({ queryKey: ['admin', 'listings'] });
      qc.invalidateQueries({ queryKey: ['marketplace'] });
    },
    onError: (err) => {
      addToast({
        title: 'Takedown Failed',
        description: err?.response?.data?.detail || 'Could not take down the listing. Please try again.',
        variant: 'error',
      });
    },
  });

  const republishMutation = useMutation({
    mutationFn: (id) => marketplaceApi.republishListing(id),
    onSuccess: () => {
      addToast({ title: 'Listing Republished', description: 'Listing is live on public marketplace.', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['admin', 'listings'] });
      qc.invalidateQueries({ queryKey: ['marketplace'] });
    },
    onError: (err) => {
      addToast({ title: 'Republish Failed', description: err?.response?.data?.detail || 'Could not republish listing.', variant: 'error' });
    },
  });

  const toggleNgoVisibilityMutation = useMutation({
    mutationFn: ({ id, visibleToNgos }) => marketplaceApi.updateListing(id, { visible_to_ngos: visibleToNgos }),
    onSuccess: (_, variables) => {
      addToast({
        title: variables.visibleToNgos ? 'Donated to NGOs!' : 'Removed from NGO Feed',
        description: variables.visibleToNgos ? 'Listing is now visible in NGO Free Rescue Feed.' : 'Restricted to regular marketplace.',
        variant: 'success',
      });
      qc.invalidateQueries({ queryKey: ['admin', 'listings'] });
    },
  });

  const deleteListingMutation = useMutation({
    mutationFn: marketplaceApi.deleteListing,
    onSuccess: () => {
      addToast({ title: 'Listing Deleted', description: 'Surplus offer removed permanently.', variant: 'error' });
      qc.invalidateQueries({ queryKey: ['admin', 'listings'] });
    },
  });

  const filteredListings = (Array.isArray(listings) ? listings : []).filter((l) =>
    (l.listing_title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (l.business?.business_name || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      {/* Takedown Reason Modal */}
      {takedownTarget && (
        <TakedownModal
          listing={takedownTarget}
          isPending={takedownMutation.isPending}
          onClose={() => setTakedownTarget(null)}
          onConfirm={(reason) => takedownMutation.mutate({ id: takedownTarget.id, reason })}
        />
      )}

      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <ShoppingBag className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              Marketplace Moderation &amp; NGO Donation Controls
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Publish/unpublish surplus items, override prices, or redirect items to free NGO food banks.
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search listings or merchants..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        {error ? (
          <div className="p-6 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Failed to load listings</p>
              <p className="text-xs text-red-500 mt-1">{error?.message || 'Could not connect to the marketplace API.'}</p>
            </div>
          </div>
        ) : isLoading ? (
          <SkeletonTable rows={6} cols={6} />
        ) : !filteredListings.length ? (
          <EmptyState
            icon={<ShoppingBag className="w-8 h-8" />}
            title="No marketplace listings found"
            description="Active merchant surplus listings will show up here for moderation."
          />
        ) : (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <table className="w-full text-sm" aria-label="Marketplace listings">
              <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  {['Listing Title', 'Merchant', 'Price / Type', 'NGO Feed', 'Status / Reason', 'Actions'].map((h) => (
                    <th key={h} className="text-left px-4 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredListings.map((listing) => {
                  const isPublished = listing.listing_status === 'PUBLISHED';
                  const isUnpublished = listing.listing_status === 'UNPUBLISHED';
                  const isNgoVisible = listing.visible_to_ngos;

                  return (
                    <tr key={listing.id} className={`hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors ${isUnpublished ? 'opacity-75' : ''}`}>
                      <td className="px-4 py-3.5">
                        <p className="font-bold text-slate-900 dark:text-slate-100">{listing.listing_title}</p>
                        <p className="text-[10px] text-slate-400 font-mono">Qty: {listing.quantity_available} units</p>
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-600 dark:text-slate-400">{listing.business?.business_name || 'Merchant'}</td>
                      <td className="px-4 py-3.5">
                        <span className="font-semibold text-emerald-600 dark:text-emerald-400 block text-xs">
                          {Number(listing.discounted_price) === 0 ? 'FREE NGO' : formatCurrency(listing.discounted_price)}
                        </span>
                        <span className="text-[10px] text-slate-400 line-through">
                          {listing.original_price ? formatCurrency(listing.original_price) : ''}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <button
                          onClick={() => toggleNgoVisibilityMutation.mutate({ id: listing.id, visibleToNgos: !isNgoVisible })}
                          className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-full border transition-all ${
                            isNgoVisible
                              ? 'bg-purple-50 text-purple-700 border-purple-300 dark:bg-purple-950/80 dark:text-purple-300'
                              : 'bg-slate-100 text-slate-600 border-slate-300 dark:bg-slate-800 dark:text-slate-400'
                          }`}
                        >
                          <Heart className="w-3 h-3 text-purple-500" />
                          {isNgoVisible ? 'DONATED TO NGO' : 'MAKE NGO FREE'}
                        </button>
                      </td>

                      {/* Status + Takedown Reason */}
                      <td className="px-4 py-3.5">
                        <StatusBadge status={listing.listing_status || 'PUBLISHED'} />
                        {isUnpublished && listing.takedown_reason && (
                          <p className="text-[10px] text-red-500 dark:text-red-400 mt-1 max-w-[140px] line-clamp-2" title={listing.takedown_reason}>
                            {listing.takedown_reason}
                          </p>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          {isPublished ? (
                            <Button
                              variant="destructive"
                              size="xs"
                              className="font-bold"
                              leftIcon={<Ban className="w-3.5 h-3.5" />}
                              onClick={() => setTakedownTarget(listing)}
                            >
                              Takedown
                            </Button>
                          ) : isUnpublished ? (
                            <Button
                              variant="primary"
                              size="xs"
                              className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold"
                              leftIcon={<CheckCircle className="w-3.5 h-3.5" />}
                              onClick={() => republishMutation.mutate(listing.id)}
                              disabled={republishMutation.isPending}
                            >
                              Republish
                            </Button>
                          ) : (
                            <span className="text-[10px] text-slate-400 italic">No action</span>
                          )}
                          <button
                            onClick={() => {
                              if (confirm(`Are you sure you want to delete "${listing.listing_title}"?`)) {
                                deleteListingMutation.mutate(listing.id);
                              }
                            }}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/50 transition-colors"
                            title="Delete Listing"
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
    </>
  );
};

export default AdminListingsPage;
