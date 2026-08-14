import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, MapPin, Navigation, ExternalLink, Heart, Route, Truck, Check, Plus } from 'lucide-react';
import { ordersApi } from '../../orders/api/ordersApi';
import { donationsApi } from '../api/donationsApi';
import { LiveMapPicker } from '../../../components/ui/LiveMapPicker';
import { Button } from '../../../components/ui/Button';
import { EmptyState } from '../../../components/ui/EmptyState';
import { SkeletonCardGrid } from '../../../components/ui/Skeleton';
import { formatDateTime, getListingCoordinates } from '../../../lib/utils';
import { useToastStore } from '../../../stores/useToastStore';

// Component: NgoPickupsPage
export const NgoPickupsPage = () => {
  const queryClient = useQueryClient();
  const addToast = useToastStore((state) => state.addToast);
  const [trackingOrder, setTrackingOrder] = useState(null);
  const [selectedPickupIds, setSelectedPickupIds] = useState([]);
  const [driverName, setDriverName] = useState('');
  const [routeDate, setRouteDate] = useState(new Date().toISOString().split('T')[0]);
  const [activeTab, setActiveTab] = useState('pickups'); // 'pickups' | 'routes'

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders', 'ngo', 'pickups'],
    queryFn: ordersApi.getCustomerOrders,
  });

  const { data: routes, isLoading: routesLoading } = useQuery({
    queryKey: ['donations', 'routes'],
    queryFn: () => donationsApi.getPickupRoutes(),
  });

  const createRouteMutation = useMutation({
    mutationFn: (data) => donationsApi.createPickupRoute(data),
    onSuccess: () => {
      addToast('Multi-stop pickup route generated successfully!', 'success');
      setSelectedPickupIds([]);
      setDriverName('');
      queryClient.invalidateQueries({ queryKey: ['donations', 'routes'] });
    },
    onError: (err) => {
      addToast(err?.response?.data?.detail || 'Failed to create route.', 'error');
    },
  });

  // Function: toggleSelectPickup
  const toggleSelectPickup = (id) => {
    setSelectedPickupIds((prev) =>
      prev.includes(id) ? prev.filter((pId) => pId !== id) : [...prev, id]
    );
  };

  // Function: handleCreateRoute
  const handleCreateRoute = (e) => {
    e.preventDefault();
    if (!selectedPickupIds.length) {
      addToast('Select at least one pickup to batch into a route.', 'error');
      return;
    }
    createRouteMutation.mutate({
      pickup_ids: selectedPickupIds,
      route_date: routeDate,
      driver_name: driverName || 'Default Driver',
    });
  };

  const isLoading = ordersLoading || routesLoading;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            NGO Food Rescue Pickups & Route Planning
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage your claimed surplus food donations and optimize multi-stop pickup routes by proximity.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('pickups')}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-colors ${
              activeTab === 'pickups'
                ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Claimed Pickups ({orders?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('routes')}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-colors ${
              activeTab === 'routes'
                ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Batched Routes ({routes?.length || 0})
          </button>
        </div>
      </div>

      {activeTab === 'pickups' && (
        <>
          {/* Route Batching Header Action */}
          {orders && orders.length > 0 && (
            <form onSubmit={handleCreateRoute} className="bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 p-4 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold">
                  <Route className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">Batch Selected Pickups into Route</h4>
                  <p className="text-xs text-slate-500">Select checkboxes below to automatically generate an optimized multi-stop route.</p>
                </div>
              </div>
              <div className="flex items-center gap-3 w-full md:w-auto">
                <input
                  type="text"
                  placeholder="Driver Name (Optional)"
                  value={driverName}
                  onChange={(e) => setDriverName(e.target.value)}
                  className="px-3 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100"
                />
                <input
                  type="date"
                  value={routeDate}
                  onChange={(e) => setRouteDate(e.target.value)}
                  className="px-3 py-1.5 text-xs rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100"
                />
                <Button
                  type="submit"
                  variant="indigo"
                  size="sm"
                  isLoading={createRouteMutation.isPending}
                  disabled={!selectedPickupIds.length}
                  leftIcon={<Plus className="w-4 h-4" />}
                >
                  Create Route ({selectedPickupIds.length})
                </Button>
              </div>
            </form>
          )}

          {isLoading ? (
            <SkeletonCardGrid count={3} />
          ) : !orders?.length ? (
            <EmptyState
              icon={<Heart className="w-8 h-8 text-indigo-600" />}
              title="No active donation pickups"
              description="Your organization has not claimed any surplus food donations yet. Browse free listings to start rescuing food."
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {orders.map((order) => {
                const { lat, lng } = getListingCoordinates(order.listing);
                const bizName = order.listing?.business?.business_name || 'Donor Merchant';
                const isSelected = selectedPickupIds.includes(order.id);

                return (
                  <motion.div
                    key={order.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`bg-white dark:bg-slate-900 rounded-2xl border ${
                      isSelected ? 'border-indigo-500 ring-2 ring-indigo-500/20' : 'border-slate-200 dark:border-slate-800'
                    } p-5 shadow-sm space-y-4 flex flex-col justify-between relative`}
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleSelectPickup(order.id)}
                            className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                          />
                          <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                            FREE NGO DONATION
                          </span>
                        </label>
                        <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">
                          #{order.claim_code}
                        </span>
                      </div>

                      <div>
                        <h3 className="font-bold text-slate-900 dark:text-slate-100 text-base leading-snug">
                          {order.listing?.listing_title || 'Surplus Food Rescue Package'}
                        </h3>
                        <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
                          <MapPin className="w-3.5 h-3.5 text-indigo-500" />
                          <span className="font-semibold text-slate-700 dark:text-slate-300">{bizName}</span>
                        </div>
                      </div>

                      <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 space-y-1.5 text-xs">
                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                          <span>Claimed On:</span>
                          <span className="font-medium">{formatDateTime(order.created_at)}</span>
                        </div>
                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                          <span>Hold Expires:</span>
                          <span className="font-medium text-amber-600 dark:text-amber-400">
                            {order.claim_expires_at ? formatDateTime(order.claim_expires_at) : '15-Min Window'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="pt-2 flex flex-col gap-2">
                      <Button
                        variant="indigo"
                        size="sm"
                        className="w-full"
                        leftIcon={<Navigation className="w-4 h-4" />}
                        onClick={() => setTrackingOrder(order)}
                      >
                        🎯 Live Route Map & GPS
                      </Button>
                      <a
                        href={`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors no-underline"
                      >
                        <ExternalLink className="w-3.5 h-3.5 text-indigo-500" /> Open in Google Maps
                      </a>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </>
      )}

      {activeTab === 'routes' && (
        <div className="space-y-4">
          {isLoading ? (
            <SkeletonCardGrid count={2} />
          ) : !routes?.length ? (
            <EmptyState
              icon={<Truck className="w-8 h-8 text-indigo-600" />}
              title="No batched routes yet"
              description="Switch to the Claimed Pickups tab to batch scheduled pickups into a multi-stop route."
            />
          ) : (
            <div className="space-y-4">
              {routes.map((route) => (
                <div key={route.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 flex items-center justify-center font-bold">
                        <Truck className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-900 dark:text-slate-100 text-sm">
                          Route #{route.id.slice(0, 8)} • Driver: {route.driver_name || 'Unassigned'}
                        </h4>
                        <p className="text-xs text-slate-500">Route Date: {route.route_date}</p>
                      </div>
                    </div>
                    <span className="text-xs font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-950/80 px-3 py-1 rounded-full">
                      {(route.pickups?.length || 0) + (route.marketplace_orders?.length || 0)} Proximity-Ordered Stops
                    </span>
                  </div>

                  <div className="space-y-2">
                    {[...(route.pickups || []), ...(route.marketplace_orders || [])].map((p, idx) => (
                      <div key={p.id || p || idx} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-[10px]">
                            {idx + 1}
                          </span>
                          <span className="font-semibold text-slate-800 dark:text-slate-200">
                            Stop {idx + 1}: Pickup #{typeof p === 'string' ? p.slice(0, 8) : p.id?.slice(0, 8)}
                          </span>
                        </div>
                        <span className="text-emerald-600 font-medium">Scheduled</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Live Route Map Modal */}
      <AnimatePresence>
        {trackingOrder && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-2xl m-auto max-h-[85vh] flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden"
            >
              <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-slate-100 text-base">
                    Live Merchant GPS Navigation
                  </h3>
                  <p className="text-xs text-slate-500">
                    {trackingOrder.listing?.business?.business_name || 'Donor Merchant Store'}
                  </p>
                </div>
                <button
                  onClick={() => setTrackingOrder(null)}
                  className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  ✕
                </button>
              </div>

              <div className="p-5 overflow-y-auto space-y-4">
                <div className="h-64 rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800">
                  <LiveMapPicker
                    latitude={getListingCoordinates(trackingOrder.listing).lat}
                    longitude={getListingCoordinates(trackingOrder.listing).lng}
                    readOnly
                  />
                </div>

                <div className="p-4 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-800 space-y-1">
                  <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300">
                    Pickup Claim Verification Code
                  </span>
                  <p className="text-2xl font-mono font-extrabold text-indigo-600 dark:text-indigo-400">
                    #{trackingOrder.claim_code}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Show this 6-digit claim code to merchant staff upon arrival at the pickup counter.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NgoPickupsPage;
