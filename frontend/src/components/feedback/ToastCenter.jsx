import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { X, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';
import { useToastStore } from '../../stores/useToastStore';
import { cn } from '../../lib/utils';

const VARIANTS = {
  success: {
    icon: <CheckCircle className="w-4 h-4" />,
    iconCls: 'text-emerald-500',
    bar: 'bg-emerald-500',
    border: 'border-emerald-200 dark:border-emerald-800',
  },
  error: {
    icon: <XCircle className="w-4 h-4" />,
    iconCls: 'text-red-500',
    bar: 'bg-red-500',
    border: 'border-red-200 dark:border-red-800',
  },
  warning: {
    icon: <AlertTriangle className="w-4 h-4" />,
    iconCls: 'text-amber-500',
    bar: 'bg-amber-500',
    border: 'border-amber-200 dark:border-amber-800',
  },
  info: {
    icon: <Info className="w-4 h-4" />,
    iconCls: 'text-sky-500',
    bar: 'bg-sky-500',
    border: 'border-sky-200 dark:border-sky-800',
  },
};

/**
 * Individual toast with a CSS-only progress bar (no framer-motion on the bar)
 * to avoid the spring-parent / linear-child timing desync.
 */
// Component: Toast
const Toast = ({ toast, onRemove }) => {
  const config = VARIANTS[toast.variant] || VARIANTS.info;
  const duration = toast.duration ?? 4000;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -16, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -12, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
      className={cn(
        'pointer-events-auto w-80 rounded-xl border bg-white dark:bg-slate-900 shadow-xl overflow-hidden',
        config.border
      )}
    >
      {/* CSS-animated progress bar — completely independent of framer motion */}
      <div
        className={cn('h-0.5', config.bar)}
        style={{
          transformOrigin: 'left',
          animation: `toast-drain ${duration}ms linear forwards`,
        }}
      />
      <div className="flex items-start gap-3 p-4">
        <span className={cn('mt-0.5 flex-shrink-0', config.iconCls)}>
          {config.icon}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 leading-snug">
            {toast.title}
          </p>
          {toast.description && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
              {toast.description}
            </p>
          )}
        </div>
        <button
          onClick={() => onRemove(toast.id)}
          className="flex-shrink-0 ml-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </motion.div>
  );
};

// Component: ToastCenter
export const ToastCenter = () => {
  const { toasts, removeToast, addToast } = useToastStore();

  useEffect(() => {
    // Function: handleCustomToast
    const handleCustomToast = (e) => {
      if (e.detail) {
        addToast(e.detail);
      }
    };
    window.addEventListener('show-toast', handleCustomToast);
    return () => window.removeEventListener('show-toast', handleCustomToast);
  }, [addToast]);

  return createPortal(
    <div
      aria-live="polite"
      aria-atomic="false"
      className="fixed top-4 right-4 z-[99999] flex flex-col gap-2 pointer-events-none"
      style={{ maxWidth: 'calc(100vw - 2rem)' }}
    >
      <AnimatePresence initial={false}>
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onRemove={removeToast} />
        ))}
      </AnimatePresence>
    </div>,
    document.body
  );
};
