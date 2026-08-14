import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Heart, Package, Calendar, Award, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '../../../components/ui/Button';
import { donationsApi } from '../api/donationsApi';

// Component: NgoDashboardPage
const NgoDashboardPage = () => {
  const { data: pickups, isLoading: pickupsLoading } = useQuery({
    queryKey: ['donations', 'pickups'],
    queryFn: () => donationsApi.getDonationPickups(),
  });

  const { data: listings, isLoading: listingsLoading } = useQuery({
    queryKey: ['donations', 'listings'],
    queryFn: () => donationsApi.getDonationListings(),
  });

  const activePickupsCount = pickups?.length || 0;
  const listingsCount = listings?.length || 0;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">NGO Rescue Dashboard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Coordinate incoming surplus food donations and track community impact</p>
        </div>
        <Link to="/ngo/browse">
          <Button variant="ngo" leftIcon={<Heart className="w-4 h-4" />}>Browse Donations</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-500">Donation Offers</span>
            <Heart className="w-5 h-5 text-indigo-600" />
          </div>
          <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
            {listingsLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : listingsCount}
          </p>
          <p className="text-xs text-indigo-600 font-semibold mt-1">Available for rescue</p>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-500">Active Pickups</span>
            <Calendar className="w-5 h-5 text-amber-500" />
          </div>
          <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
            {pickupsLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : `${activePickupsCount} pickups`}
          </p>
          <p className="text-xs text-amber-600 font-semibold mt-1">Claimed & Scheduled</p>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-500">Community Impact</span>
            <Award className="w-5 h-5 text-emerald-600" />
          </div>
          <p className="text-3xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
            {listingsCount > 0 ? `${listingsCount * 15} kg` : '0 kg'}
          </p>
          <p className="text-xs text-emerald-600 font-semibold mt-1">Food waste prevented</p>
        </div>
      </div>
    </div>
  );
};

export default NgoDashboardPage;
