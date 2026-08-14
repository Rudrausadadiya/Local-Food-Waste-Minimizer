import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Package, ShoppingBag, AlertTriangle, Plus, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useBranchStore } from '../../../stores/useBranchStore';
import { inventoryApi } from '../../inventory/api/inventoryApi';
import { ordersApi } from '../../orders/api/ordersApi';
import { Button } from '../../../components/ui/Button';
import { StatusBadge } from '../../../components/ui/Badge';
import { Skeleton } from '../../../components/ui/Skeleton';

// Component: MetricCard
const MetricCard = ({ label, value, sub, icon, color = 'emerald' }) => (
  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">
    <div className="flex items-start justify-between mb-3">
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
      <div className={`w-9 h-9 rounded-lg bg-${color}-100 dark:bg-${color}-900/20 flex items-center justify-center`}>
        {icon}
      </div>
    </div>
    <p className="text-2xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">{value}</p>
    {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
  </div>
);

// Component: VendorDashboardPage
const VendorDashboardPage = () => {
  const { activeBranchId } = useBranchStore();

  const { data: batches, isLoading: batchLoading } = useQuery({
    queryKey: ['inventory', activeBranchId ?? '', {}],
    queryFn: () => inventoryApi.getBatches(activeBranchId ?? ''),
    enabled: !!activeBranchId,
  });

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ['orders', 'vendor', activeBranchId ?? '', 'PENDING'],
    queryFn: () => ordersApi.getVendorOrders({ status: 'PENDING' }),
  });

  const expiringBatches = batches?.filter((b) => {
    const diff = new Date(b.expiry_date).getTime() - Date.now();
    return diff > 0 && diff < 12 * 3_600_000;
  }) ?? [];

  const container = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } };
  const item = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Vendor Dashboard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Your operational snapshot for today</p>
        </div>
        <Link to="/vendor/marketplace/new">
          <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>New Listing</Button>
        </Link>
      </div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4"
      >
        {[
          { label: 'Active Listings', value: batchLoading ? '—' : (batches?.length ?? 0), icon: <ShoppingBag className="w-5 h-5 text-emerald-600" />, color: 'emerald' },
          { label: 'Pending Pickups', value: ordersLoading ? '—' : (orders?.length ?? 0), icon: <Clock className="w-5 h-5 text-amber-600" />, color: 'amber', sub: 'Awaiting claim code' },
          { label: 'Expiring Soon', value: expiringBatches.length, icon: <AlertTriangle className="w-5 h-5 text-red-500" />, color: 'red', sub: 'Next 12 hours' },
          { label: 'Total Batches', value: batches?.length ?? '—', icon: <Package className="w-5 h-5 text-sky-600" />, color: 'sky' },
        ].map((card) => (
          <motion.div key={card.label} variants={item}>
            <MetricCard {...card} />
          </motion.div>
        ))}
      </motion.div>

      {expiringBatches.length > 0 && (
        <div className="bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <h2 className="text-sm font-semibold text-amber-800 dark:text-amber-400">Expiration Watch — Next 12 Hours</h2>
          </div>
          {expiringBatches.slice(0, 3).map((batch) => {
            const hoursLeft = Math.floor((new Date(batch.expiry_date).getTime() - Date.now()) / 3_600_000);
            const minsLeft = Math.floor(((new Date(batch.expiry_date).getTime() - Date.now()) % 3_600_000) / 60_000);
            return (
              <div key={batch.id} className="flex items-center justify-between gap-4 bg-white dark:bg-slate-900 rounded-lg p-3 border border-amber-100 dark:border-amber-900/30">
                <div>
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                    {batch.product.name} — <span className="font-mono text-xs text-slate-500">{batch.batch_number}</span>
                  </p>
                  <p className="text-xs text-amber-700 dark:text-amber-400 tabular-nums">
                    {batch.quantity_available} units · Expires in {hoursLeft}h {minsLeft}m
                  </p>
                </div>
                <Link to="/vendor/marketplace/new">
                  <Button variant="outline" size="sm">Create Listing</Button>
                </Link>
              </div>
            );
          })}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-800">
            <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-200">Pickups</h2>
            <Link to="/vendor/orders" className="text-xs text-emerald-600 hover:underline font-medium">View all</Link>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {ordersLoading
              ? Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 px-5 py-3">
                  <Skeleton className="h-3 flex-1" />
                  <Skeleton className="h-7 w-20 rounded-lg" />
                </div>
              ))
              : orders?.length === 0
              ? <p className="px-5 py-6 text-sm text-slate-400 text-center">No pending pickups</p>
              : orders?.slice(0, 5).map((order) => (
                <div key={order.id} className="flex items-center justify-between gap-3 px-5 py-3">
                  <div>
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                      {order.quantity}x {order.listing?.listing_title ?? 'Item'}
                    </p>
                    <p className="text-xs text-slate-400 font-mono">Code: #{order.claim_code}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={order.status} />
                  </div>
                </div>
              ))
            }
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-800">
            <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-200">Inventory Summary</h2>
            <Link to="/vendor/inventory" className="text-xs text-emerald-600 hover:underline font-medium">Manage</Link>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {batchLoading
              ? Array.from({ length: 3 }).map((_, i) => <div key={i} className="px-5 py-3"><Skeleton className="h-3 w-full" /></div>)
              : batches?.slice(0, 5).map((batch) => (
                <div key={batch.id} className="flex items-center justify-between gap-3 px-5 py-3">
                  <div>
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{batch.product.name}</p>
                    <p className="text-xs text-slate-400 font-mono">{batch.batch_number}</p>
                  </div>
                  <span className="tabular-nums text-sm font-semibold text-slate-700 dark:text-slate-300">
                    {batch.quantity_available} left
                  </span>
                </div>
              ))
            }
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorDashboardPage;
