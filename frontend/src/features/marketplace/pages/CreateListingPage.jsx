import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery, useMutation } from '@tanstack/react-query';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { useBranchStore } from '../../../stores/useBranchStore';
import { inventoryApi } from '../../inventory/api/inventoryApi';
import { marketplaceApi } from '../api/marketplaceApi';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { useToastStore } from '../../../stores/useToastStore';

const schema = z.object({
  inventory_batch: z.string().optional(),
  listing_title: z.string().min(3, 'Title is required'),
  description: z.string().optional(),
  original_price: z.coerce.number().min(0.01, 'Enter valid original price'),
  discounted_price: z.coerce.number().min(0.01, 'Enter valid surplus price'),
  quantity_available: z.coerce.number().min(1, 'Quantity must be at least 1'),
  pricing_strategy: z.enum(['MANUAL', 'AUTOMATIC', 'AI_RECOMMENDED']),
  expires_at: z.string().optional(),
  visible_to_ngos: z.boolean().default(false),
  is_featured: z.boolean().default(false),
});

// Component: CreateListingPage
const CreateListingPage = () => {
  const { activeBranchId, activeBusinessId } = useBranchStore();
  const navigate = useNavigate();
  const { addToast } = useToastStore();

  const { data: batches } = useQuery({
    queryKey: ['inventory', activeBranchId ?? '', {}],
    queryFn: () => inventoryApi.getBatches(activeBranchId ?? ''),
    enabled: !!activeBranchId,
  });

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      pricing_strategy: 'AI_RECOMMENDED',
      visible_to_ngos: false,
      is_featured: false,
      expires_at: new Date(Date.now() + 7 * 86400 * 1000).toISOString().slice(0, 16),
    },
  });

  const selectedBatchId = watch('inventory_batch');
  const originalPrice = watch('original_price');
  const pricingStrategy = watch('pricing_strategy');

  // Handle auto batch selection defaults
  // Function: handleBatchSelect
  const handleBatchSelect = (e) => {
    const bId = e.target.value;
    setValue('inventory_batch', bId);
    const batch = batches?.find((b) => b.id === bId);
    if (batch) {
      setValue('listing_title', `Surplus ${batch.product.name}`);
      const price = Number(batch.product.regular_price || 5.0);
      setValue('original_price', price);
      setValue('quantity_available', batch.quantity_available);
      setValue('expires_at', new Date(Date.now() + 7 * 86400 * 1000).toISOString().slice(0, 16));
      // Calculate AI discount (60% off)
      setValue('discounted_price', Number((price * 0.4).toFixed(2)));
    }
  };

  const mutation = useMutation({
    mutationFn: (data) => {
      const selectedBatch = batches?.find((b) => b.id === data.inventory_batch);
      let isoExpiry = data.expires_at;
      try {
        const d = new Date(isoExpiry);
        if (isNaN(d.getTime()) || d.getTime() <= Date.now() + 3600 * 1000) {
          d.setTime(Date.now() + 7 * 86400 * 1000);
        }
        isoExpiry = d.toISOString();
      } catch {
        isoExpiry = new Date(Date.now() + 7 * 86400 * 1000).toISOString();
      }

      const payload = {
        ...data,
        expires_at: isoExpiry,
        branch: activeBranchId,
        product: selectedBatch?.product?.id || selectedBatch?.product,
        business: selectedBatch?.business?.id || selectedBatch?.business || selectedBatch?.branch?.business || activeBusinessId,
        listing_status: 'PUBLISHED',
      };
      return marketplaceApi.createListing(payload);
    },
    onSuccess: () => {
      addToast({ title: 'Listing published!', description: 'Your surplus item is live on the marketplace.', variant: 'success' });
      navigate('/vendor/marketplace');
    },
    onError: (err) => {
      const errorData = err?.response?.data;
      let msg = 'Validation error.';
      if (errorData) {
        if (typeof errorData === 'string') msg = errorData;
        else if (errorData.message) msg = errorData.message;
        else if (errorData.detail) msg = errorData.detail;
        else msg = Object.entries(errorData).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ');
      }
      addToast({ title: 'Publishing failed', description: msg, variant: 'error' });
    },
  });

  // Function: onSubmit
  const onSubmit = (data) => mutation.mutate(data);

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <Link to="/vendor/marketplace" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-200">
        <ArrowLeft className="w-4 h-4" /> Back to listings
      </Link>

      {/* Feature 2: 1-Click Surplus Surprise Bag / Mystery Box Preset Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-lg space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-base">
            <Sparkles className="w-5 h-5 text-amber-300" />
            <span>🎁 Surplus "Mystery Box" / Surprise Bag Preset</span>
          </div>
          <span className="text-[10px] font-extrabold uppercase bg-white/20 px-2.5 py-1 rounded-full backdrop-blur-xs">
            70% Rescue Rate
          </span>
        </div>
        <p className="text-xs text-purple-100 leading-relaxed">
          Don't have time to list individual items? Sell a Surprise Bag containing today's fresh leftover inventory packed near closing time!
        </p>
        <button
          type="button"
          onClick={() => {
            setValue('listing_title', 'Bakery & Pastry Surplus Surprise Bag');
            setValue('original_price', 15.00);
            setValue('discounted_price', 4.99);
            setValue('quantity_available', 10);
            setValue('pricing_strategy', 'AI_RECOMMENDED');
            setValue('description', "Contains a delicious, fresh assortment of today's artisanal loaves, croissants, and pastries packed near closing time.");
            setValue('expires_at', new Date(Date.now() + 6 * 3600 * 1000).toISOString().slice(0, 16));
            setValue('inventory_batch', ''); // Clear batch selection
            addToast({
              title: '🎁 Mystery Bag Preset Loaded!',
              description: 'Loaded ₹15.00 value for ₹4.99 (67% Off). Adjust details if needed.',
              variant: 'success'
            });
          }}
          className="w-full py-2.5 px-4 rounded-xl bg-white text-purple-900 font-bold text-xs hover:bg-purple-50 transition-transform active:scale-98 shadow-md"
        >
          ⚡ Load 1-Click "Surplus Surprise Bag" Preset (₹15 Value → ₹4.99)
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6">
        {/* Step 1: Select batch */}
        <div>
          <label className="block text-sm font-semibold text-slate-800 dark:text-slate-200 mb-2">
            1. Select Inventory Batch
          </label>
          <select
            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500"
            onChange={handleBatchSelect}
            value={selectedBatchId ?? ''}
          >
            <option value="">Select a batch...</option>
            {batches?.filter(b => {
              if (!b.expiry_date) return true;
              const today = new Date();
              today.setHours(0,0,0,0);
              const expiry = new Date(b.expiry_date);
              return expiry >= today;
            }).map((b) => (
              <option key={b.id} value={b.id}>
                {b.product.name} ({b.batch_number}) — {b.quantity_available} left
              </option>
            ))}
          </select>
          {errors.inventory_batch && <p className="text-xs text-red-500 mt-1">{errors.inventory_batch.message}</p>}
        </div>

        {/* Listing Title */}
        <Input
          label="Listing Title"
          placeholder="e.g. Surplus Fresh Artisan Loaves"
          error={errors.listing_title?.message}
          {...register('listing_title')}
        />

        {/* Step 2: Pricing Strategy */}
        <div className="space-y-3">
          <label className="block text-sm font-semibold text-slate-800 dark:text-slate-200">
            2. Pricing Strategy
          </label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'MANUAL', label: 'Manual Price', desc: 'Set custom discount' },
              { id: 'AUTOMATIC', label: 'Automatic', desc: 'Linear markdown' },
              { id: 'AI_RECOMMENDED', label: 'AI-Recommended', desc: '60% optimal rescue rate', icon: <Sparkles className="w-3.5 h-3.5 text-violet-500" /> },
            ].map(({ id, label, desc, icon }) => (
              <button
                key={id}
                type="button"
                onClick={() => {
                  setValue('pricing_strategy', id);
                  if (id === 'AI_RECOMMENDED' && originalPrice) {
                    setValue('discounted_price', Number((originalPrice * 0.4).toFixed(2)));
                  }
                }}
                className={`p-3 rounded-xl border text-left transition-all ${
                  pricingStrategy === id
                    ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center gap-1.5 font-medium text-xs text-slate-800 dark:text-slate-200">
                  {icon} {label}
                </div>
                <p className="text-xs text-slate-400 mt-0.5">{desc}</p>
              </button>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-4 pt-2">
            <Input label="Original Price (₹)" type="number" step="1" error={errors.original_price?.message} {...register('original_price')} />
            <Input label="Surplus Price (₹)" type="number" step="1" error={errors.discounted_price?.message} {...register('discounted_price')} />
            <Input label="Quantity Available" type="number" error={errors.quantity_available?.message} {...register('quantity_available')} />
          </div>
        </div>

        {/* Step 3: Expiry & Options */}
        <div className="space-y-4">
          <Input
            label="Expiration Date & Time"
            type="datetime-local"
            error={errors.expires_at?.message}
            {...register('expires_at')}
          />

          <div className="space-y-3 pt-2 border-t border-slate-100 dark:border-slate-800">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" {...register('visible_to_ngos')} />
              <div>
                <p className="text-sm font-medium text-slate-800 dark:text-slate-200">Visible to NGOs for Direct Donation</p>
                <p className="text-xs text-slate-400">Allows verified non-profits to claim unreserved food for free prior to expiration.</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" {...register('is_featured')} />
              <div>
                <p className="text-sm font-medium text-slate-800 dark:text-slate-200">Feature on Local Marketplace Homepage</p>
                <p className="text-xs text-slate-400">Increases visibility on customer browse map.</p>
              </div>
            </label>
          </div>
        </div>

        <div className="pt-4 flex gap-3 justify-end">
          <Link to="/vendor/marketplace"><Button variant="outline" type="button">Cancel</Button></Link>
          <Button variant="primary" type="submit" loading={mutation.isPending}>Publish Listing Now</Button>
        </div>
      </form>
    </div>
  );
};

export default CreateListingPage;
