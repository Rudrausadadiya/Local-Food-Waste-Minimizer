import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Package, Plus, Search, Filter, ChevronRight, X, Calendar, DollarSign, Tag, Layers } from 'lucide-react';
import { useBranchStore } from '../../../stores/useBranchStore';
import { inventoryApi } from '../api/inventoryApi';
import { StockLevelBar } from '../../../components/ui/StockLevelBar';
import { StatusBadge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { EmptyState } from '../../../components/ui/EmptyState';
import { SkeletonTable } from '../../../components/ui/Skeleton';
import { useToastStore } from '../../../stores/useToastStore';
import { formatDateTime } from '../../../lib/utils';

// Function: getStockStatus
const getStockStatus = (b) => {
  if (b.quantity_available === 0) return 'OUT_OF_STOCK';
  if (b.quantity_available <= 5) return 'LOW_STOCK';
  return 'IN_STOCK';
};

// Component: InventoryListPage
const InventoryListPage = () => {
  const { activeBranchId } = useBranchStore();
  const [search, setSearch] = useState('');
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [showStockInModal, setShowStockInModal] = useState(false);

  const { addToast } = useToastStore();
  const qc = useQueryClient();

  // Stock In Form State
  const [productName, setProductName] = useState('');
  const [image, setImage] = useState(null);
  const [batchNumber, setBatchNumber] = useState(`BATCH-${Date.now().toString().slice(-5)}`);
  const [quantity, setQuantity] = useState('25');
  const [storageLocation, setStorageLocation] = useState('REFRIGERATED');

  const { data: batches, isLoading } = useQuery({
    queryKey: ['inventory', activeBranchId ?? '', {}],
    queryFn: () => inventoryApi.getBatches(activeBranchId ?? ''),
    enabled: !!activeBranchId,
  });

  const { data: transactions, isLoading: txLoading } = useQuery({
    queryKey: ['inventory', selectedBatch?.id ?? '', 'transactions'],
    queryFn: () => inventoryApi.getTransactions(selectedBatch.id),
    enabled: !!selectedBatch,
  });

  // Stock In Mutation
  const createBatchMutation = useMutation({
    mutationFn: (newBatchData) => inventoryApi.createBatch(newBatchData),
    onSuccess: () => {
      addToast({
        title: 'Stock In Complete!',
        description: `Successfully added ${quantity} units of ${productName || 'Surplus Item'} to inventory.`,
        variant: 'success'
      });
      qc.invalidateQueries({ queryKey: ['inventory'] });
      setShowStockInModal(false);
      // Reset form
      setProductName('');
      setImage(null);
      setBatchNumber(`BATCH-${Date.now().toString().slice(-5)}`);
    },
    onError: (err) => {
      addToast({
        title: 'Stock In Failed',
        description: err?.response?.data?.detail || 'Could not record stock in batch.',
        variant: 'error'
      });
    },
  });

  // Function: handleStockInSubmit
  const handleStockInSubmit = (e) => {
    e.preventDefault();
    if (!productName.trim()) {
      addToast({ title: 'Product Name Required', description: 'Enter the item or product name.', variant: 'error' });
      return;
    }
    const formData = new FormData();
    formData.append('batch_number', batchNumber);
    formData.append('quantity', parseFloat(quantity));
    formData.append('storage_location', storageLocation);
    formData.append('product_name', productName);
    formData.append('branch_id', activeBranchId);
    if (image) {
      formData.append('image', image);
    }

    createBatchMutation.mutate(formData);
  };

  const [showFilterDropdown, setShowFilterDropdown] = useState(false);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [filterStorage, setFilterStorage] = useState('ALL');

  const filtered = batches?.filter((b) => {
    const nameMatch = (b.product?.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (b.batch_number || '').toLowerCase().includes(search.toLowerCase());
    
    const status = getStockStatus(b);
    const statusMatch = filterStatus === 'ALL' || status === filterStatus;
    const storageMatch = filterStorage === 'ALL' || b.storage_location === filterStorage;

    return nameMatch && statusMatch && storageMatch;
  }) ?? [];

  const txTypeColors = {
    STOCK_IN: 'text-emerald-600',
    STOCK_OUT: 'text-red-500',
    TRANSFER: 'text-sky-600',
    ADJUSTMENT: 'text-amber-600',
  };

  return (
    <div className="flex h-full">
      <div className={`flex flex-col flex-1 min-w-0 transition-all duration-200 ${selectedBatch ? 'hidden lg:flex' : 'flex'}`}>
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Inventory Management</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{filtered.length} batches tracked</p>
            </div>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setShowStockInModal(true)}
            >
              Stock In
            </Button>
          </div>



          <div className="flex gap-3">
            <div className="flex-1">
              <Input
                placeholder="Search products or batch numbers..."
                prefixIcon={<Search className="w-4 h-4" />}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="relative">
              <Button
                variant={filterStatus !== 'ALL' || filterStorage !== 'ALL' ? 'primary' : 'outline'}
                size="md"
                leftIcon={<Filter className="w-4 h-4" />}
                onClick={() => setShowFilterDropdown(!showFilterDropdown)}
              >
                Filter {filterStatus !== 'ALL' || filterStorage !== 'ALL' ? '• Active' : ''}
              </Button>

              {showFilterDropdown && (
                <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl z-30 p-4 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                    <span className="font-bold text-sm text-slate-900 dark:text-slate-100">Filter Inventory</span>
                    <button
                      onClick={() => {
                        setFilterStatus('ALL');
                        setFilterStorage('ALL');
                      }}
                      className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold hover:underline"
                    >
                      Reset All
                    </button>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Stock Status</label>
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100"
                    >
                      <option value="ALL">All Statuses</option>
                      <option value="IN_STOCK">In Stock</option>
                      <option value="LOW_STOCK">Low Stock (&le; 5 units)</option>
                      <option value="OUT_OF_STOCK">Out of Stock</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Storage Environment</label>
                    <select
                      value={filterStorage}
                      onChange={(e) => setFilterStorage(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100"
                    >
                      <option value="ALL">All Environments</option>
                      <option value="ROOM_TEMP">Room Temperature</option>
                      <option value="REFRIGERATED">Refrigerated (Chilled)</option>
                      <option value="FROZEN">Freezer (-18°C)</option>
                    </select>
                  </div>

                  <Button
                    variant="secondary"
                    size="sm"
                    className="w-full text-xs"
                    onClick={() => setShowFilterDropdown(false)}
                  >
                    Apply Filters
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-6"><SkeletonTable rows={6} cols={5} /></div>
          ) : filtered.length === 0 ? (
            <EmptyState
              icon={<Package className="w-8 h-8" />}
              title="No inventory batches"
              description="No products in inventory yet. Add your master catalog items or complete a stock-in batch."
              action={{
                label: '+ Add Stock',
                onClick: () => setShowStockInModal(true)
              }}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm" aria-label="Inventory batches">
                <thead className="bg-slate-50 dark:bg-slate-900/50 sticky top-0">
                  <tr className="border-b border-slate-200 dark:border-slate-800">
                    {['Product / Batch', 'Stock', 'Status', ''].map((h) => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 bg-white dark:bg-slate-900">
                  {filtered.map((batch) => (
                    <motion.tr
                      key={batch.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
                      onClick={() => setSelectedBatch(batch)}
                    >
                      <td className="px-4 py-3.5">
                        <p className="font-medium text-slate-800 dark:text-slate-200">{batch.product?.name || 'Surplus Product'}</p>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">{batch.batch_number}</p>
                      </td>
                      <td className="px-4 py-3.5 min-w-48">
                        <StockLevelBar
                          available={batch.quantity_available}
                          showLabels={false}
                        />
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 tabular-nums">
                          {batch.quantity_available} avail
                        </p>
                      </td>

                      <td className="px-4 py-3.5">
                        <StatusBadge status={getStockStatus(batch)} />
                      </td>
                      <td className="px-4 py-3.5">
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Batch Side Drawer */}
      <AnimatePresence>
        {selectedBatch && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 360, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 350, damping: 28 }}
            className="flex-shrink-0 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden flex flex-col"
            aria-label="Batch detail"
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{selectedBatch.product?.name || 'Surplus Item'}</h2>
                <p className="text-xs text-slate-400 font-mono">{selectedBatch.batch_number}</p>
              </div>
              <button onClick={() => setSelectedBatch(null)} className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400" aria-label="Close detail">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-5">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Stock Breakdown</p>
                <StockLevelBar
                  available={selectedBatch.quantity_available}
                  reserved={selectedBatch.quantity_reserved}
                  damaged={selectedBatch.quantity_damaged}
                  expired={selectedBatch.quantity_expired}
                />
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Transaction History</p>
                {txLoading ? (
                  <div className="space-y-2">{Array.from({length:4}).map((_,i) => <div key={i} className="h-10 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
                ) : !transactions?.length ? (
                  <p className="text-sm text-slate-400 text-center py-4">No transactions recorded</p>
                ) : (
                  <div className="space-y-1">
                    {transactions.map((tx) => (
                      <div key={tx.id} className="flex items-center justify-between gap-3 py-2 border-b border-slate-100 dark:border-slate-800 last:border-0">
                        <div>
                          <p className={`text-xs font-semibold ${txTypeColors[tx.transaction_type] ?? 'text-slate-700'}`}>
                            {tx.transaction_type.replace('_', ' ')}
                          </p>
                          <p className="text-xs text-slate-400">{formatDateTime(tx.created_at)}</p>
                          {tx.reason && <p className="text-xs text-slate-400 italic">{tx.reason}</p>}
                        </div>
                        <span className={`tabular-nums font-bold text-sm ${tx.quantity > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                          {tx.quantity > 0 ? '+' : ''}{tx.quantity}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Stock In / Add Stock Modal */}
      <AnimatePresence>
        {showStockInModal && (
          <div className="fixed inset-0 z-50 flex items-start justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-lg m-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden"
            >
              <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                    <Plus className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">Stock In New Batch</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Receive and record incoming inventory stock</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowStockInModal(false)}
                  className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleStockInSubmit} className="p-6 space-y-4">
                <Input
                  label="Product / Item Name"
                  placeholder="e.g. Artisan Cinnamon Croissants"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  required
                />

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Storage Environment</label>
                  <select
                    value={storageLocation}
                    onChange={(e) => setStorageLocation(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="ROOM_TEMP">Room Temperature</option>
                    <option value="REFRIGERATED">Refrigerated (Chilled)</option>
                    <option value="FROZEN">Freezer (-18°C)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="Batch Number"
                    value={batchNumber}
                    onChange={(e) => setBatchNumber(e.target.value)}
                    required
                  />
                  <Input
                    label="Quantity Received (Units)"
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    required
                  />
                </div>

                <Input
                  label="Product Image (Optional)"
                  type="file"
                  accept="image/png, image/jpeg"
                  onChange={(e) => setImage(e.target.files[0])}
                />

                <div className="pt-4 flex gap-3 justify-end border-t border-slate-100 dark:border-slate-800">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowStockInModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={createBatchMutation.isPending}
                  >
                    Confirm Stock In
                  </Button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default InventoryListPage;
