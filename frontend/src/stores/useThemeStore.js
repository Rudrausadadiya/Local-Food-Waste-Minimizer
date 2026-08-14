import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Function: getSystemTheme
const getSystemTheme = () =>
  window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

// Function: applyTheme
const applyTheme = (resolved) => {
  const root = document.documentElement;
  if (resolved === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
};

export const useThemeStore = create()(
  persist(
    (set, get) => ({
      mode: 'system',
      resolvedTheme: 'light',

      setMode: (mode) => {
        const resolved = mode === 'system' ? getSystemTheme() : mode;
        applyTheme(resolved);
        set({ mode, resolvedTheme: resolved });
      },

      toggleTheme: () => {
        const current = get().resolvedTheme;
        const next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        set({ mode: next, resolvedTheme: next });
      },

      initTheme: () => {
        const { mode } = get();
        const resolved = mode === 'system' ? getSystemTheme() : mode;
        applyTheme(resolved);
        set({ resolvedTheme: resolved });
      },
    }),
    { name: 'fw-theme', partialize: (s) => ({ mode: s.mode }) }
  )
);
