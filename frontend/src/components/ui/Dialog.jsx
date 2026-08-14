import React, { useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

const sizeClasses = { sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl' };

export const Dialog = ({
  open, onClose, title, description, children, className, size = 'md'
}) => {
  useEffect(() => {
    // Function: handler
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    if (open) document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="dialog-title">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 8 }}
            transition={{ type: 'spring', stiffness: 350, damping: 28 }}
            className={cn(
              'relative w-full m-auto max-h-[85vh] flex flex-col rounded-2xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden',
              sizeClasses[size],
              className
            )}
          >
            <div className="flex items-start justify-between gap-4 p-6 border-b border-slate-100 dark:border-slate-800 flex-shrink-0">
              <div>
                <h2 id="dialog-title" className="text-base font-semibold text-slate-900 dark:text-slate-100">
                  {title}
                </h2>
                {description && (
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{description}</p>
                )}
              </div>
              <button
                onClick={onClose}
                className="rounded-lg p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-6 flex-1 overflow-y-auto min-h-0">{children}</div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export const ConfirmDialog = ({
  open, onClose, onConfirm, title, description, confirmLabel = 'Confirm', confirmVariant = 'destructive', loading
}) => (
  <Dialog open={open} onClose={onClose} title={title} description={description} size="sm">
    <div className="flex gap-3 justify-end">
      <Button variant="outline" onClick={onClose} disabled={loading}>Cancel</Button>
      <Button variant={confirmVariant} onClick={onConfirm} loading={loading}>{confirmLabel}</Button>
    </div>
  </Dialog>
);
