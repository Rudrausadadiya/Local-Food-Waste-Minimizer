import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Heart, MapPin, ShieldAlert } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceApi } from '../api/marketplaceApi';
import { PriceBadge } from '../../../components/ui/PriceBadge';
import { Button } from '../../../components/ui/Button';
import { SkeletonCardGrid } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { useToastStore } from '../../../stores/useToastStore';

import { ordersApi } from '../../orders/api/ordersApi';

// Component: WishlistPage
const WishlistPage = () => {
  const { addToast } = useToastStore();
  const qc = useQueryClient();
  const navigate = useNavigate();

  const { data: customerOrders } = useQuery({
    queryKey: ['orders', 'customer'],
    queryFn: () => ordersApi.getCustomerOrders(),
  });

  const activeHoldListingIds = new Set(
    (customerOrders || [])
      .filter((o) => (o.status === 'PENDING' || o.order_status === 'PENDING'))
      .map((o) => o.listing?.id || o.listing)
  );

  const { data: wishlist, isLoading } = useQuery({
    queryKey: ['marketplace', 'wishlist'],
    queryFn: marketplaceApi.getWishlist,
  });

  const removeMutation = useMutation({
    mutationFn: marketplaceApi.removeFromWishlist,
    onSuccess: () => {
      addToast({ title: 'Removed from saved', variant: 'info' });
      qc.invalidateQueries({ queryKey: ['marketplace', 'wishlist'] });
    },
  });

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Saved Items</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {wishlist?.length ?? 0} items saved to your wishlist
        </p>
      </div>

      {isLoading ? (
        <SkeletonCardGrid count={4} />
      ) : !wishlist?.length ? (
        <EmptyState
          icon={<Heart className="w-8 h-8 text-emerald-600" />}
          title="Your wishlist is empty"
          description="Save surplus food items you're interested in by tapping the heart icon on any listing."
          action={{ label: 'Browse Marketplace', onClick: () => navigate('/customer/browse') }}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {wishlist.map((item) => {
            const listing = item.listing_details || (typeof item.listing === 'object' ? item.listing : item);
            const targetListingId = listing.id || item.listing;
            const isUnavailable = listing.listing_status === 'UNPUBLISHED' || listing.listing_status === 'EXPIRED' || listing.listing_status === 'CLOSED';

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                layout
                className={`bg-white dark:bg-slate-900 rounded-xl border overflow-hidden shadow-sm transition-shadow ${
                  isUnavailable
                    ? 'border-red-200 dark:border-red-800 opacity-80'
                    : 'border-slate-200 dark:border-slate-800 hover:shadow-md'
                }`}
              >
                {/* Image area */}
                <div className="h-40 bg-slate-100 dark:bg-slate-800 overflow-hidden relative">
                  {listing.image ? (
                    <img
                      src={listing.image}
                      alt={listing.listing_title || 'Surplus Item'}
                      className={`w-full h-full object-cover ${isUnavailable ? 'grayscale brightness-75' : ''}`}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-300 dark:text-slate-600">
                      <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}

                  {/* Unavailable overlay */}
                  {isUnavailable && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/50 gap-1.5">
                      <ShieldAlert className="w-7 h-7 text-red-300" />
                      <span className="text-xs font-bold text-white">Unavailable</span>
                    </div>
                  )}

                  {/* Remove button */}
                  <button
                    onClick={() => removeMutation.mutate(item.id)}
                    className="absolute top-2 right-2 w-8 h-8 rounded-full bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm flex items-center justify-center text-red-500 hover:bg-white hover:scale-110 transition-all shadow-xs"
                    aria-label="Remove from wishlist"
                  >
                    <Heart className="w-4 h-4 fill-red-500" />
                  </button>
                </div>

                <div className="p-4 space-y-2">
                  <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm line-clamp-1">
                    {listing.listing_title || 'Surplus Food Bag'}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                    {listing.business?.business_name || 'Artisan Food Merchant'}
                  </p>

                  {isUnavailable ? (
                    <div className="pt-1 space-y-1.5">
                      <div className="flex items-center gap-1.5 text-xs text-red-600 dark:text-red-400 font-medium">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        This item is currently unavailable
                      </div>
                      <p className="text-[10px] text-slate-400">This listing was removed from the marketplace. You can remove it from your wishlist.</p>
                      <button
                        onClick={() => removeMutation.mutate(item.id)}
                        className="text-[10px] text-red-500 hover:underline mt-1"
                      >
                        Remove from wishlist
                      </button>
                    </div>
                  ) : (
                    <>
                      <PriceBadge
                        originalPrice={Number(listing.original_price || 0)}
                        discountedPrice={Number(listing.discounted_price || 0)}
                        size="sm"
                      />
                      <Link to={`/customer/listing/${item.listing.id}`} className="flex-1">
                        <Button
                          variant={activeHoldListingIds.has(item.listing.id) || item.listing.quantity_available <= 0 || item.listing.listing_status !== 'PUBLISHED' ? 'secondary' : 'primary'}
                          disabled={activeHoldListingIds.has(item.listing.id) || item.listing.quantity_available <= 0 || item.listing.listing_status !== 'PUBLISHED'}
                          size="sm"
                          className="w-full"
                        >
                          {activeHoldListingIds.has(item.listing.id) ? 'Already Reserved (15m Hold)' : item.listing.quantity_available <= 0 || item.listing.listing_status !== 'PUBLISHED' ? 'Sold Out' : 'Reserve Now'}
                        </Button>
                      </Link>
                    </>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default WishlistPage;
