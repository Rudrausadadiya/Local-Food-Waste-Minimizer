import React, { useState } from 'react';
import { NavLink, Link, useNavigate, Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, Building2, ShoppingBag, Users, BarChart2, LogOut, Sun, Moon, Menu } from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuthStore } from '../stores/useAuthStore';
import { useThemeStore } from '../stores/useThemeStore';
import { UserAccountMenu } from '../components/navigation/UserAccountMenu';

// Component: AdminLayout
export const AdminLayout = ({ children }) => {
  const { user, logout } = useAuthStore();
  const { resolvedTheme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { label: 'Dashboard', to: '/admin/dashboard', icon: LayoutDashboard },
    { label: 'Businesses', to: '/admin/businesses', icon: Building2 },
    { label: 'Listings', to: '/admin/listings', icon: ShoppingBag },
    { label: 'Users', to: '/admin/users', icon: Users },
    { label: 'Analytics', to: '/admin/analytics', icon: BarChart2 },
  ];

  const sidebarContent = (
    <>
      <Link to="/admin/dashboard" onClick={() => setMobileOpen(false)} className="flex items-center gap-3 px-4 h-14 border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
        <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
          <span className="text-white text-xs font-bold">ADM</span>
        </div>
        <span className="text-sm font-bold text-slate-100">Platform Admin</span>
      </Link>
      <nav className="flex-1 p-2 space-y-0.5" aria-label="Admin navigation">
        {navItems.map(({ label, to, icon: Icon }) => (
          <NavLink key={to} to={to} onClick={() => setMobileOpen(false)}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              isActive
                ? 'bg-slate-800 text-white'
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
            )}
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-slate-800 flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-emerald-600 flex items-center justify-center text-white text-xs font-semibold">
          {user?.first_name?.[0]}{user?.last_name?.[0]}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-slate-200 truncate">{user?.first_name} {user?.last_name}</p>
          <p className="text-xs text-slate-500 truncate">Administrator</p>
        </div>
        <button onClick={() => { setMobileOpen(false); logout(); navigate('/login'); }} className="text-slate-500 hover:text-slate-300" aria-label="Log out"><LogOut className="w-4 h-4" /></button>
      </div>
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

      <aside className="hidden lg:flex flex-col w-56 bg-slate-900 h-full flex-shrink-0 border-r border-slate-800">
        {sidebarContent}
      </aside>

      <AnimatePresence>
        {mobileOpen && (
          <motion.aside
            initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
            transition={{ type: 'spring', stiffness: 350, damping: 30 }}
            className="fixed inset-y-0 left-0 z-50 flex flex-col w-56 bg-slate-900 border-r border-slate-800 lg:hidden"
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

