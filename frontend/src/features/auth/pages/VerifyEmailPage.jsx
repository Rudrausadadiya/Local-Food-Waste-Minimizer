import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Leaf, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { useToastStore } from '../../../stores/useToastStore';
import { authApi } from '../api/authApi';

// Component: VerifyEmailPage
export const VerifyEmailPage = () => {
  const [searchParams] = useSearchParams();
  const { addToast } = useToastStore();
  const [errorMessage, setErrorMessage] = useState(null);

  const uidb64 = searchParams.get('uidb64') || searchParams.get('uid');
  const token = searchParams.get('token');

  const mutation = useMutation({
    mutationFn: (data) => authApi.verifyEmail(data),
    onSuccess: () => {
      addToast({ title: 'Email Verified', description: 'Your email address has been verified successfully.', variant: 'success' });
    },
    onError: (error) => {
      const data = error?.response?.data;
      let msg = 'Verification failed. The link may be invalid or expired.';
      if (typeof data === 'string') {
        msg = data;
      } else if (data?.message) {
        msg = data.message;
      } else if (data?.detail) {
        msg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      } else if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0];
        const val = data[firstKey];
        const text = Array.isArray(val) ? val[0] : String(val);
        msg = `${firstKey}: ${text}`;
      }
      setErrorMessage(msg);
      addToast({ title: 'Verification Failed', description: msg, variant: 'error' });
    },
  });

  useEffect(() => {
    if (uidb64 && token) {
      mutation.mutate({ uidb64, token });
    } else {
      setErrorMessage('Missing verification parameters in URL.');
    }
  }, [uidb64, token]);

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-950">
      <div className="hidden lg:flex flex-col justify-between w-96 bg-emerald-600 p-10 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <span className="text-white font-bold text-lg">FoodWaste</span>
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white leading-tight mb-4">
            Rescue food.<br />Reduce waste.<br />Save money.
          </h1>
          <p className="text-emerald-100 text-sm leading-relaxed">
            Connect surplus food from businesses to nearby customers and NGOs before it's too late.
          </p>
        </div>
        <p className="text-emerald-200 text-xs">© {new Date().getFullYear()} Local Food Waste Minimizer</p>
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22, ease: 'easeOut' }}
          className="w-full max-w-sm text-center"
        >
          {mutation.isPending && (
            <div className="py-8 space-y-4">
              <Loader2 className="w-10 h-10 text-emerald-600 animate-spin mx-auto" />
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Verifying your email...</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Please wait while we confirm your email address.</p>
            </div>
          )}

          {mutation.isSuccess && (
            <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-2xl p-8 space-y-4">
              <div className="w-14 h-14 rounded-full bg-emerald-100 dark:bg-emerald-900/60 flex items-center justify-center mx-auto text-emerald-600 dark:text-emerald-400">
                <CheckCircle className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Email Verified!</h2>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  Your email address has been verified. You can now access all features of your account.
                </p>
              </div>
              <Link to="/login" className="block pt-2">
                <Button variant="primary" size="lg" className="w-full">
                  Continue to Sign In
                </Button>
              </Link>
            </div>
          )}

          {(errorMessage || (!uidb64 || !token)) && !mutation.isPending && !mutation.isSuccess && (
            <div className="bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-2xl p-8 space-y-4">
              <div className="w-14 h-14 rounded-full bg-rose-100 dark:bg-rose-900/60 flex items-center justify-center mx-auto text-rose-600 dark:text-rose-400">
                <AlertCircle className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Verification Failed</h2>
                <p className="text-xs text-rose-600 dark:text-rose-300 mt-1">
                  {errorMessage || 'Invalid or expired verification link.'}
                </p>
              </div>
              <Link to="/login" className="block pt-2">
                <Button variant="outline" size="lg" className="w-full">
                  Return to Sign In
                </Button>
              </Link>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default VerifyEmailPage;
