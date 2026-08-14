import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { MapPin, Heart, List, Map, Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import { marketplaceApi } from '../api/marketplaceApi';
import { PriceBadge } from '../../../components/ui/PriceBadge';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { EmptyState } from '../../../components/ui/EmptyState';
import { SkeletonCardGrid } from '../../../components/ui/Skeleton';
import { LiveMapPicker } from '../../../components/ui/LiveMapPicker';
import { useToastStore } from '../../../stores/useToastStore';
import { getTimeUntil, getListingCoordinates } from '../../../lib/utils';

import { ordersApi } from '../../orders/api/ordersApi';

const CATEGORIES = ['All', 'Bakery', 'Prepared Meals', 'Produce', 'Dairy', 'Beverages'];

// Component: CountdownTimer
const CountdownTimer = ({ expiresAt }) => {
  const [time, setTime] = useState(() => getTimeUntil(expiresAt));
  useEffect(() => {
    const id = setInterval(() => setTime(getTimeUntil(expiresAt)), 1000);
    return () => clearInterval(id);
  }, [expiresAt]);
  if (time.expired) return <span className="text-red-500 text-xs font-medium">Expired</span>;
  return (
    <span className="tabular-nums text-xs font-medium text-amber-600 dark:text-amber-400">
      ⏱ {String(time.hours).padStart(2,'0')}h {String(time.minutes).padStart(2,'0')}m {String(time.seconds).padStart(2,'0')}s
    </span>
  );
};

// Component: ListingCard
const ListingCard = ({ listing, onWishlist, isSaved, isReserved }) => (
  <motion.div
    layout
    layoutId={`listing-${listing.id}`}
    initial={{ opacity: 0, y: 16 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
    className="group bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden cursor-pointer shadow-sm hover:shadow-lg transition-shadow duration-200"
  >
    <Link to={`/customer/listing/${listing.id}`} className="block">
      <div className="relative h-44 bg-slate-100 dark:bg-slate-800 overflow-hidden">
        {listing.image ? (
          <img
            src={listing.image}
            alt={listing.listing_title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-300 dark:text-slate-600">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
          </div>
        )}
        <div className="absolute top-2 left-2 flex gap-1.5">
          {listing.is_featured && <Badge variant="info" label="Featured" />}
          {listing.visible_to_ngos && <Badge variant="ngo" label="NGO" />}
          {listing.listing_type === 'DONATION' && <Badge variant="ngo" label="FREE" />}
        </div>
        <div className="absolute bottom-2 right-2">
          <CountdownTimer expiresAt={listing.expires_at} />
        </div>
      </div>

      <div className="p-4">
        <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm leading-snug mb-1 line-clamp-2">{listing.listing_title}</h3>
        <div className="flex items-center gap-1 text-xs text-slate-400 mb-2">
          <MapPin className="w-3.5 h-3.5" />
          <span>{listing.business?.business_name}</span>
          {listing.branch?.address && (
            <span>· {listing.branch.address.city}</span>
          )}
        </div>

        {/* Environmental Footprint Impact Badge */}
        <div className="mb-3 inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200/60 dark:border-emerald-800/60 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300">
          <span>🌱 {((listing.quantity_available || 1) * 1.5).toFixed(1)} kg CO₂ saved</span>
          <span>·</span>
          <span>💧 {Math.round((listing.quantity_available || 1) * 150)}L water</span>
        </div>

        <div className="flex items-end justify-between">
          <PriceBadge
            originalPrice={Number(listing.original_price)}
            discountedPrice={Number(listing.discounted_price)}
            pricingStrategy={listing.pricing_strategy}
            size="sm"
          />
          <span className="text-xs text-slate-400 tabular-nums">{listing.quantity_available} left</span>
        </div>
      </div>
    </Link>

    <div className="px-4 pb-4 flex gap-2">
      <Link to={`/customer/listing/${listing.id}`} className="flex-1">
        <Button
          variant={isReserved || listing.quantity_available <= 0 || listing.listing_status !== 'PUBLISHED' ? 'secondary' : 'primary'}
          disabled={isReserved || listing.quantity_available <= 0 || listing.listing_status !== 'PUBLISHED'}
          size="sm"
          className="w-full"
        >
          {isReserved ? 'Already Reserved (15m Hold)' : listing.quantity_available <= 0 || listing.listing_status !== 'PUBLISHED' ? 'Sold Out' : 'Reserve Now'}
        </Button>
      </Link>
      <button
        onClick={(e) => { e.stopPropagation(); onWishlist(listing.id); }}
        className={`p-2 rounded-lg border transition-colors ${
          isSaved
            ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-950/30 text-red-500'
            : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-400 hover:text-red-500'
        }`}
        aria-label={isSaved ? 'Remove from wishlist' : 'Save to wishlist'}
        title={isSaved ? 'Remove from wishlist' : 'Save to wishlist'}
      >
        <Heart className={`w-4 h-4 ${isSaved ? 'fill-red-500' : ''}`} />
      </button>
    </div>
  </motion.div>
);

// Component: BrowseMarketplacePage
const BrowseMarketplacePage = () => {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [viewMode, setViewMode] = useState('list');
  const { addToast } = useToastStore();
  const qc = useQueryClient();

  const { data: customerOrders } = useQuery({
    queryKey: ['orders', 'customer'],
    queryFn: () => ordersApi.getCustomerOrders(),
  });

  const activeHoldListingIds = new Set(
    (customerOrders || [])
      .filter((o) => (o.status === 'PENDING' || o.order_status === 'PENDING'))
      .map((o) => o.listing?.id || o.listing)
  );

  const { data: listings, isLoading } = useQuery({
    queryKey: ['marketplace', 'listings', { search }],
    queryFn: () => marketplaceApi.getPublicListings({ search }),
  });

  const filteredListings = (listings || []).filter((listing) => {
    // Exclude listings from SUSPENDED or REJECTED businesses
    const bizStatus = listing.business?.business_status;
    if (bizStatus === 'SUSPENDED' || bizStatus === 'REJECTED') {
      return false;
    }
    if (listing.listing_status === 'UNPUBLISHED' || listing.listing_status === 'EXPIRED') {
      return false;
    }

    if (category === 'All') return true;
    const catLower = category.toLowerCase();
    const title = (listing.listing_title || '').toLowerCase();
    const prodName = (listing.product?.name || listing.product?.product_name || '').toLowerCase();
    const prodCat = (listing.product?.category?.name || listing.product?.category || '').toLowerCase();

    if (catLower.includes('bakery')) {
      return prodCat.includes('bakery') || title.includes('croissant') || title.includes('bread') || title.includes('bakery') || title.includes('pastry') || prodName.includes('bread') || prodName.includes('croissant');
    }
    if (catLower.includes('meal') || catLower.includes('prepared')) {
      return prodCat.includes('meal') || prodCat.includes('prepared') || title.includes('meal') || title.includes('salad') || title.includes('bowl') || title.includes('box') || prodName.includes('salad');
    }
    if (catLower.includes('produce') || catLower.includes('fruit') || catLower.includes('veg')) {
      return prodCat.includes('produce') || prodCat.includes('veg') || title.includes('apple') || title.includes('fruit') || title.includes('garden') || title.includes('produce');
    }
    if (catLower.includes('dairy') || catLower.includes('milk') || catLower.includes('cheese')) {
      return prodCat.includes('dairy') || title.includes('milk') || title.includes('cheese') || title.includes('yogurt') || title.includes('butter');
    }
    if (catLower.includes('beverage') || catLower.includes('drink')) {
      return prodCat.includes('beverage') || title.includes('juice') || title.includes('coffee') || title.includes('tea') || title.includes('smoothie');
    }
    return prodCat.includes(catLower) || title.includes(catLower);
  });

  const { data: wishlistData } = useQuery({
    queryKey: ['marketplace', 'wishlist'],
    queryFn: marketplaceApi.getWishlist,
  });

  // Build a set of listing IDs that are already in the wishlist for quick lookup
  const savedListingIds = new Set(
    (wishlistData || []).map((item) => {
      // item.listing_details?.id (if nested) or item.listing (UUID string)
      if (item.listing_details?.id) return item.listing_details.id;
      if (typeof item.listing === 'string') return item.listing;
      if (typeof item.listing === 'object') return item.listing?.id;
      return null;
    }).filter(Boolean)
  );

  const wishlistMutation = useMutation({
    mutationFn: marketplaceApi.addToWishlist,
    onSuccess: (_, listingId) => {
      const isNowSaved = !savedListingIds.has(listingId);
      addToast({
        title: isNowSaved ? '❤️ Saved to Wishlist' : 'Removed from Wishlist',
        description: isNowSaved ? 'Find it under Saved Items anytime.' : 'Item removed from your saved list.',
        variant: isNowSaved ? 'success' : 'info',
      });
      qc.invalidateQueries({ queryKey: ['marketplace', 'wishlist'] });
    },
    onError: () => {
      addToast({ title: 'Could not update wishlist', variant: 'error' });
    },
  });

  return (
    <div className="flex flex-col h-full">
      <div className="sticky top-0 z-10 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 sm:px-6 py-4 space-y-3">
        <div className="flex gap-3">
          <div className="flex-1">
            <Input
              placeholder="Search surplus food nearby..."
              prefixIcon={<Search className="w-4 h-4" />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex gap-1 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
            <button
              onClick={() => setViewMode('list')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${viewMode === 'list' ? 'bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 shadow-sm' : 'text-slate-500'}`}
              aria-pressed={viewMode === 'list'}
            >
              <List className="w-3.5 h-3.5" /> List
            </button>
            <button
              onClick={() => setViewMode('map')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${viewMode === 'map' ? 'bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 shadow-sm' : 'text-slate-500'}`}
              aria-pressed={viewMode === 'map'}
            >
              <Map className="w-3.5 h-3.5" /> Map
            </button>
          </div>
        </div>
        <div className="flex gap-2 overflow-x-auto pb-0.5 no-scrollbar" role="list" aria-label="Category filters">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              role="listitem"
              className={`flex-shrink-0 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                category === cat
                  ? 'bg-emerald-600 text-white border-emerald-600'
                  : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-300'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        {isLoading ? (
          <SkeletonCardGrid count={6} />
        ) : filteredListings.length === 0 ? (
          <EmptyState
            icon={<Search className="w-8 h-8 text-emerald-600" />}
            title={category === 'All' ? "No surplus listings found nearby" : `No ${category} surplus listings available right now`}
            description={
              category === 'All'
                ? "No active surplus food listings found in your area right now. Try expanding your search or check back near store closing hours."
                : `Surplus ${category.toLowerCase()} items sell out quickly! Check back near merchant closing hours or browse all nearby surplus food.`
            }
            action={
              category !== 'All' ? (
                <Button variant="primary" size="sm" onClick={() => setCategory('All')}>
                  Browse All Surplus Food
                </Button>
              ) : null
            }
          />
        ) : viewMode === 'map' ? (
          <div className="h-full min-h-[550px] w-full rounded-2xl overflow-hidden shadow-lg border border-slate-200 dark:border-slate-800">
            <LiveMapPicker
              height="580px"
              allowSearch={true}
              allowLiveTracking={true}
              markers={filteredListings.map((l) => {
                const { lat, lng } = getListingCoordinates(l);

                return {
                  id: l.id,
                  title: l.listing_title,
                  businessName: l.business?.business_name || 'Artisan Food Merchant',
                  type: l.listing_type || (l.discounted_price === '0.00' ? 'DONATION' : 'SURPLUS'),
                  priceLabel: l.listing_type === 'DONATION' || Number(l.discounted_price) === 0 ? 'FREE NGO' : `₹${Number(l.discounted_price).toFixed(2)}`,
                  originalPrice: l.original_price ? `₹${Number(l.original_price).toFixed(2)}` : null,
                  lat,
                  lng,
                  image: l.image,
                  link: `/customer/listing/${l.id}`,
                };
              })}
            />
          </div>
        ) : (
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4"
            initial="hidden"
            animate="show"
            variants={{ hidden: {}, show: { transition: { staggerChildren: 0.04 } } }}
          >
            {filteredListings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                onWishlist={wishlistMutation.mutate}
                isSaved={savedListingIds.has(listing.id)}
                isReserved={activeHoldListingIds.has(listing.id)}
              />
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default BrowseMarketplacePage;
