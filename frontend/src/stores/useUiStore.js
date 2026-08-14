import { create } from 'zustand';

export const useUiStore = create((set) => ({
  isSidebarCollapsed: false,
  activeModal: null,

  toggleSidebar: () =>
    set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

  openModal: (id) => set({ activeModal: id }),
  closeModal: () => set({ activeModal: null }),
}));
