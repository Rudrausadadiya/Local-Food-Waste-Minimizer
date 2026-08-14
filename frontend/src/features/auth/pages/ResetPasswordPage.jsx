import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Leaf, ArrowLeft, AlertCircle } from 'lucide-react';
import { PasswordInput } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { useToastStore } from '../../../stores/useToastStore';
import { authApi } from '../api/authApi';

const schema = z.object({
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

// Component: ResetPasswordPage
export const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { addToast } = useToastStore();
  const [inlineError, setInlineError] = useState(null);

  const uidb64 = searchParams.get('uidb64') || searchParams.get('uid');
  const token = searchParams.get('token');

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    mode: 'onBlur',
  });

  const mutation = useMutation({
    mutationFn: (data) => authApi.resetPassword(data),
    onSuccess: () => {
      addToast({ title: 'Password Reset', description: 'Your password has been successfully updated.', variant: 'success' });
      navigate('/login', { replace: true });
    },
    onError: (error) => {
      const data = error?.response?.data;
      let msg = 'Unable to reset password. The link may be invalid or expired.';
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
      setInlineError(msg);
      addToast({ title: 'Reset Failed', description: msg, variant: 'error' });
    },
  });

  // Function: onSubmit
  const onSubmit = (data) => {
    if (!uidb64 || !token) {
      setInlineError('Missing or invalid reset token. Please request a new password reset link.');
      return;
    }
    setInlineError(null);
    mutation.mutate({
      uidb64,
      token,
      new_password: data.new_password,
    });
  };

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
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Set new password</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Please enter and confirm your new password below.
            </p>
          </div>

          {(inlineError || (!uidb64 || !token)) && (
            <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{inlineError || 'Invalid or missing password reset link. Please request a new link.'}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <PasswordInput
              label="New Password"
              placeholder="Min 8 characters"
              error={errors.new_password?.message}
              autoComplete="new-password"
              {...register('new_password')}
            />

            <PasswordInput
              label="Confirm New Password"
              placeholder="Re-enter new password"
              error={errors.confirm_password?.message}
              autoComplete="new-password"
              {...register('confirm_password')}
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={mutation.isPending}
              disabled={!uidb64 || !token}
              className="w-full"
            >
              Reset Password
            </Button>

            <div className="pt-2 text-center">
              <Link to="/login" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 font-medium">
                <ArrowLeft className="w-3.5 h-3.5" /> Back to sign in
              </Link>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
};

export default ResetPasswordPage;
