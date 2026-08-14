import React, { useState } from 'react';
import { NavLink, Link, useNavigate, Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, Search, BarChart2, Calendar, LogOut, Sun, Moon, Menu } from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuthStore } from '../stores/useAuthStore';
import { useThemeStore } from '../stores/useThemeStore';
import { UserAccountMenu } from '../components/navigation/UserAccountMenu';

// Component: NgoLayout
export const NgoLayout = ({ children }) => {
  const { user, logout } = useAuthStore();
  const { resolvedTheme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { label: 'Dashboard', to: '/ngo/dashboard', icon: LayoutDashboard },
    { label: 'Browse Donations', to: '/ngo/browse', icon: Search },
    { label: 'Pickups', to: '/ngo/reservations', icon: Calendar },
    { label: 'Impact', to: '/ngo/impact', icon: BarChart2 },
  ];

  const sidebarContent = (
    <>
      <Link to="/" onClick={() => setMobileOpen(false)} className="flex items-center gap-3 px-4 h-16 border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center flex-shrink-0 shadow-md shadow-indigo-500/20">
          <span className="text-white text-xs font-black tracking-wider">NGO</span>
        </div>
        <div className="flex flex-col overflow-hidden">
          <span className="text-sm font-extrabold font-display bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-300 bg-clip-text text-transparent tracking-tight">
            Food Rescue
          </span>
          <span className="text-[10px] font-semibold text-indigo-600/80 dark:text-indigo-400/80 -mt-1 tracking-wider uppercase">Community Portal</span>
        </div>
      </Link>
      <nav className="flex-1 p-2 space-y-1" aria-label="NGO navigation">
        {navItems.map(({ label, to, icon: Icon }) => (
          <NavLink key={to} to={to} onClick={() => setMobileOpen(false)}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all duration-200',
              isActive
                ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200/50 dark:border-indigo-800/50 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/80 dark:hover:text-slate-100'
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">{label}</span>
          </NavLink>
        ))}
      </nav>
    </>
  );

  return (
    <div className="flex h-full bg-slate-50 dark:bg-slate-950">
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/40 lg:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      <aside className="hidden lg:flex flex-col w-60 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 h-full flex-shrink-0">
        {sidebarContent}
      </aside>

      <AnimatePresence>
        {mobileOpen && (
          <motion.aside
            initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
            transition={{ type: 'spring', stiffness: 350, damping: 30 }}
            className="fixed inset-y-0 left-0 z-50 flex flex-col w-60 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 lg:hidden"
          >
            {sidebarContent}
          </motion.aside>
        )}
      </AnimatePresence>

      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <header className="h-14 flex items-center gap-3 px-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex-shrink-0">
          <button className="lg:hidden p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => setMobileOpen(true)} aria-label="Open navigation menu">
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          <UserAccountMenu />
        </header>
        <main className="flex-1 overflow-y-auto">
          <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.18 }} className="h-full">
            {children || <Outlet />}
          </motion.div>
        </main>
      </div>
    </div>
  );
};

