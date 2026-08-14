import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Clock, RefreshCw, LogOut } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { StatusBadge } from '../../../components/ui/Badge';
import { useAuthStore } from '../../../stores/useAuthStore';
import { authApi } from '../api/authApi';

// Component: PendingOnboardingPage
export const PendingOnboardingPage = () => {
  const { user, logout, updateUser } = useAuthStore();
  const navigate = useNavigate();

  const { data: profile, refetch, isFetching } = useQuery({
    queryKey: ['auth', 'profile'],
    queryFn: authApi.getProfile,
    refetchInterval: 10000,
  });

  React.useEffect(() => {
    if (profile?.business_status) {
      updateUser({ business_status: profile.business_status });
      if (profile.business_status === 'APPROVED') {
        const dest = user?.role === 'VENDOR' ? '/vendor/dashboard' : '/ngo/dashboard';
        navigate(dest, { replace: true });
      }
    }
  }, [profile, user?.role, updateUser, navigate]);

  // Function: handleLogout
  const handleLogout = () => { logout(); navigate('/login'); };

  const currentStatus = profile?.business_status || user?.business_status || 'PENDING';
  const isRevoked = currentStatus === 'UNVERIFIED' || profile?.is_verified === false || user?.is_verified === false;
  const isRejected = currentStatus === 'REJECTED';
  const isSuspended = currentStatus === 'SUSPENDED';

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 350, damping: 28 }}
        className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-lg p-8 text-center"
      >
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5 ${
          isRevoked || isRejected || isSuspended ? 'bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400' : 'bg-amber-100 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400'
        }`}>
          <Clock className="w-8 h-8" />
        </div>

        <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-2">
          {isRevoked
            ? 'Store Verification Revoked'
            : isRejected
            ? 'Registration Verification Rejected'
            : isSuspended
            ? 'Account Temporarily Suspended'
            : 'Account Verification Under Review'}
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 leading-relaxed">
          {isRevoked
            ? 'Your store verification has been revoked by system operations. Access to your merchant dashboard and store listings is suspended until re-verified by an administrator.'
            : isRejected
            ? 'Your merchant application was reviewed and not approved at this time. Please contact system administrators for assistance.'
            : isSuspended
            ? 'Your account has been suspended by system operations. Please contact support.'
            : 'Thank you for registering. Our team is currently reviewing your merchant application. Once approved, you will get full access.'}
        </p>

        <div className="flex items-center justify-center gap-3 mb-6">
          <StatusBadge status={currentStatus} />
        </div>

        {user && (
          <div className="rounded-xl bg-slate-50 dark:bg-slate-800 p-4 text-left space-y-2 mb-6 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Name</span>
              <span className="font-medium text-slate-800 dark:text-slate-200">{user.first_name} {user.last_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Email</span>
              <span className="font-medium text-slate-800 dark:text-slate-200 truncate max-w-48">{user.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Role</span>
              <span className="font-medium text-slate-800 dark:text-slate-200">{user.role}</span>
            </div>
          </div>
        )}

        <div className="flex gap-3">
          <Button variant="outline" onClick={handleLogout} leftIcon={<LogOut className="w-4 h-4" />} className="flex-1">
            Log Out
          </Button>
          <Button variant="primary" onClick={() => refetch()} loading={isFetching} leftIcon={<RefreshCw className="w-4 h-4" />} className="flex-1">
            Refresh Status
          </Button>
        </div>
      </motion.div>
    </div>
  );
};
