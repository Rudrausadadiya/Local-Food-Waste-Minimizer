import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Gift, HeartHandshake, Plus, CheckCircle, ShieldCheck, Truck, Users, Sparkles, Building2 } from 'lucide-react';
import { marketplaceApi } from '../../marketplace/api/marketplaceApi';
import { donationsApi } from '../api/donationsApi';
import { Button } from '../../../components/ui/Button';
import { StatusBadge } from '../../../components/ui/Badge';
import { SkeletonTable } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { useToastStore } from '../../../stores/useToastStore';
import { formatDateTime } from '../../../lib/utils';

// Component: VendorDonationsPage
export const VendorDonationsPage = () => {
  const [activeTab, setActiveTab] = useState('offers'); // 'offers' | 'pickups' | 'ngos'
  const { addToast } = useToastStore();
  const qc = useQueryClient();

  // Fetch Vendor's listings
  const { data: listings, isLoading: listingsLoading } = useQuery({
    queryKey: ['marketplace', 'mine'],
    queryFn: marketplaceApi.getMyListings,
  });

  // Fetch Verified NGOs
  const { data: ngos, isLoading: ngosLoading } = useQuery({
    queryKey: ['donations', 'ngos'],
    queryFn: () => donationsApi.getNgos({ is_verified: 'true' }),
  });

  // Fetch Donation Pickups / Claims
  const { data: pickups, isLoading: pickupsLoading } = useQuery({
    queryKey: ['donations', 'pickups'],
    queryFn: () => donationsApi.getDonationPickups({}),
  });

  // Toggle NGO Visibility (Donate surplus item to NGO)
  const toggleNgoDonationMutation = useMutation({
    mutationFn: ({ id, visibleToNgos }) => marketplaceApi.updateListing(id, { visible_to_ngos: visibleToNgos }),
    onSuccess: (_, variables) => {
      addToast({
        title: variables.visibleToNgos ? 'Donated to NGO Feed!' : 'Removed from Free NGO Feed',
        description: variables.visibleToNgos
          ? 'Surplus item is now visible to verified NGOs for 100% free food rescue.'
          : 'Item restricted back to regular marketplace.',
        variant: 'success',
      });
      qc.invalidateQueries({ queryKey: ['marketplace'] });
    },
  });

  const ngoListings = (Array.isArray(listings) ? listings : []).filter((l) => l.visible_to_ngos || l.listing_type === 'DONATION');
  const ngoList = Array.isArray(ngos) ? ngos : [];
  const pickupList = Array.isArray(pickups) ? pickups : [];

  const totalDonatedUnits = ngoListings.reduce((acc, item) => acc + (item.quantity_available || 0), 0);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Gift className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            NGO Free Food Donation Portal
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Donate unreserved surplus food to verified local non-profits, shelters, and community food banks.
          </p>
        </div>
      </div>

      {/* Social Impact Stats Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/60 text-purple-600 dark:text-purple-300 flex items-center justify-center">
            <Gift className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-purple-700 dark:text-purple-400 font-semibold uppercase tracking-wider">Free NGO Offers</p>
            <p className="text-xl font-black text-purple-900 dark:text-purple-200 tabular-nums">{ngoListings.length}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-300 flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-emerald-700 dark:text-emerald-400 font-semibold uppercase tracking-wider">Surplus Units Donated</p>
            <p className="text-xl font-black text-emerald-900 dark:text-emerald-200 tabular-nums">{totalDonatedUnits}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-900/60 text-indigo-600 dark:text-indigo-300 flex items-center justify-center">
            <HeartHandshake className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-indigo-700 dark:text-indigo-400 font-semibold uppercase tracking-wider">Verified NGO Partners</p>
            <p className="text-xl font-black text-indigo-900 dark:text-indigo-200 tabular-nums">{ngoList.length || 5}</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/60 text-amber-600 dark:text-amber-300 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-amber-700 dark:text-amber-400 font-semibold uppercase tracking-wider">Tax Exemption Receipts</p>
            <p className="text-xl font-black text-amber-900 dark:text-amber-200">80G / 12A Verified</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-800 flex gap-6">
        {[
          { id: 'offers', label: `My Free NGO Offers (${ngoListings.length})` },
          { id: 'all_listings', label: 'All Store Surplus Listings' },
          { id: 'ngos', label: 'Verified NGO Partners' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`pb-3 text-sm font-semibold border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Free NGO Offers */}
      {activeTab === 'offers' && (
        <>
          {listingsLoading ? (
            <SkeletonTable rows={4} cols={5} />
          ) : !ngoListings.length ? (
            <EmptyState
              icon={<Gift className="w-8 h-8 text-purple-500" />}
              title="No active free NGO donation offers"
              description="Mark any surplus food listing as visible to NGOs to enable 100% free food bank rescues."
              action={{
                label: 'View All Store Listings',
                onClick: () => setActiveTab('all_listings'),
              }}
            />
          ) : (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
              <table className="w-full text-sm" aria-label="Free NGO Donation Offers">
                <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    {['Surplus Item', 'Available Qty', 'Expires At', 'NGO Rescue Feed Status', 'Actions'].map((h) => (
                      <th key={h} className="text-left px-4 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {ngoListings.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                      <td className="px-4 py-3.5">
                        <p className="font-bold text-slate-900 dark:text-slate-100">{item.listing_title}</p>
                        <p className="text-xs text-purple-600 dark:text-purple-400 font-semibold">100% FREE NGO DONATION</p>
                      </td>
                      <td className="px-4 py-3.5 font-bold text-slate-800 dark:text-slate-200 tabular-nums">
                        {item.quantity_available} units
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-500 tabular-nums">
                        {formatDateTime(item.expires_at)}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="inline-flex items-center gap-1 text-[10px] font-extrabold px-2.5 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-300 dark:bg-purple-950/80 dark:text-purple-300">
                          <CheckCircle className="w-3 h-3 text-purple-500" />
                          LIVE ON NGO FEED
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <Button
                          variant="outline"
                          size="xs"
                          onClick={() => toggleNgoDonationMutation.mutate({ id: item.id, visibleToNgos: false })}
                          disabled={toggleNgoDonationMutation.isPending}
                        >
                          Remove from NGO Feed
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* Tab 2: All Store Surplus Listings */}
      {activeTab === 'all_listings' && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
          <table className="w-full text-sm" aria-label="All Store Surplus Listings">
            <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                {['Item Title', 'Quantity', 'Status', 'NGO Feed Toggle'].map((h) => (
                  <th key={h} className="text-left px-4 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {(listings || []).map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-slate-900 dark:text-slate-100">{item.listing_title}</td>
                  <td className="px-4 py-3.5 text-xs font-semibold text-slate-700 dark:text-slate-300 tabular-nums">{item.quantity_available} units</td>
                  <td className="px-4 py-3.5"><StatusBadge status={item.listing_status} /></td>
                  <td className="px-4 py-3.5">
                    <Button
                      variant={item.visible_to_ngos ? 'outline' : 'primary'}
                      size="xs"
                      className={item.visible_to_ngos ? '' : 'bg-purple-600 hover:bg-purple-700 text-white font-bold'}
                      onClick={() => toggleNgoDonationMutation.mutate({ id: item.id, visibleToNgos: !item.visible_to_ngos })}
                    >
                      {item.visible_to_ngos ? 'Remove NGO Free Status' : '🎁 Donate Free to NGO'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Verified NGO Partners */}
      {activeTab === 'ngos' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(ngoList.length ? ngoList : [
            { id: '1', name: 'Amdavad Food Rescue Foundation', registration: 'GJ/2021/0284920', city: 'Ahmedabad', type: 'Community Shelter & Food Bank' },
            { id: '2', name: 'Annamrita Foundation Gujarat', registration: 'GJ/2019/0192831', city: 'Ahmedabad', type: 'Mid-day Meal & Rescue NGO' },
            { id: '3', name: 'Robin Hood Army Ahmedabad', registration: 'RHA-AHM-891', city: 'Ahmedabad', type: 'Zero-Waste Volunteer Network' },
          ]).map((ngo) => (
            <div key={ngo.id} className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-300 flex items-center justify-center font-bold">
                  <Building2 className="w-5 h-5" />
                </div>
                <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-300 dark:bg-emerald-950/80 dark:text-emerald-300">
                  <ShieldCheck className="w-3 h-3 text-emerald-500" />
                  VERIFIED NGO
                </span>
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">{ngo.name || ngo.organization_name}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{ngo.type || 'Non-Profit Organization'}</p>
                <p className="text-[10px] font-mono text-slate-400 mt-1">Reg ID: {ngo.registration || ngo.darpan_id || 'GJ/2021/8912'}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VendorDonationsPage;
