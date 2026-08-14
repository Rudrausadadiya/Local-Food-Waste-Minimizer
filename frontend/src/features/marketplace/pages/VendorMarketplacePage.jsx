import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, ShoppingBag, Trash2, AlertTriangle, ShieldAlert } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceApi } from '../api/marketplaceApi';
import { StatusBadge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { PriceBadge } from '../../../components/ui/PriceBadge';
import { SkeletonTable } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { ConfirmDialog } from '../../../components/ui/Dialog';
import { useToastStore } from '../../../stores/useToastStore';
import { formatDateTime } from '../../../lib/utils';

// Component: VendorMarketplacePage
const VendorMarketplacePage = () => {
  const navigate = useNavigate();
  const [deleteId, setDeleteId] = useState(null);
  const { addToast } = useToastStore();
  const qc = useQueryClient();

  const { data: listings, isLoading } = useQuery({
    queryKey: ['marketplace', 'mine'],
    queryFn: marketplaceApi.getMyListings,
  });

  const deleteMutation = useMutation({
    mutationFn: marketplaceApi.deleteListing,
    onSuccess: () => {
      addToast({ title: 'Listing deleted', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['marketplace', 'mine'] });
      setDeleteId(null);
    },
  });

  const takenDownListings = (Array.isArray(listings) ? listings : []).filter(
    (l) => l.listing_status === 'UNPUBLISHED' && l.takedown_reason
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Surplus Listings</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage active, draft, and expired marketplace listings</p>
        </div>
        <Link to="/vendor/marketplace/new">
          <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>New Listing</Button>
        </Link>
      </div>

      {/* ── Admin Takedown Alerts ── */}
      {takenDownListings.length > 0 && (
        <div className="space-y-3">
          {takenDownListings.map((listing) => (
            <div key={listing.id} className="flex items-start gap-4 p-4 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800">
              <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-900/60 flex items-center justify-center shrink-0">
                <ShieldAlert className="w-5 h-5 text-red-600 dark:text-red-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="font-bold text-red-800 dark:text-red-200 text-sm">Listing Taken Down by Admin</p>
                  <span className="text-[10px] font-mono bg-red-100 dark:bg-red-900/60 text-red-600 dark:text-red-400 px-2 py-0.5 rounded-full">UNPUBLISHED</span>
                </div>
                <p className="font-semibold text-slate-800 dark:text-slate-200 text-sm mt-0.5">{listing.listing_title}</p>
                <div className="mt-1.5 flex items-start gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0 mt-0.5" />
                  <p className="text-xs text-red-600 dark:text-red-400">
                    <span className="font-semibold">Reason: </span>{listing.takedown_reason}
                  </p>
                </div>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1.5">
                  This listing is no longer visible to customers or NGOs. Contact support to appeal this decision.
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Listings Table ── */}
      {isLoading ? (
        <SkeletonTable rows={5} cols={5} />
      ) : !(Array.isArray(listings) && listings.length) ? (
        <EmptyState
          icon={<ShoppingBag className="w-8 h-8" />}
          title="No marketplace listings"
          description="Publish surplus food from your inventory to start rescuing food and recovering revenue."
          action={{ label: '+ New Listing', onClick: () => navigate('/vendor/marketplace/new') }}
        />
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
          <table className="w-full text-sm" aria-label="Vendor listings">
            <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                {['Listing', 'Pricing', 'Available', 'Expires At', 'Status', 'Actions'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {listings.map((item) => {
                const isTakenDown = item.listing_status === 'UNPUBLISHED' && item.takedown_reason;
                return (
                  <tr
                    key={item.id}
                    className={`transition-colors ${
                      isTakenDown
                        ? 'bg-red-50/50 dark:bg-red-950/20 hover:bg-red-50 dark:hover:bg-red-950/30'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
                    }`}
                  >
                    <td className="px-4 py-3.5">
                      <p className={`font-medium text-sm ${isTakenDown ? 'text-red-700 dark:text-red-300 line-through' : 'text-slate-800 dark:text-slate-200'}`}>
                        {item.listing_title}
                      </p>
                      <p className="text-xs text-slate-400">{item.listing_type}</p>
                      {isTakenDown && (
                        <p className="text-[10px] text-red-500 mt-0.5 flex items-center gap-1">
                          <ShieldAlert className="w-3 h-3" /> Admin: {item.takedown_reason}
                        </p>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      <PriceBadge originalPrice={Number(item.original_price)} discountedPrice={Number(item.discounted_price)} size="sm" />
                    </td>
                    <td className="px-4 py-3.5 tabular-nums text-slate-700 dark:text-slate-300 font-semibold">
                      {item.quantity_available} units
                    </td>
                    <td className="px-4 py-3.5 text-xs text-slate-500 tabular-nums">
                      {formatDateTime(item.expires_at)}
                    </td>
                    <td className="px-4 py-3.5">
                      <StatusBadge status={item.listing_status} />
                    </td>
                    <td className="px-4 py-3.5">
                      <button
                        onClick={() => setDeleteId(item.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-slate-100 dark:hover:bg-slate-800"
                        aria-label="Delete listing"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog
        open={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={() => deleteMutation.mutate(deleteId)}
        title="Delete Listing?"
        description="Are you sure you want to delete this surplus listing? This cannot be undone."
        loading={deleteMutation.isPending}
      />
    </div>
  );
};

export default VendorMarketplacePage;
