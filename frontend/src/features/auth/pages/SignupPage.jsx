import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Store, HeartHandshake, ShoppingBag, Leaf } from 'lucide-react';
import { Input, PasswordInput } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { cn } from '../../../lib/utils';
import { authApi } from '../api/authApi';
import { useToastStore } from '../../../stores/useToastStore';

const roleCards = [
  { role: 'VENDOR', label: 'Food Business', sub: 'Restaurant, bakery, café, hotel', icon: <Store className="w-6 h-6" /> },
  { role: 'NGO', label: 'NGO / Non-Profit', sub: 'Food rescue organisation', icon: <HeartHandshake className="w-6 h-6" /> },
  { role: 'CUSTOMER', label: 'Customer', sub: 'Buy discounted surplus food', icon: <ShoppingBag className="w-6 h-6" /> },
];

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  business_name: z.string().optional(),
  business_type: z.string().optional(),
});

// Component: SignupPage
export const SignupPage = () => {
  const [selectedRole, setSelectedRole] = useState(null);
  const navigate = useNavigate();
  const { addToast } = useToastStore();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    mode: 'onBlur',
  });

  const mutation = useMutation({
    mutationFn: (data) =>
      authApi.register({ ...data, role: selectedRole ?? 'CUSTOMER' }),
    onSuccess: () => {
      if (selectedRole === 'VENDOR' || selectedRole === 'NGO') {
        addToast({ title: 'Account created!', description: 'Your business is pending approval from our admin team.', variant: 'info' });
        navigate('/onboarding/pending');
      } else {
        addToast({ title: 'Account created!', description: 'Welcome! Please check your email for a verification link, then sign in.', variant: 'success' });
        navigate('/login');
      }
    },
    onError: (error) => {
      const data = error?.response?.data;
      let msg = 'Registration failed. Please try again.';
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
      addToast({ title: 'Registration failed', description: msg, variant: 'error' });
    },
  });

  // Function: onSubmit
  const onSubmit = (data) => {
    if (!selectedRole) return;
    mutation.mutate(data);
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
          <h1 className="text-3xl font-bold text-white leading-tight mb-4">Join the food rescue movement</h1>
          <p className="text-emerald-100 text-sm leading-relaxed">
            Whether you have surplus food to share or want to find incredible deals, we bring businesses, NGOs, and customers together.
          </p>
        </div>
        <p className="text-emerald-200 text-xs">© {new Date().getFullYear()} Local Food Waste Minimizer</p>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.22, ease: 'easeOut' }}
          className="w-full max-w-md py-8"
        >
          <div className="mb-7">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Create your account</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Choose your role to get started</p>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-6">
            {roleCards.map(({ role, label, sub, icon }) => (
              <button
                key={role}
                type="button"
                onClick={() => setSelectedRole(role)}
                className={cn(
                  'flex flex-col items-center gap-2 p-4 rounded-xl border-2 text-center transition-all duration-150',
                  selectedRole === role
                    ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-white dark:bg-slate-900'
                )}
              >
                <span className={cn('text-slate-500', selectedRole === role && 'text-emerald-600 dark:text-emerald-400')}>
                  {icon}
                </span>
                <div>
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{label}</p>
                  <p className="text-xs text-slate-400 mt-0.5 leading-tight">{sub}</p>
                </div>
              </button>
            ))}
          </div>

          <AnimatePresence>
            {selectedRole && (
              <motion.form
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                onSubmit={handleSubmit(onSubmit)}
                className="space-y-4 overflow-hidden"
                noValidate
              >
                <div className="grid grid-cols-2 gap-3">
                  <Input label="First name" error={errors.first_name?.message} placeholder="John" {...register('first_name')} />
                  <Input label="Last name" error={errors.last_name?.message} placeholder="Doe" {...register('last_name')} />
                </div>
                <Input label="Email address" type="email" placeholder="you@example.com" error={errors.email?.message} autoComplete="email" {...register('email')} />
                <PasswordInput label="Password" placeholder="Min. 8 characters" error={errors.password?.message} autoComplete="new-password" {...register('password')} />

                {(selectedRole === 'VENDOR' || selectedRole === 'NGO') && (
                  <>
                    <Input
                      label={selectedRole === 'VENDOR' ? 'Business / Store Name' : 'NGO / Organisation Name'}
                      placeholder={selectedRole === 'VENDOR' ? 'Artisan Bakery & Café' : 'Food Rescue Foundation'}
                      error={errors.business_name?.message}
                      {...register('business_name')}
                    />

                    <div className="flex flex-col gap-1.5">
                      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Category / Entity Type</label>
                      <select
                        className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        {...register('business_type')}
                      >
                        <option value="">Select type...</option>
                        {selectedRole === 'VENDOR' && (
                          <>
                            <option value="VENDOR">Restaurant / Café / Bakery</option>
                            <option value="RETAIL">Grocery / Supermarket</option>
                            <option value="CORPORATE">Corporate / Hotel Catering</option>
                          </>
                        )}
                        {selectedRole === 'NGO' && <option value="NGO">Non-Profit / Food Rescue NGO</option>}
                      </select>
                    </div>

                    <Input
                      label={selectedRole === 'VENDOR' ? 'FSSAI License Number (14 Digits)' : 'NITI Aayog Darpan ID / Trust Reg. No.'}
                      placeholder={selectedRole === 'VENDOR' ? 'e.g. 10020021000123' : 'e.g. GJ/2021/0284920'}
                      error={errors.registration_number?.message}
                      {...register('registration_number')}
                    />

                    <Input
                      label={selectedRole === 'VENDOR' ? 'GSTIN Number (Optional)' : '80G / 12A Tax Exemption Cert No. (Optional)'}
                      placeholder={selectedRole === 'VENDOR' ? 'e.g. 24AAAAA0000A1Z5' : 'e.g. AAATG1234F20211'}
                      error={errors.gst_number?.message}
                      {...register('gst_number')}
                    />
                  </>
                )}

                <Button type="submit" variant="primary" size="lg" loading={mutation.isPending} className="w-full">
                  {selectedRole === 'VENDOR' || selectedRole === 'NGO' ? 'Create Account & Submit for Approval' : 'Create Account'}
                </Button>
              </motion.form>
            )}
          </AnimatePresence>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 font-medium">Sign in</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};
