import { create } from 'zustand'

export interface Purpose {
  id: string
  name: string
}

interface PurposeStore {
  purposes: Purpose[]
  addPurpose: (purpose: Purpose) => void
  deletePurpose: (id: string) => void
}

export const usePurposeStore = create<PurposeStore>((set) => ({
  purposes: [],
  
  addPurpose: (purpose) =>
    set((state) => ({
      purposes: [...state.purposes, purpose],
    })),

  deletePurpose: (id) =>
    set((state) => ({
      purposes: state.purposes.filter((p) => p.id !== id),
    })),
})) 