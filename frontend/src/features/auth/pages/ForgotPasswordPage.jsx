import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Leaf, ArrowLeft, CheckCircle } from 'lucide-react';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { useToastStore } from '../../../stores/useToastStore';
import { authApi } from '../api/authApi';

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
});

// Component: ForgotPasswordPage
export const ForgotPasswordPage = () => {
  const { addToast } = useToastStore();
  const [submitted, setSubmitted] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    mode: 'onBlur',
  });

  const mutation = useMutation({
    mutationFn: (email) => authApi.forgotPassword(email),
    onSuccess: () => {
      setSubmitted(true);
      addToast({ title: 'Request Sent', description: 'Check your email for reset instructions.', variant: 'success' });
    },
    onError: (error) => {
      const data = error?.response?.data;
      let msg = 'Failed to request password reset. Please try again.';
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
      addToast({ title: 'Request failed', description: msg, variant: 'error' });
    },
  });

  // Function: onSubmit
  const onSubmit = (data) => mutation.mutate(data.email);

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
          className="w-full max-w-sm"
        >
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Forgot password</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Enter your email address and we'll send you a link to reset your password.
            </p>
          </div>

          {submitted ? (
            <div className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl p-6 text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/60 flex items-center justify-center mx-auto text-emerald-600 dark:text-emerald-400">
                <CheckCircle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Check your inbox</h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  If an account exists for that email, we've sent a reset link. Please check your inbox and follow the instructions.
                </p>
              </div>
              <Link to="/login" className="inline-flex items-center gap-2 text-xs font-semibold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400">
                <ArrowLeft className="w-4 h-4" /> Back to sign in
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
              <Input
                label="Email address"
                type="email"
                placeholder="you@example.com"
                error={errors.email?.message}
                autoComplete="email"
                {...register('email')}
              />

              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={mutation.isPending}
                className="w-full"
              >
                Send Reset Link
              </Button>

              <div className="pt-2 text-center">
                <Link to="/login" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 font-medium">
                  <ArrowLeft className="w-3.5 h-3.5" /> Back to sign in
                </Link>
              </div>
            </form>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
