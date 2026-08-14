import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Heart, MapPin, Truck, LayoutGrid, Map } from 'lucide-react';
import { marketplaceApi } from '../../marketplace/api/marketplaceApi';
import { ordersApi } from '../../orders/api/ordersApi';
import { Button } from '../../../components/ui/Button';
import { Badge } from '../../../components/ui/Badge';
import { SkeletonCardGrid } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { LiveMapPicker } from '../../../components/ui/LiveMapPicker';
import { useToastStore } from '../../../stores/useToastStore';
import { getListingCoordinates } from '../../../lib/utils';

// Component: NgoBrowsePage
const NgoBrowsePage = () => {
  const [viewMode, setViewMode] = useState('grid');
  const { addToast } = useToastStore();
  const qc = useQueryClient();

  // FETCH NGO LISTINGS: Queries the marketplace feed for items visible to NGOs
  const { data: listings, isLoading } = useQuery({
    queryKey: ['marketplace', 'ngo-feed'],
    queryFn: () => marketplaceApi.getPublicListings({ visible_to_ngos: 'true' }),
  });

  // FILTER LISTINGS: Removes suspended businesses and unpublished/expired listings
  const activeListings = (listings || []).filter((l) => {
    const bizStatus = l.business?.business_status;
    if (bizStatus === 'SUSPENDED' || bizStatus === 'REJECTED') {
      return false;
    }
    if (l.listing_status === 'UNPUBLISHED' || l.listing_status === 'EXPIRED') {
      return false;
    }
    return true;
  });

  // CLAIM DONATION MUTATION: Handles the process of an NGO claiming a food listing
  const claimDonationMutation = useMutation({
    mutationFn: (listingId) => ordersApi.createOrder({ listing: listingId, quantity: 1 }),
    onSuccess: (data) => {
      addToast({
        title: 'Donation Claimed!',
        description: data?.claim_code ? `Pickup Claim Code #${data.claim_code} generated. Check your pickups list.` : 'Donation request submitted successfully. Check your pickups list.',
        variant: 'success'
      });
      qc.invalidateQueries({ queryKey: ['marketplace'] });
    },
    onError: (err) => {
      addToast({
        title: 'Claim Failed',
        description: err?.response?.data?.detail || 'Could not claim donation.',
        variant: 'error'
      });
    },
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">NGO Surplus & Donation Feed</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Browse free donation offers and NGO-eligible surplus food items nearby</p>
        </div>

        {/* Grid vs Map Toggle */}
        <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl self-start sm:self-auto">
          <button
            onClick={() => setViewMode('grid')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewMode === 'grid'
                ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" /> Grid View
          </button>
          <button
            onClick={() => setViewMode('map')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewMode === 'map'
                ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <Map className="w-3.5 h-3.5" /> Interactive Map
          </button>
        </div>
      </div>

      {isLoading ? (
        <SkeletonCardGrid count={6} />
      ) : viewMode === 'map' ? (
        // INTERACTIVE MAP VIEW: Displays active listings on a map
        <div className="h-full min-h-[550px] w-full rounded-2xl overflow-hidden shadow-lg border border-slate-200 dark:border-slate-800">
          <LiveMapPicker
            height="580px"
            allowSearch={true}
            allowLiveTracking={true}
            markers={(activeListings || []).map((l) => {
              const { lat, lng } = getListingCoordinates(l);
              return {
                id: l.id,
                title: l.listing_title,
                businessName: l.business?.business_name || 'Donor Merchant',
                type: 'NGO',
                priceLabel: 'FREE DONATION',
                lat,
                lng,
                image: l.image,
              };
            })}
          />
        </div>
      ) : !activeListings?.length ? (
        <EmptyState
          icon={<Heart className="w-8 h-8" />}
          title="No active donation listings"
          description="There are currently no active food donation listings available nearby. Check back soon or set up alerts."
        />
      ) : (
        // GRID VIEW: Displays active listings as cards
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {activeListings.map((listing) => (
            <motion.div
              key={listing.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <Badge variant="ngo" label={listing.listing_type === 'DONATION' ? 'FREE DONATION' : 'NGO ELIGIBLE'} />
                <span className="text-xs text-indigo-600 dark:text-indigo-400 font-bold tabular-nums">{listing.quantity_available} items left</span>
              </div>

              <div>
                <h3 className="font-bold text-slate-900 dark:text-slate-100 text-base">{listing.listing_title}</h3>
                <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                  <MapPin className="w-3.5 h-3.5" /> {listing.business?.business_name}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Truck className="w-3.5 h-3.5" /> Direct Pickup
                </span>
                <Button
                  variant="ngo"
                  size="sm"
                  loading={claimDonationMutation.isPending}
                  onClick={() => claimDonationMutation.mutate(listing.id)}
                >
                  Claim Donation
                </Button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NgoBrowsePage;
