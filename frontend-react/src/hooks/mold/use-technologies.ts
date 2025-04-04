"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Technology } from "@/types/mold/technology"
import { useMolds } from "@/hooks/mold/use-molds" // Import useMolds here

/**
 * Mock API functions for technologies
 * In a real application, these would be replaced with actual API calls
 */
const mockTechnologies: Technology[] = [
  {
    id: "1",
    name: "Die Casting",
  },
  {
    id: "2",
    name: "Injection Molding",
  },
  {
    id: "3",
    name: "Sand Casting",
  },
  {
    id: "4",
    name: "Investment Casting",
  },
]

/**
 * Custom hook for managing technologies data
 */
export function useTechnologies() {
  const queryClient = useQueryClient()
  const { data: molds, updateMold } = useMolds() // Call useMolds here

  /**
   * Fetch all technologies
   */
  const fetchTechnologies = async (): Promise<Technology[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockTechnologies
  }

  /**
   * Create a new technology
   */
  const createTechnologyFn = async (technology: Omit<Technology, "id">): Promise<Technology> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Generate a new ID
    const newTechnology: Technology = {
      ...technology,
      id: Math.random().toString(36).substring(2, 9),
    }

    // Add to mock data
    mockTechnologies.push(newTechnology)

    return newTechnology
  }

  /**
   * Update an existing technology
   */
  const updateTechnologyFn = async (technology: Technology): Promise<Technology> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and update the technology
    const index = mockTechnologies.findIndex((t) => t.id === technology.id)
    if (index === -1) {
      throw new Error("Technology not found")
    }

    // Get the old name before updating
    const oldName = mockTechnologies[index].name

    // Update the technology
    mockTechnologies[index] = technology

    // If the name changed, update all molds that use this technology
    if (oldName !== technology.name) {
      // In a real application, this would be a separate API call
      // const { useMolds } = await import("@/hooks/use-molds"); // No longer needed here
      // const { data: molds, updateMold } = useMolds(); // No longer needed here

      if (molds) {
        for (const mold of molds) {
          if (mold.technology === oldName) {
            await updateMold({ ...mold, technology: technology.name })
          }
        }
      }
    }

    return technology
  }

  /**
   * Delete a technology
   */
  const deleteTechnologyFn = async (id: string): Promise<void> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and remove the technology
    const index = mockTechnologies.findIndex((t) => t.id === id)
    if (index === -1) {
      throw new Error("Technology not found")
    }

    // Get the technology name before removing it
    const techName = mockTechnologies[index].name

    // Remove the technology
    mockTechnologies.splice(index, 1)

    // Update all molds that use this technology
    // In a real application, this would be a separate API call
    // const { useMolds } = await import("@/hooks/use-molds"); // No longer needed here
    // const { data: molds, updateMold } = useMolds(); // No longer needed here

    if (molds) {
      for (const mold of molds) {
        if (mold.technology === techName) {
          await updateMold({ ...mold, technology: "" })
        }
      }
    }
  }

  /**
   * Query for fetching technologies
   */
  const query = useQuery({
    queryKey: ["technologies"],
    queryFn: fetchTechnologies,
  })

  /**
   * Mutation for creating a technology
   */
  const createMutation = useMutation({
    mutationFn: createTechnologyFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["technologies"] })
    },
  })

  /**
   * Mutation for updating a technology
   */
  const updateMutation = useMutation({
    mutationFn: updateTechnologyFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["technologies"] })
      // Also invalidate molds query since we might have updated molds
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for deleting a technology
   */
  const deleteMutation = useMutation({
    mutationFn: deleteTechnologyFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["technologies"] })
      // Also invalidate molds query since we might have updated molds
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    createTechnology: createMutation.mutateAsync,
    updateTechnology: updateMutation.mutateAsync,
    deleteTechnology: deleteMutation.mutateAsync,
  }
}

