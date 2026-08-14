import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Leaf } from 'lucide-react';
import { Input, PasswordInput } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { useAuthStore } from '../../../stores/useAuthStore';
import { useToastStore } from '../../../stores/useToastStore';
import { authApi } from '../api/authApi';

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
});

// Component: LoginPage
export const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setAuth } = useAuthStore();
  const { addToast } = useToastStore();
  const from = location.state?.from?.pathname;

  const rememberedEmail = typeof window !== 'undefined' ? localStorage.getItem('remembered_email') : null;

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    mode: 'onBlur',
    defaultValues: {
      email: rememberedEmail || '',
      rememberMe: Boolean(rememberedEmail),
    },
  });

  const mutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data, variables) => {
      setAuth(data.user, data.access, data.refresh);
      if (variables.rememberMe) {
        localStorage.setItem('remembered_email', variables.email);
      } else {
        localStorage.removeItem('remembered_email');
      }
      addToast({ title: 'Welcome back!', description: `Logged in as ${data.user.first_name}`, variant: 'success' });
      const role = data.user.role;
      const status = data.user.business_status;

      if ((role === 'VENDOR' || role === 'NGO') && (status === 'PENDING' || status === 'REJECTED' || status === 'SUSPENDED')) {
        navigate('/onboarding/pending', { replace: true });
        return;
      }

      let defaultDest = '/customer/browse';
      if (role === 'VENDOR') defaultDest = '/vendor/dashboard';
      else if (role === 'NGO') defaultDest = '/ngo/dashboard';
      else if (role === 'ADMIN') defaultDest = '/admin/dashboard';

      let dest = defaultDest;
      if (from) {
        if (role === 'VENDOR' && from.startsWith('/vendor')) dest = from;
        else if (role === 'NGO' && from.startsWith('/ngo')) dest = from;
        else if (role === 'CUSTOMER' && (from.startsWith('/customer') || from.startsWith('/marketplace'))) dest = from;
        else if (role === 'ADMIN' && from.startsWith('/admin')) dest = from;
      }

      navigate(dest, { replace: true });
    },
    onError: (error) => {
      const data = error?.response?.data;
      let msg = 'Invalid credentials. Please try again.';
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
      addToast({ title: 'Login failed', description: msg, variant: 'error' });
    },
  });

  // Function: onSubmit
  const onSubmit = (data) => mutation.mutate(data);

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
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Welcome back</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <Input
              label="Email address"
              type="email"
              placeholder="you@example.com"
              error={errors.email?.message}
              autoComplete="email"
              {...register('email')}
            />
            <PasswordInput
              label="Password"
              placeholder="Your password"
              error={errors.password?.message}
              autoComplete="current-password"
              {...register('password')}
            />

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 cursor-pointer">
                <input type="checkbox" className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" {...register('rememberMe')} />
                Remember me
              </label>
              <Link to="/forgot-password" className="text-sm text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 font-medium">
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={mutation.isPending}
              className="w-full"
            >
              Sign In
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            Don't have an account?{' '}
            <Link to="/signup" className="text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 font-medium">
              Create account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};
