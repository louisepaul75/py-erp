"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { MoldSize } from "@/types/mold/mold-size"
import { useMolds } from "@/hooks/mold/use-molds"

/**
 * Mock API functions for mold sizes
 * In a real application, these would be replaced with actual API calls
 */
const mockMoldSizes: MoldSize[] = [
  {
    id: "1",
    name: "Small",
    description: "Small mold size (up to 10cm)",
  },
  {
    id: "2",
    name: "Medium",
    description: "Medium mold size (10-20cm)",
  },
  {
    id: "3",
    name: "Large",
    description: "Large mold size (20-30cm)",
  },
  {
    id: "4",
    name: "Extra Large",
    description: "Extra large mold size (over 30cm)",
  },
]

/**
 * Custom hook for managing mold sizes data
 */
export function useMoldSizes() {
  const queryClient = useQueryClient()
  const { data: molds, updateMold } = useMolds()

  /**
   * Fetch all mold sizes
   */
  const fetchMoldSizes = async (): Promise<MoldSize[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockMoldSizes
  }

  /**
   * Create a new mold size
   */
  const createMoldSizeFn = async (moldSize: Omit<MoldSize, "id">): Promise<MoldSize> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Generate a new ID
    const newMoldSize: MoldSize = {
      ...moldSize,
      id: Math.random().toString(36).substring(2, 9),
    }

    // Add to mock data
    mockMoldSizes.push(newMoldSize)

    return newMoldSize
  }

  /**
   * Update an existing mold size
   */
  const updateMoldSizeFn = async (moldSize: MoldSize): Promise<MoldSize> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and update the mold size
    const index = mockMoldSizes.findIndex((s) => s.id === moldSize.id)
    if (index === -1) {
      throw new Error("Mold size not found")
    }

    // Get the old name before updating
    const oldName = mockMoldSizes[index].name

    // Update the mold size
    mockMoldSizes[index] = moldSize

    // If the name changed, update all molds that use this mold size
    if (oldName !== moldSize.name && molds) {
      for (const mold of molds) {
        if (mold.moldSize === oldName) {
          await updateMold({ ...mold, moldSize: moldSize.name })
        }
      }
    }

    return moldSize
  }

  /**
   * Delete a mold size
   */
  const deleteMoldSizeFn = async (id: string): Promise<void> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and remove the mold size
    const index = mockMoldSizes.findIndex((s) => s.id === id)
    if (index === -1) {
      throw new Error("Mold size not found")
    }

    // Get the mold size name before removing it
    const sizeName = mockMoldSizes[index].name

    // Remove the mold size
    mockMoldSizes.splice(index, 1)

    // Update all molds that use this mold size
    if (molds) {
      for (const mold of molds) {
        if (mold.moldSize === sizeName) {
          await updateMold({ ...mold, moldSize: "" })
        }
      }
    }
  }

  /**
   * Query for fetching mold sizes
   */
  const query = useQuery({
    queryKey: ["moldSizes"],
    queryFn: fetchMoldSizes,
  })

  /**
   * Mutation for creating a mold size
   */
  const createMutation = useMutation({
    mutationFn: createMoldSizeFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["moldSizes"] })
    },
  })

  /**
   * Mutation for updating a mold size
   */
  const updateMutation = useMutation({
    mutationFn: updateMoldSizeFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["moldSizes"] })
      // Also invalidate molds query since we might have updated molds
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for deleting a mold size
   */
  const deleteMutation = useMutation({
    mutationFn: deleteMoldSizeFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["moldSizes"] })
      // Also invalidate molds query since we might have updated molds
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    createMoldSize: createMutation.mutateAsync,
    updateMoldSize: updateMutation.mutateAsync,
    deleteMoldSize: deleteMutation.mutateAsync,
  }
}

