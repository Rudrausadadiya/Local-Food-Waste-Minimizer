import React from 'react';
import { NavLink, Link, useNavigate, Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, ShoppingBag, Heart, LogOut, Sun, Moon } from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuthStore } from '../stores/useAuthStore';
import { useThemeStore } from '../stores/useThemeStore';
import { UserAccountMenu } from '../components/navigation/UserAccountMenu';

// Component: CustomerLayout
export const CustomerLayout = ({ children }) => {
  const { user, logout } = useAuthStore();
  const { resolvedTheme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-full bg-slate-50/80 dark:bg-slate-950">
      <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-800/80 flex-shrink-0 sticky top-0 z-[10000] shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 via-teal-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform duration-200">
              <span className="text-white text-xs font-black tracking-wider">FW</span>
            </div>
            <div className="hidden sm:flex flex-col">
              <span className="text-base font-extrabold font-display bg-gradient-to-r from-emerald-700 via-teal-600 to-emerald-600 dark:from-emerald-400 dark:to-teal-300 bg-clip-text text-transparent tracking-tight">
                FoodWaste
              </span>
              <span className="text-[10px] font-semibold text-emerald-600/80 dark:text-emerald-400/80 -mt-1 tracking-wider uppercase">Minimizer</span>
            </div>
          </Link>

          <div className="flex-1" />

          <nav className="flex items-center gap-1.5" aria-label="Customer navigation">
            {[
              { label: 'Browse', to: '/customer/browse', icon: ShoppingBag },
              { label: 'Saved', to: '/customer/saved', icon: Heart },
              { label: 'Orders', to: '/customer/orders', icon: LayoutDashboard },
            ].map(({ label, to, icon: Icon }) => (
              <NavLink key={to} to={to}
                className={({ isActive }) => cn(
                  'flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all duration-200',
                  isActive
                    ? 'text-emerald-700 bg-emerald-50 dark:text-emerald-300 dark:bg-emerald-950/60 shadow-xs border border-emerald-200/50 dark:border-emerald-800/50'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 dark:text-slate-400 dark:hover:text-slate-100 dark:hover:bg-slate-800/80'
                )}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>

          <UserAccountMenu />
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.18, ease: 'easeOut' }}
          className="h-full"
        >
          {children || <Outlet />}
        </motion.div>
      </main>
    </div>
  );
};
