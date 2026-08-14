import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, MapPin, Clock, Navigation, Store, ExternalLink, Award, Truck, CheckCircle, ShieldCheck } from 'lucide-react';
import { ordersApi } from '../api/ordersApi';
import { StatusBadge } from '../../../components/ui/Badge';
import { SkeletonCardGrid } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { LiveMapPicker } from '../../../components/ui/LiveMapPicker';
import { Button } from '../../../components/ui/Button';
import { formatCurrency, formatDateTime, getListingCoordinates } from '../../../lib/utils';
import { useAuthStore } from '../../../stores/useAuthStore';

// Component: CustomerOrdersPage
const CustomerOrdersPage = () => {
  const [trackingOrder, setTrackingOrder] = useState(null);
  const [activeTab, setActiveTab] = useState('ALL');
  const user = useAuthStore((state) => state.user);

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders', 'customer', activeTab],
    queryFn: () => ordersApi.getCustomerOrders(activeTab !== 'ALL' ? { status: activeTab } : {}),
  });

  const { data: loyaltyData } = useQuery({
    queryKey: ['orders', 'loyalty', user?.id],
    queryFn: () => ordersApi.getCustomerLoyalty(user?.id),
    enabled: Boolean(user?.id),
  });

  const loyaltyPoints = loyaltyData?.loyalty_points || 0;
  const history = loyaltyData?.history || [];

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">My Orders & Live Pickups</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Track store pickup routes, view live GPS location, and check loyalty points.</p>
        </div>

        {/* Customer Loyalty Points Card */}
        <div className="bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-2xl p-4 shadow-sm flex items-center gap-4 w-full md:w-auto">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center font-bold">
            <Award className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-amber-100">Loyalty Rewards</span>
            <p className="text-xl font-extrabold tabular-nums">{loyaltyPoints} Points Available</p>
            <p className="text-[11px] text-amber-100">100 points = ₹100 discount</p>
          </div>
        </div>
      </div>

      {/* Status Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-800 flex gap-6">
        {['ALL', 'PENDING', 'COMPLETED', 'CANCELLED'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-3 text-sm font-semibold border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab.replace('_', ' ')}
          </button>
        ))}
      </div>

      {ordersLoading ? (
        <SkeletonCardGrid count={3} />
      ) : !orders?.length ? (
        <EmptyState
          icon={<ShoppingBag className="w-8 h-8" />}
          title="No active reservations"
          description="You haven't reserved any surplus food items yet. Browse nearby marketplace listings to rescue food."
        />
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            const isDelivery = order.order_type === 'DELIVERY' || Boolean(order.delivery);
            const delStatus = order.delivery?.status || (isDelivery ? 'PENDING' : null);

            return (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 flex flex-col md:flex-row gap-6 items-start md:items-center justify-between shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-2">
                    <StatusBadge status={order.order_status || order.status} />
                    {isDelivery && (
                      <span className="text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950/80 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800">
                        Delivery: {delStatus}
                      </span>
                    )}
                    <span className="text-xs text-slate-400 tabular-nums">Ordered {formatDateTime(order.created_at)}</span>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{order.listing?.listing_title}</h3>
                    <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
                      <Store className="w-4 h-4 text-emerald-600" />
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{order.listing?.business?.business_name || 'Partner Merchant'}</span>
                    </div>
                  </div>

                  {/* Delivery Timeline if Delivery Order */}
                  {isDelivery && (
                    <div className="p-3 rounded-2xl bg-sky-50/70 dark:bg-sky-950/40 border border-sky-100 dark:border-sky-900 space-y-2 text-xs">
                      <div className="flex items-center justify-between font-bold text-sky-900 dark:text-sky-300">
                        <span className="flex items-center gap-1.5"><Truck className="w-4 h-4" /> Delivery Status Tracker</span>
                        <span className="uppercase text-[10px] bg-sky-200 dark:bg-sky-900 text-sky-800 dark:text-sky-200 px-2 py-0.5 rounded">{delStatus}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-slate-600 dark:text-slate-400">
                        <span className={`w-2.5 h-2.5 rounded-full ${delStatus === 'PENDING' ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`} /> Order Pending
                        <span className="text-slate-300">→</span>
                        <span className={`w-2.5 h-2.5 rounded-full ${delStatus === 'DISPATCHED' ? 'bg-indigo-500 animate-pulse' : delStatus === 'DELIVERED' ? 'bg-emerald-500' : 'bg-slate-300'}`} /> Dispatched
                        <span className="text-slate-300">→</span>
                        <span className={`w-2.5 h-2.5 rounded-full ${delStatus === 'DELIVERED' ? 'bg-emerald-500 font-bold' : 'bg-slate-300'}`} /> Delivered
                      </div>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2 pt-2">
                    <Button
                      variant="primary"
                      size="sm"
                      leftIcon={<Navigation className="w-4 h-4" />}
                      onClick={() => setTrackingOrder(order)}
                      className="bg-emerald-600 hover:bg-emerald-700 text-white"
                    >
                      🎯 Live Track Pickup Route & Map
                    </Button>
                  </div>
                </div>

                {/* Claim Code Box */}
                <div className="rounded-2xl bg-gradient-to-b from-emerald-50 to-teal-50/60 dark:from-emerald-950/50 dark:to-slate-900 border border-emerald-200/80 dark:border-emerald-800/80 p-4 text-center min-w-48 flex flex-col items-center shadow-xs">
                  <p className="text-[11px] font-bold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider mb-1">Pickup Claim Code</p>
                  {order.claim_code ? (
                    <p className="text-2xl font-mono font-black text-emerald-800 dark:text-emerald-200 tracking-wider">
                      #{order.claim_code}
                    </p>
                  ) : (
                    <div className="h-8 w-24 bg-slate-200 dark:bg-slate-700 animate-pulse rounded my-1" />
                  )}

                  {order.claim_code && (
                    <div className="my-2.5 p-2 bg-white rounded-xl shadow-xs border border-emerald-100 dark:border-slate-800">
                      <img
                        src={`https://api.qrserver.com/v1/create-qr-code/?size=110x110&data=${encodeURIComponent(order.claim_code)}`}
                        alt={`QR Code #${order.claim_code}`}
                        className="w-24 h-24 object-contain rounded-md"
                      />
                    </div>
                  )}

                  <p className="text-xs text-slate-500 dark:text-slate-400 tabular-nums font-bold">{formatCurrency(Number(order.total_price || order.total_amount || 0))}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Live Tracking Modal */}
      <AnimatePresence>
        {trackingOrder && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-2xl m-auto max-h-[85vh] flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden"
            >
              <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex-shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                    <Navigation className="w-5 h-5 animate-pulse" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">Live Pickup Route & GPS Tracking</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Real-time route navigation to merchant pickup location</p>
                  </div>
                </div>
                <button
                  onClick={() => setTrackingOrder(null)}
                  className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 space-y-5 flex-1 overflow-y-auto min-h-0">
                <div className="p-4 rounded-2xl bg-emerald-50/80 dark:bg-emerald-950/40 border border-emerald-200/80 dark:border-emerald-800 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-extrabold uppercase bg-emerald-200 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200 px-2 py-0.5 rounded-md">
                      Active Pickup Hold
                    </span>
                    <h4 className="font-bold text-slate-900 dark:text-slate-100 text-base mt-1">
                      {trackingOrder.listing?.business?.business_name || 'Store Location'}
                    </h4>
                    <p className="text-xs text-slate-600 dark:text-slate-300">Item: {trackingOrder.listing?.listing_title}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] font-bold text-slate-400 uppercase">Claim Code</p>
                    <p className="font-mono font-black text-lg text-emerald-600 dark:text-emerald-400">#{trackingOrder.claim_code}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700 dark:text-slate-300">
                    <span className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-emerald-600" /> Interactive Route Map
                    </span>
                    <span className="text-[10px] text-emerald-600 font-mono">Distance: ~1.2 km</span>
                  </div>
                  
                  {(() => {
                    const { lat: storeLat, lng: storeLng } = getListingCoordinates(trackingOrder.listing);
                    const storeName = trackingOrder.listing?.business?.business_name || 'Pickup Store';

                    return (
                      <>
                        <LiveMapPicker
                          initialLat={storeLat}
                          initialLng={storeLng}
                          height="280px"
                          allowLiveTracking={true}
                          markers={[
                            { 
                              lat: storeLat, 
                              lng: storeLng, 
                              popupText: `Store: ${storeName}` 
                            }
                          ]}
                        />

                        <a
                          href={`https://www.google.com/maps/dir/?api=1&destination=${storeLat},${storeLng}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-full py-3 px-4 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center justify-center gap-2 transition-colors shadow-md"
                        >
                          <ExternalLink className="w-4 h-4" /> Open Turn-by-Turn GPS Navigation (Google Maps)
                        </a>
                      </>
                    );
                  })()}
                </div>
              </div>

              <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex justify-end">
                <Button variant="outline" size="sm" onClick={() => setTrackingOrder(null)}>
                  Close Map
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CustomerOrdersPage;
