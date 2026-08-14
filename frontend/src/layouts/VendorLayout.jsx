import React, { useState } from 'react';
import { NavLink, Link, useNavigate, Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, Package, ShoppingBag, ClipboardList, Gift,
  BarChart2, GitBranch, ChevronLeft, ChevronRight, Bell, Sun, Moon, LogOut, Menu
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuthStore } from '../stores/useAuthStore';
import { useUiStore } from '../stores/useUiStore';
import { useThemeStore } from '../stores/useThemeStore';
import { BranchSwitcher } from '../features/business/components/BranchSwitcher';
import { UserAccountMenu } from '../components/navigation/UserAccountMenu';
import { NotificationMenu } from '../components/navigation/NotificationMenu';

const navItems = [
  { label: 'Dashboard', to: '/vendor/dashboard', icon: LayoutDashboard },
  { label: 'Inventory', to: '/vendor/inventory', icon: Package },
  { label: 'Marketplace', to: '/vendor/marketplace', icon: ShoppingBag },
  { label: 'Orders', to: '/vendor/orders', icon: ClipboardList },
  { label: 'Donations', to: '/vendor/donations', icon: Gift },
  { label: 'Analytics', to: '/vendor/analytics', icon: BarChart2 },
  { label: 'Branches', to: '/vendor/branches', icon: GitBranch },
];

// Component: VendorLayout
export const VendorLayout = ({ children }) => {
  const { user, logout } = useAuthStore();
  const { isSidebarCollapsed, toggleSidebar } = useUiStore();
  const { resolvedTheme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Function: handleLogout
  const handleLogout = () => { logout(); navigate('/login'); };

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

      <motion.aside
        animate={{ width: isSidebarCollapsed ? 64 : 224 }}
        transition={{ type: 'spring', stiffness: 350, damping: 28 }}
        className="hidden lg:flex flex-col bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 h-full flex-shrink-0 overflow-hidden z-30"
      >
        <Link to="/" className="flex items-center gap-3 px-4 h-16 border-b border-slate-100 dark:border-slate-800 flex-shrink-0 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 via-teal-500 to-emerald-400 flex items-center justify-center flex-shrink-0 shadow-md shadow-emerald-500/20">
            <span className="text-white text-xs font-black tracking-wider">FW</span>
          </div>
          {!isSidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
              className="flex flex-col overflow-hidden"
            >
              <span className="text-sm font-extrabold font-display bg-gradient-to-r from-emerald-700 via-teal-600 to-emerald-600 dark:from-emerald-400 dark:to-teal-300 bg-clip-text text-transparent tracking-tight">
                FoodWaste
              </span>
              <span className="text-[10px] font-semibold text-emerald-600/80 dark:text-emerald-400/80 -mt-1 tracking-wider uppercase">Vendor Hub</span>
            </motion.div>
          )}
        </Link>

        <nav className="flex-1 p-2 space-y-1 overflow-y-auto" aria-label="Vendor navigation">
          {navItems.map(({ label, to, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all duration-200',
                  isActive
                    ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200/50 dark:border-emerald-800/50 shadow-xs'
                    : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/80 dark:hover:text-slate-100'
                )
              }
              title={isSidebarCollapsed ? label : undefined}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {!isSidebarCollapsed && <span className="truncate">{label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="p-2 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={toggleSidebar}
            className="w-full flex items-center justify-center p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isSidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </motion.aside>

      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <header className="h-14 flex items-center gap-3 px-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex-shrink-0">
          <button className="lg:hidden p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => setMobileOpen(true)}>
            <Menu className="w-5 h-5" />
          </button>

          <BranchSwitcher />

          <div className="flex-1" />

          <NotificationMenu />

          <UserAccountMenu />
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
    </div>
  );
};
