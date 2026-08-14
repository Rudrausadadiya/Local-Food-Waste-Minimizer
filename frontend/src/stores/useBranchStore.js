import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useBranchStore = create()(
  persist(
    (set) => ({
      activeBusinessId: null,
      activeBranchId: null,
      branches: [],

      setBusiness: (id) => set({ activeBusinessId: id }),
      setActiveBranch: (branchId) => set({ activeBranchId: branchId }),
      setBranches: (branches) =>
        set((state) => ({
          branches,
          activeBranchId:
            state.activeBranchId && branches.some((b) => b.id === state.activeBranchId)
              ? state.activeBranchId
              : branches[0]?.id ?? null,
        })),
      reset: () => set({ activeBusinessId: null, activeBranchId: null, branches: [] }),
    }),
    {
      name: 'fw-branch',
    }
  )
);
