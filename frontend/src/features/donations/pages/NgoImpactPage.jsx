import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { BarChart2, Heart, Award, ShieldCheck, TrendingUp, Users, Droplets, Leaf } from 'lucide-react';
import { donationsApi } from '../api/donationsApi';
import { SkeletonCardGrid } from '../../../components/ui/Skeleton';
import { EmptyState } from '../../../components/ui/EmptyState';

// Component: NgoImpactPage
export const NgoImpactPage = () => {
  const { data: impactSummary, isLoading: summaryLoading } = useQuery({
    queryKey: ['donations', 'impact', 'summary'],
    queryFn: donationsApi.getImpactSummary,
  });

  const { data: impacts, isLoading: impactsLoading } = useQuery({
    queryKey: ['donations', 'impacts'],
    queryFn: () => donationsApi.getImpacts(),
  });

  const isLoading = summaryLoading || impactsLoading;

  if (isLoading) {
    return (
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <SkeletonCardGrid count={4} />
      </div>
    );
  }

  const completedPickups = impactSummary?.completed_pickups || 0;
  const mealsServed = impactSummary?.meals_served || 0;
  const foodSavedKg = impactSummary?.food_saved_kg || 0;
  const carbonSavedKg = impactSummary?.carbon_saved_kg || 0;
  const beneficiaries = impactSummary?.beneficiaries || 0;

  if (completedPickups === 0) {
    return (
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <BarChart2 className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            NGO Community Impact & Sustainability
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Verified environmental impact metrics, carbon emission prevention stats, and food rescue analytics.
          </p>
        </div>
        <EmptyState
          icon={<Heart className="w-8 h-8 text-indigo-600" />}
          title="No completed pickups yet"
          description="Your organization has not completed any food rescue pickups yet. Impact metrics will calculate automatically once pickups are confirmed."
        />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <BarChart2 className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          NGO Community Impact & Sustainability
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Verified environmental impact metrics, carbon emission prevention stats, and food rescue analytics.
        </p>
      </div>

      {/* Top Impact Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Meals Rescued</span>
            <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <Heart className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 tabular-nums">{mealsServed}</p>
          <p className="text-xs text-indigo-600 font-semibold mt-1 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> Real Verified Meals
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">CO₂e Prevented</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <Leaf className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 tabular-nums">{carbonSavedKg.toFixed(1)} kg</p>
          <p className="text-xs text-emerald-600 font-semibold mt-1 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> Direct Landfill Avoidance
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Food Saved</span>
            <div className="w-9 h-9 rounded-xl bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 flex items-center justify-center">
              <Droplets className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 tabular-nums">{foodSavedKg.toFixed(1)} kg</p>
          <p className="text-xs text-sky-600 font-semibold mt-1">Net Weight Rescued</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">People Served</span>
            <div className="w-9 h-9 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 tabular-nums">{beneficiaries}</p>
          <p className="text-xs text-purple-600 font-semibold mt-1">Total Beneficiaries</p>
        </motion.div>
      </div>

      {/* Verified Certificate & Impact Audit Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 dark:text-slate-100 text-lg">Community Food Distribution Audit Logs</h3>
            <span className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold">Live Audit Trail</span>
          </div>

          <div className="space-y-3">
            {impacts && impacts.length > 0 ? (
              impacts.map((item) => (
                <div key={item.id} className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between text-xs">
                  <div className="space-y-0.5">
                    <span className="font-bold text-slate-900 dark:text-slate-100">
                      Rescued {item.meals_served} Meals ({item.food_saved_kg} kg)
                    </span>
                    <p className="text-slate-500">
                      Calculated At: {new Date(item.calculated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-emerald-600 dark:text-emerald-400">+{item.carbon_saved_kg} kg CO₂e</span>
                    <p className="text-slate-400 text-[10px]">Verified Impact</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500">No individual impact logs recorded yet.</p>
            )}
          </div>
        </div>

        {/* Certificate Card */}
        <div className="bg-gradient-to-br from-indigo-900 via-indigo-950 to-slate-950 text-white rounded-2xl p-6 shadow-xl space-y-4 relative overflow-hidden flex flex-col justify-between">
          <div className="space-y-2 relative z-10">
            <div className="w-10 h-10 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="font-black text-xl text-white">Verified NGO Impact Leader</h3>
            <p className="text-xs text-indigo-200 leading-relaxed">
              Awarded for outstanding contribution to urban food rescue and zero-waste community nutrition.
            </p>
          </div>

          <div className="pt-4 border-t border-indigo-800/60 relative z-10 space-y-1">
            <p className="text-[10px] text-indigo-300 font-bold uppercase tracking-wider">Certified Completed Pickups</p>
            <p className="font-bold text-sm text-white">{completedPickups} Pickups Verified</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NgoImpactPage;
