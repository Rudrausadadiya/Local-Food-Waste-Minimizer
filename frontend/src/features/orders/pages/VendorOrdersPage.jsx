import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, QrCode, ShieldCheck, Truck, CheckCircle } from 'lucide-react';
import { ordersApi } from '../api/ordersApi';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { StatusBadge } from '../../../components/ui/Badge';
import { SkeletonTable } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';
import { useToastStore } from '../../../stores/useToastStore';
import { formatCurrency } from '../../../lib/utils';

// Component: VendorOrdersPage
const VendorOrdersPage = () => {
  const [claimCodeInput, setClaimCodeInput] = useState('');
  const [activeTab, setActiveTab] = useState('PENDING');
  const [isScanningQR, setIsScanningQR] = useState(false);
  const [verifiedSuccessOrder, setVerifiedSuccessOrder] = useState(null);

  const { addToast } = useToastStore();
  const qc = useQueryClient();

  const { data: orders, isLoading } = useQuery({
    queryKey: ['orders', 'vendor', activeTab],
    queryFn: () => ordersApi.getVendorOrders(activeTab === 'ALL' ? {} : { status: activeTab }),
  });

  const verifyMutation = useMutation({
    mutationFn: (code) => ordersApi.verifyClaimCode(code),
    onSuccess: (data) => {
      setVerifiedSuccessOrder(data);
      addToast({ title: '✅ Claim Verified!', description: `Claim Code #${data.claim_code || claimCodeInput} verified and pickup completed.`, variant: 'success' });
      setClaimCodeInput('');
      setIsScanningQR(false);
      qc.invalidateQueries({ queryKey: ['orders', 'vendor'] });
    },
    onError: (err) => {
      addToast({ title: 'Verification Failed', description: err?.response?.data?.detail ?? 'Invalid claim code or already completed.', variant: 'error' });
    },
  });

  const completeMutation = useMutation({
    mutationFn: (id) => ordersApi.completeOrder(id),
    onSuccess: () => {
      addToast({ title: 'Order Completed', description: 'Surplus item pickup confirmed.', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['orders', 'vendor'] });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (id) => ordersApi.cancelOrder(id),
    onSuccess: () => {
      addToast({ title: 'Order Cancelled', description: 'Order cancelled and stock restored to listing.', variant: 'info' });
      qc.invalidateQueries({ queryKey: ['orders', 'vendor'] });
    },
    onError: (err) => {
      addToast({ title: 'Cancellation Failed', description: err?.response?.data?.detail || 'Failed to cancel order.', variant: 'error' });
    },
  });

  const dispatchMutation = useMutation({
    mutationFn: (id) => ordersApi.dispatchDelivery(id),
    onSuccess: () => {
      addToast({ title: 'Delivery Dispatched', description: 'Delivery status updated to DISPATCHED.', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['orders', 'vendor'] });
    },
    onError: (err) => {
      addToast({ title: 'Dispatch Failed', description: err?.response?.data?.detail || 'Failed to dispatch delivery.', variant: 'error' });
    },
  });

  const deliverMutation = useMutation({
    mutationFn: (id) => ordersApi.markDelivered(id),
    onSuccess: () => {
      addToast({ title: 'Delivery Completed', description: 'Delivery marked as DELIVERED.', variant: 'success' });
      qc.invalidateQueries({ queryKey: ['orders', 'vendor'] });
    },
    onError: (err) => {
      addToast({ title: 'Delivery Update Failed', description: err?.response?.data?.detail || 'Failed to mark delivered.', variant: 'error' });
    },
  });

  // Function: handleSimulateQRScan
  const handleSimulateQRScan = () => {
    setIsScanningQR(true);
    setTimeout(() => {
      const pendingOrder = orders?.find((o) => o.status === 'PENDING' && o.claim_code) || orders?.find((o) => Boolean(o.claim_code));
      if (pendingOrder?.claim_code) {
        setClaimCodeInput(pendingOrder.claim_code);
        verifyMutation.mutate(pendingOrder.claim_code);
      } else {
        setIsScanningQR(false);
        addToast({ title: 'No pending orders', description: 'No pending pickup claim code found to scan.', variant: 'info' });
      }
    }, 1200);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Customer Orders & Pickups</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Verify customer claim codes, handle delivery dispatches, and confirm completed orders.</p>
      </div>

      {/* Quick Counter Claim Verification & QR Scanner Box */}
      <div className="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/80 rounded-3xl p-6 space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-emerald-950 dark:text-emerald-300">⚡ Counter Quick Verification</h2>
              <span className="text-[10px] font-bold uppercase bg-emerald-200 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 px-2 py-0.5 rounded-md">
                Fast Pickup
              </span>
            </div>
            <p className="text-xs text-emerald-700 dark:text-emerald-400">
              Scan customer mobile QR code or type 6-digit claim code upon arrival
            </p>
          </div>

          <div className="flex flex-wrap gap-2 w-full sm:w-auto">
            <Button
              variant="outline"
              size="md"
              leftIcon={<QrCode className="w-4 h-4 text-emerald-600" />}
              onClick={handleSimulateQRScan}
              loading={isScanningQR}
              className="bg-white dark:bg-slate-900"
            >
              {isScanningQR ? 'Scanning Camera...' : '📷 Scan Mobile QR'}
            </Button>
          </div>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (claimCodeInput.trim()) verifyMutation.mutate(claimCodeInput.trim());
          }}
          className="flex flex-col sm:flex-row gap-2 pt-2 border-t border-emerald-200/60 dark:border-emerald-800/60"
        >
          <Input
            placeholder="Enter claim code"
            value={claimCodeInput}
            onChange={(e) => setClaimCodeInput(e.target.value)}
            className="w-full sm:w-60 font-mono font-bold uppercase tracking-wider text-base"
          />
          <Button
            variant="primary"
            type="submit"
            loading={verifyMutation.isPending}
            disabled={!claimCodeInput.trim()}
            leftIcon={<ShieldCheck className="w-4 h-4" />}
          >
            Verify & Complete Pickup
          </Button>
        </form>

        {/* Verification Success Banner */}
        <AnimatePresence>
          {verifiedSuccessOrder && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-emerald-300 dark:border-emerald-700 shadow-md flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold">
                  ✓
                </div>
                <div>
                  <p className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider">Pickup Verified & Marked Completed</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    {verifiedSuccessOrder.listing?.listing_title || 'Surplus Food Order'}
                  </p>
                </div>
              </div>
              <button onClick={() => setVerifiedSuccessOrder(null)} className="text-xs text-slate-400 hover:underline">
                Dismiss
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Tabs */}
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

      {isLoading ? (
        <SkeletonTable rows={5} cols={5} />
      ) : !orders?.length ? (
        <EmptyState
          icon={<Clock className="w-8 h-8" />}
          title={`No ${activeTab.toLowerCase()} orders`}
          description="Customer reservations and pickup requests will appear here."
        />
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
          <table className="w-full text-sm" aria-label="Customer orders">
            <thead className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                {['Order ID', 'Item / Type', 'Quantity', 'Total Price', 'Claim / Delivery', 'Status', 'Actions'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {orders.map((order) => {
                const isDelivery = order.order_type === 'DELIVERY' || Boolean(order.delivery);
                const delStatus = order.delivery?.status || (isDelivery ? 'PENDING' : null);

                return (
                  <tr key={order.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3.5 font-mono text-xs text-slate-500">
                      #{order.id.slice(0, 8)}
                    </td>
                    <td className="px-4 py-3.5">
                      <p className="font-medium text-slate-800 dark:text-slate-200">{order.listing?.listing_title ?? 'Surplus Item'}</p>
                      <span className="text-[10px] uppercase font-bold text-slate-400">{order.order_type || 'TAKEAWAY'}</span>
                    </td>
                    <td className="px-4 py-3.5 tabular-nums">{order.quantity}</td>
                    <td className="px-4 py-3.5 font-semibold text-emerald-600 tabular-nums">
                      {formatCurrency(Number(order.total_price || order.total_amount || 0))}
                    </td>
                    <td className="px-4 py-3.5">
                      {isDelivery ? (
                        <div className="space-y-0.5">
                          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-sky-50 dark:bg-sky-950/80 text-sky-700 dark:text-sky-300">
                            Delivery: {delStatus}
                          </span>
                          {order.delivery?.delivery_address && (
                            <p className="text-[11px] text-slate-500 truncate max-w-[140px]">{order.delivery.delivery_address}</p>
                          )}
                        </div>
                      ) : (
                        <span className="font-mono font-bold text-xs bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-lg text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700">
                          #{order.claim_code || 'N/A'}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5">
                      <StatusBadge status={order.order_status || order.status} />
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-2">
                        {order.status === 'PENDING' && (
                          <div className="flex items-center gap-1.5">
                            {!isDelivery && (
                              <Button
                                variant="primary"
                                size="sm"
                                loading={completeMutation.isPending}
                                onClick={() => completeMutation.mutate(order.id)}
                              >
                                Complete Pickup
                              </Button>
                            )}
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-red-600 border-red-200 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-950/40"
                              loading={cancelMutation.isPending}
                              onClick={() => cancelMutation.mutate(order.id)}
                            >
                              Cancel
                            </Button>
                          </div>
                        )}

                        {isDelivery && delStatus === 'PENDING' && (
                          <Button
                            variant="indigo"
                            size="sm"
                            leftIcon={<Truck className="w-3.5 h-3.5" />}
                            loading={dispatchMutation.isPending}
                            onClick={() => dispatchMutation.mutate(order.id)}
                          >
                            Dispatch
                          </Button>
                        )}

                        {isDelivery && delStatus === 'DISPATCHED' && (
                          <Button
                            variant="emerald"
                            size="sm"
                            leftIcon={<CheckCircle className="w-3.5 h-3.5" />}
                            loading={deliverMutation.isPending}
                            onClick={() => deliverMutation.mutate(order.id)}
                          >
                            Mark Delivered
                          </Button>
                        )}
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
  );
};

export default VendorOrdersPage;
