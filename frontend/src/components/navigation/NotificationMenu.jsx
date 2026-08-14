import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, Check, CheckCheck, Inbox, AlertTriangle, Info, ShieldAlert } from 'lucide-react';
import { notificationsApi } from '../../features/notifications/api/notificationsApi';
import { useToastStore } from '../../stores/useToastStore';
import { cn, formatDateTime } from '../../lib/utils';

// Component: NotificationMenu
export const NotificationMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const qc = useQueryClient();
  const { addToast } = useToastStore();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.getNotifications(),
    refetchInterval: 30000,
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const markAsReadMutation = useMutation({
    mutationFn: (id) => notificationsApi.markAsRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationsApi.markAllAsRead(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] });
      addToast({ title: 'Notifications cleared', variant: 'success' });
    },
  });

  useEffect(() => {
    // Function: handleClickOutside
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Function: getIcon
  const getIcon = (type) => {
    switch (type) {
      case 'ORDER': return <Inbox className="w-4 h-4 text-emerald-500" />;
      case 'ALERT': return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case 'SECURITY': return <ShieldAlert className="w-4 h-4 text-red-500" />;
      default: return <Info className="w-4 h-4 text-sky-500" />;
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white dark:ring-slate-900" />
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.96 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl z-50 flex flex-col overflow-hidden"
          >
            <div className="p-3 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
              <h3 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                Notifications
                {unreadCount > 0 && (
                  <span className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300 text-[10px] px-2 py-0.5 rounded-full font-bold">
                    {unreadCount} New
                  </span>
                )}
              </h3>
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllAsReadMutation.mutate()}
                  disabled={markAllAsReadMutation.isPending}
                  className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 flex items-center gap-1 font-medium transition-colors"
                >
                  <CheckCheck className="w-3.5 h-3.5" /> Mark all read
                </button>
              )}
            </div>

            <div className="max-h-[60vh] overflow-y-auto">
              {isLoading ? (
                <div className="p-4 space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 animate-pulse flex-shrink-0" />
                      <div className="flex-1 space-y-2">
                        <div className="h-3 w-3/4 bg-slate-100 dark:bg-slate-800 rounded animate-pulse" />
                        <div className="h-2 w-1/2 bg-slate-100 dark:bg-slate-800 rounded animate-pulse" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-8 text-center text-slate-500 dark:text-slate-400">
                  <Bell className="w-8 h-8 mx-auto mb-2 opacity-20" />
                  <p className="text-sm font-medium">No notifications yet</p>
                  <p className="text-xs opacity-70">We'll let you know when something arrives.</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {notifications.map((n) => (
                    <div
                      key={n.id}
                      className={cn(
                        "p-4 flex gap-3 transition-colors",
                        n.is_read ? "opacity-70" : "bg-slate-50/50 dark:bg-slate-800/20"
                      )}
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        <div className={cn(
                          "w-8 h-8 rounded-full flex items-center justify-center",
                          n.is_read ? "bg-slate-100 dark:bg-slate-800" : "bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-100 dark:border-emerald-900"
                        )}>
                          {getIcon(n.notification_type)}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={cn(
                          "text-sm mb-0.5",
                          n.is_read ? "text-slate-700 dark:text-slate-300 font-medium" : "text-slate-900 dark:text-slate-100 font-bold"
                        )}>
                          {n.title}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                          {n.message}
                        </p>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-[10px] text-slate-400 font-medium">
                            {formatDateTime(n.created_at)}
                          </span>
                          {!n.is_read && (
                            <button
                              onClick={() => markAsReadMutation.mutate(n.id)}
                              className="text-[10px] text-emerald-600 dark:text-emerald-400 hover:underline font-bold"
                            >
                              Mark read
                            </button>
                          )}
                        </div>
                      </div>
                      {!n.is_read && (
                        <div className="flex-shrink-0 mt-1">
                          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {notifications.length > 0 && (
              <div className="p-2 border-t border-slate-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/80 text-center">
                <span className="text-[10px] text-slate-400">End of notifications</span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
