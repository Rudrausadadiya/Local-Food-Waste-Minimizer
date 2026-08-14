import { create } from 'zustand';

export const useToastStore = create((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = crypto.randomUUID();
    set((state) => {
      const isDuplicate = state.toasts.some(
        (t) => t.title === toast.title && t.description === toast.description
      );
      if (isDuplicate) return state;
      return { toasts: [...state.toasts, { ...toast, id }] };
    });
    const duration = toast.duration ?? 4000;
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
    }, duration);
  },

  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),

  clearToasts: () => set({ toasts: [] }),
}));
