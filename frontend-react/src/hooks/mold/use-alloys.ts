"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Alloy } from "@/types/mold/alloy"
import { useMolds } from "@/hooks/mold/use-molds" // Import useMolds here

/**
 * Mock API functions for alloys
 * In a real application, these would be replaced with actual API calls
 */
const mockAlloys: Alloy[] = [
  {
    id: "1",
    name: "Aluminum",
  },
  {
    id: "2",
    name: "Steel",
  },
  {
    id: "3",
    name: "Brass",
  },
  {
    id: "4",
    name: "Bronze",
  },
  {
    id: "5",
    name: "Zinc",
  },
]

/**
 * Custom hook for managing alloys data
 */
export function useAlloys() {
  const queryClient = useQueryClient()
  const { data: molds, updateMold } = useMolds() // Call useMolds here

  /**
   * Fetch all alloys
   */
  const fetchAlloys = async (): Promise<Alloy[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockAlloys
  }

  /**
   * Create a new alloy
   */
  const createAlloyFn = async (alloy: Omit<Alloy, "id">): Promise<Alloy> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Generate a new ID
    const newAlloy: Alloy = {
      ...alloy,
      id: Math.random().toString(36).substring(2, 9),
    }

    // Add to mock data
    mockAlloys.push(newAlloy)

    return newAlloy
  }

  /**
   * Update an existing alloy
   */
  const updateAlloyFn = async (alloy: Alloy): Promise<Alloy> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and update the alloy
    const index = mockAlloys.findIndex((a) => a.id === alloy.id)
    if (index === -1) {
      throw new Error("Alloy not found")
    }

    // Get the old name before updating
    const oldName = mockAlloys[index].name

    // Update the alloy
    mockAlloys[index] = alloy

    // If the name changed, update all molds that use this alloy
    if (oldName !== alloy.name) {
      // In a real application, this would be a separate API call

      if (molds) {
        for (const mold of molds) {
          if (mold.alloy === oldName) {
            await updateMold({ ...mold, alloy: alloy.name })
          }
        }
      }
    }

    return alloy
  }

  /**
   * Delete an alloy
   */
  const deleteAlloyFn = async (id: string): Promise<void> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and remove the alloy
    const index = mockAlloys.findIndex((a) => a.id === id)
    if (index === -1) {
      throw new Error("Alloy not found")
    }

    // Get the alloy name before removing it
    const alloyName = mockAlloys[index].name

    // Remove the alloy
    mockAlloys.splice(index, 1)

    // Update all molds that use this alloy
    // In a real application, this would be a separate API call
    if (molds) {
      for (const mold of molds) {
        if (mold.alloy === alloyName) {
          await updateMold({ ...mold, alloy: "" })
        }
      }
    }
  }

  /**
   * Query for fetching alloys
   */
  const query = useQuery({
    queryKey: ["alloys"],
    queryFn: fetchAlloys,
  })

  /**
   * Mutation for creating an alloy
   */
  const createMutation = useMutation({
    mutationFn: createAlloyFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alloys"] })
    },
  })

  /**
   * Mutation for updating an alloy
   */
  const updateMutation = useMutation({
    mutationFn: updateAlloyFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alloys"] })
      // Also invalidate molds query since we might have updated molds
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for deleting an alloy
   */
  const deleteMutation = useMutation({
    mutationFn: deleteAlloyFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alloys"] })
      // Also invalidate molds query since we might have updated molds
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    createAlloy: createMutation.mutateAsync,
    updateAlloy: updateMutation.mutateAsync,
    deleteAlloy: deleteMutation.mutateAsync,
  }
}

