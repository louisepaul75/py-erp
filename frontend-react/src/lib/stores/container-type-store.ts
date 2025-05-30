import { create } from 'zustand'
import { fetchContainerTypes } from '../api/container-types'

export interface ContainerTypeImage {
  id: string
  url: string
}

export interface ContainerType {
  id: string
  name: string
  manufacturer: string
  articleNumber: string
  length: number
  width: number
  height: number
  boxWeight: number
  dividerWeight: number
  standardSlots: number
  images: ContainerTypeImage[]
}

interface ContainerTypeStore {
  containerTypes: ContainerType[]
  isLoading: boolean
  error: string | null
  fetchContainerTypes: () => Promise<void>
  addContainerType: (containerType: ContainerType) => void
  updateContainerType: (id: string, updatedContainerType: ContainerType) => void
  deleteContainerType: (id: string) => void
  addImageToContainerType: (containerId: string, image: ContainerTypeImage) => void
  deleteImageFromContainerType: (containerId: string, imageId: string) => void
}

export const useContainerTypeStore = create<ContainerTypeStore>((set) => ({
  containerTypes: [],
  isLoading: false,
  error: null,
  
  fetchContainerTypes: async () => {
    set({ isLoading: true, error: null })
    try {
      const types = await fetchContainerTypes()
      set({ containerTypes: types, isLoading: false })
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
    }
  },

  addContainerType: (containerType) =>
    set((state) => ({
      containerTypes: [...state.containerTypes, containerType],
    })),

  updateContainerType: (id, updatedContainerType) =>
    set((state) => ({
      containerTypes: state.containerTypes.map((ct) =>
        ct.id === id ? updatedContainerType : ct
      ),
    })),

  deleteContainerType: (id) =>
    set((state) => ({
      containerTypes: state.containerTypes.filter((ct) => ct.id !== id),
    })),

  addImageToContainerType: (containerId, image) =>
    set((state) => ({
      containerTypes: state.containerTypes.map((ct) =>
        ct.id === containerId
          ? { ...ct, images: [...ct.images, image] }
          : ct
      ),
    })),

  deleteImageFromContainerType: (containerId, imageId) =>
    set((state) => ({
      containerTypes: state.containerTypes.map((ct) =>
        ct.id === containerId
          ? { ...ct, images: ct.images.filter((img) => img.id !== imageId) }
          : ct
      ),
    })),
})) 