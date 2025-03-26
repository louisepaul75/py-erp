import { create } from 'zustand'

export interface Scale {
  id: string
  name: string
  ipAddress: string
  tolerance: number
}

interface ScaleStore {
  scales: Scale[]
  addScale: (scale: Scale) => void
  updateScale: (id: string, updatedScale: Scale) => void
  deleteScale: (id: string) => void
}

export const useScaleStore = create<ScaleStore>((set) => ({
  scales: [],
  
  addScale: (scale) =>
    set((state) => ({
      scales: [...state.scales, scale],
    })),

  updateScale: (id, updatedScale) =>
    set((state) => ({
      scales: state.scales.map((s) =>
        s.id === id ? updatedScale : s
      ),
    })),

  deleteScale: (id) =>
    set((state) => ({
      scales: state.scales.filter((s) => s.id !== id),
    })),
})) 