import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, MapPin, Clock, ShieldCheck, Star, MessageSquare, Send, ShieldAlert } from 'lucide-react';
import { marketplaceApi } from '../api/marketplaceApi';
import { ordersApi } from '../../orders/api/ordersApi';
import { PriceBadge } from '../../../components/ui/PriceBadge';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { Dialog } from '../../../components/ui/Dialog';
import { SkeletonDetail } from '../../../components/ui/Skeleton';
import { useToastStore } from '../../../stores/useToastStore';
import { useAuthStore } from '../../../stores/useAuthStore';
import { formatDateTime, getTimeUntil } from '../../../lib/utils';

// Component: ListingDetailPage
const ListingDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();
  const [claimModalOpen, setClaimModalOpen] = useState(false);
  const [createdOrder, setCreatedOrder] = useState(null);
  const { user } = useAuthStore();

  // Review Form state
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState('');

  const { data: listing, isLoading } = useQuery({
    queryKey: ['marketplace', 'detail', id],
    queryFn: () => marketplaceApi.getListing(id),
    enabled: !!id,
  });

  const { data: reviews, isLoading: reviewsLoading } = useQuery({
    queryKey: ['marketplace', 'reviews', id],
    queryFn: () => marketplaceApi.getListingReviews(id),
    enabled: !!id,
  });

  const { data: customerOrders } = useQuery({
    queryKey: ['orders', 'customer'],
    queryFn: () => ordersApi.getCustomerOrders(),
  });

  const isAlreadyReserved = (customerOrders || []).some(
    (o) => (o.listing?.id === id || o.listing === id) && (o.status === 'PENDING' || o.order_status === 'PENDING')
  );

  const reserveMutation = useMutation({
    mutationFn: (coords) => ordersApi.createOrder(id, 1, 0, coords?.lat, coords?.lon),
    onSuccess: (data) => {
      setCreatedOrder(data);
      setClaimModalOpen(true);
      addToast({ title: 'Reservation confirmed!', description: 'Claim code generated.', variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['marketplace'] });
      queryClient.invalidateQueries({ queryKey: ['orders', 'customer'] });
    },
    onError: (err) => {
      addToast({ title: 'Reservation failed', description: err?.response?.data?.detail ?? 'Item may no longer be available.', variant: 'error' });
    },
  });

  // Function: handleReserve
  const handleReserve = () => {
    // If the user is an NGO claiming a donation, skip location entirely
    if (user?.role === 'NGO' || user?.account_type === 'NGO') {
      reserveMutation.mutate({});
      return;
    }

    // Check for user's default saved address first
    try {
      const storageKey = user ? `fw_saved_addresses_${user.id || user.email}` : 'fw_saved_addresses_guest';
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const addresses = JSON.parse(stored);
        const defaultAddr = addresses.find(a => a.isDefault);
        if (defaultAddr && (defaultAddr.lat || defaultAddr.latitude) && (defaultAddr.lng || defaultAddr.longitude)) {
          const lat = defaultAddr.lat || defaultAddr.latitude;
          const lon = defaultAddr.lng || defaultAddr.longitude;
          reserveMutation.mutate({ lat, lon });
          return;
        }
      }
    } catch (e) {
      console.warn('Could not parse saved addresses', e);
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          reserveMutation.mutate({ lat: position.coords.latitude, lon: position.coords.longitude });
        },
        (error) => {
          // If the user denies location or it fails, try to reserve without coordinates
          // The backend will enforce location strictly, so this will likely trigger the distance error
          reserveMutation.mutate({});
        },
        { timeout: 5000 }
      );
    } else {
      reserveMutation.mutate({});
    }
  };

  const reviewMutation = useMutation({
    mutationFn: (data) => marketplaceApi.createReview(data),
    onSuccess: () => {
      addToast({ title: 'Review Submitted!', description: 'Thank you for rating this verified surplus purchase.', variant: 'success' });
      setReviewText('');
      queryClient.invalidateQueries({ queryKey: ['marketplace', 'reviews', id] });
    },
    onError: (err) => {
      const msg = err?.response?.data?.detail || err?.response?.data?.non_field_errors?.[0] || 'You can only review listings you have completed an order for.';
      addToast({ title: 'Review Submission Failed', description: msg, variant: 'error' });
    },
  });

  // Function: handleReviewSubmit
  const handleReviewSubmit = (e) => {
    e.preventDefault();
    if (!reviewText.trim()) return;
    reviewMutation.mutate({
      listing: id,
      rating,
      review: reviewText.trim(),
    });
  };

  if (isLoading) {
    return <div className="p-6 max-w-5xl mx-auto"><SkeletonDetail /></div>;
  }

  if (!listing) {
    return (
      <div className="p-12 text-center">
        <p className="text-slate-500 mb-4">Listing not found or expired.</p>
        <Link to="/customer/browse"><Button variant="outline">Back to browse</Button></Link>
      </div>
    );
  }

  const isUnavailable = listing.listing_status === 'UNPUBLISHED';
  if (isUnavailable) {
    return (
      <div className="p-6 max-w-5xl mx-auto">
        <Link to="/customer/browse" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 mb-6">
          <ArrowLeft className="w-4 h-4" /> Back to browse
        </Link>
        <div className="rounded-2xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30 p-10 flex flex-col items-center text-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-red-100 dark:bg-red-900/60 flex items-center justify-center">
            <ShieldAlert className="w-8 h-8 text-red-500" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-red-800 dark:text-red-200">This Listing is Unavailable</h2>
            <p className="text-sm text-red-600 dark:text-red-400 mt-2 max-w-sm">
              This item has been temporarily removed from the marketplace by our moderation team.
              Please browse other available surplus food items.
            </p>
          </div>
          <Link to="/customer/browse">
            <Button variant="primary">Browse Available Items</Button>
          </Link>
        </div>
      </div>
    );
  }

  const time = getTimeUntil(listing.expires_at);

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">
      <Link to="/customer/browse" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-200">
        <ArrowLeft className="w-4 h-4" /> Back to browse
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Image */}
        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-slate-100 dark:bg-slate-900 h-80 lg:h-96 relative">
          {listing.image ? (
            <img src={listing.image} alt={listing.listing_title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-slate-300 dark:text-slate-600">
              <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            </div>
          )}
          <div className="absolute top-3 left-3 flex gap-2">
            {listing.is_featured && <Badge variant="info" label="Featured" />}
            {listing.visible_to_ngos && <Badge variant="ngo" label="NGO-Visible" />}
          </div>
        </div>

        {/* Right: Info */}
        <div className="space-y-5">
          <div>
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">
              {listing.business?.business_type}
            </span>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-1 mb-2">
              {listing.listing_title}
            </h1>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <MapPin className="w-4 h-4 text-slate-400" />
              <span>{listing.business?.business_name}</span>
              {listing.business?.is_verified && (
                <span className="inline-flex items-center gap-0.5 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                  <ShieldCheck className="w-3.5 h-3.5" /> Verified
                </span>
              )}
            </div>
          </div>

          <PriceBadge
            originalPrice={Number(listing.original_price)}
            discountedPrice={Number(listing.discounted_price)}
            pricingStrategy={listing.pricing_strategy}
          />

          {/* Environmental Footprint Impact Card */}
          <div className="rounded-xl bg-emerald-50/70 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-300 flex items-center justify-center font-bold text-lg">
                🌱
              </div>
              <div>
                <p className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider">Environmental Rescue Impact</p>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                  Rescuing this item prevents <span className="text-emerald-600 dark:text-emerald-400 font-bold">2.4 kg CO₂e</span> emissions & saves <span className="text-sky-600 dark:text-sky-400 font-bold">240 L</span> water
                </p>
              </div>
            </div>
          </div>

          {/* Expiry clock */}
          <div className="rounded-xl bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-900/30 p-4 flex items-center gap-3">
            <Clock className="w-5 h-5 text-amber-600 flex-shrink-0" />
            <div>
              <p className="text-xs font-semibold text-amber-800 dark:text-amber-400">Shelf-Life Countdown</p>
              <p className="text-sm font-medium text-slate-800 dark:text-slate-200 tabular-nums">
                {time.expired ? 'Expired' : `${time.hours}h ${time.minutes}m ${time.seconds}s left`} (Expires {formatDateTime(listing.expires_at)})
              </p>
            </div>
          </div>

          {listing.description && (
            <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{listing.description}</p>
          )}

          <div className="pt-2 flex gap-3">
            <Button
              variant={isAlreadyReserved || time.expired || listing.quantity_available === 0 || listing.listing_status !== 'PUBLISHED' ? 'secondary' : 'primary'}
              size="lg"
              className="flex-1"
              disabled={isAlreadyReserved || time.expired || listing.quantity_available === 0 || listing.listing_status !== 'PUBLISHED'}
              loading={reserveMutation.isPending}
              onClick={handleReserve}
            >
              {isAlreadyReserved
                ? 'Already Reserved (15m Hold Active)'
                : listing.listing_status !== 'PUBLISHED'
                ? 'Unavailable'
                : listing.quantity_available === 0
                ? 'Sold Out'
                : 'Reserve Now'}
            </Button>
          </div>
        </div>
      </div>

      {/* Feature 5: Customer Reviews & Rating Section */}
      <div className="pt-8 border-t border-slate-200 dark:border-slate-800 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Verified Customer Reviews</h2>
          </div>
          <span className="text-xs font-semibold text-slate-500 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-full">
            {reviews?.length || 0} Reviews
          </span>
        </div>

        {/* Review Form (Restricted by Backend to Verified Purchasers) */}
        <form onSubmit={handleReviewSubmit} className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/60 rounded-2xl p-5 space-y-4">
          <div>
            <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Have you purchased this item? Leave a Review!</h4>
            <p className="text-xs text-slate-500">Only verified customers with completed orders for this listing can post reviews.</p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">Your Rating:</span>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  onClick={() => setRating(star)}
                  className="p-1 hover:scale-110 transition-transform"
                >
                  <Star className={`w-5 h-5 ${star <= rating ? 'text-amber-400 fill-amber-400' : 'text-slate-300 dark:text-slate-600'}`} />
                </button>
              ))}
            </div>
          </div>

          <textarea
            rows={3}
            placeholder="Write your honest review here (e.g. food freshness, portion size, pickup experience)..."
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            className="w-full p-3 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="indigo"
              size="sm"
              isLoading={reviewMutation.isPending}
              disabled={!reviewText.trim()}
              leftIcon={<Send className="w-3.5 h-3.5" />}
            >
              Post Review
            </Button>
          </div>
        </form>

        {/* Existing Reviews List */}
        {reviewsLoading ? (
          <div className="text-xs text-slate-400">Loading reviews...</div>
        ) : !reviews?.length ? (
          <div className="p-6 text-center bg-slate-50/50 dark:bg-slate-900/50 rounded-2xl border border-slate-100 dark:border-slate-800 text-slate-500 text-xs">
            No customer reviews yet. Be the first verified purchaser to leave a review!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reviews.map((rev) => (
              <div key={rev.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 space-y-2 shadow-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`w-4 h-4 ${star <= rev.rating ? 'text-amber-400 fill-amber-400' : 'text-slate-200 dark:text-slate-700'}`}
                      />
                    ))}
                  </div>
                  <span className="text-[10px] text-emerald-600 font-bold bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded">
                    Verified Buyer
                  </span>
                </div>
                <p className="text-xs text-slate-700 dark:text-slate-300">{rev.review}</p>
                <p className="text-[10px] text-slate-400">{formatDateTime(rev.created_at)}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Claim code modal */}
      <Dialog
        open={claimModalOpen}
        onClose={() => { setClaimModalOpen(false); navigate('/customer/orders'); }}
        title="Reservation Confirmed!"
        description="Present this claim code to the merchant upon arrival."
        size="sm"
      >
        <div className="text-center py-4 space-y-4">
          <div className="rounded-2xl bg-gradient-to-b from-emerald-50 to-teal-50/60 dark:from-emerald-950/60 dark:to-slate-900 border border-emerald-200/80 dark:border-emerald-800/80 p-5 flex flex-col items-center shadow-sm">
            <p className="text-xs uppercase font-bold text-emerald-700 dark:text-emerald-300 mb-1">Your Pickup Claim Code</p>
            {createdOrder?.claim_code ? (
              <p className="text-3xl font-mono font-black text-emerald-800 dark:text-emerald-200 tracking-wider">
                #{createdOrder.claim_code}
              </p>
            ) : (
              <div className="h-9 w-28 bg-slate-200 dark:bg-slate-700 animate-pulse rounded my-1" />
            )}

            {createdOrder?.claim_code && (
              <div className="my-3 p-2 bg-white rounded-xl shadow-xs border border-emerald-100 dark:border-slate-800">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=130x130&data=${encodeURIComponent(createdOrder.claim_code)}`}
                  alt="Claim QR Code"
                  className="w-28 h-28 object-contain rounded-md"
                />
              </div>
            )}

            <div className="text-[11px] font-semibold text-amber-700 dark:text-amber-300 bg-amber-100/70 dark:bg-amber-950/70 px-3 py-1 rounded-full flex items-center justify-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              <span>15-Minute Pickup Hold Active</span>
            </div>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Show this QR code or 6-digit claim code at {listing.business?.business_name} upon arrival.
          </p>
          <Button variant="primary" className="w-full" onClick={() => { setClaimModalOpen(false); navigate('/customer/orders'); }}>
            View My Orders
          </Button>
        </div>
      </Dialog>
    </div>
  );
};

export default ListingDetailPage;
