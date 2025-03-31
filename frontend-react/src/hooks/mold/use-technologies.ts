"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Technology } from "@/types/mold/technology"
import { useMolds } from "@/hooks/mold/use-molds" // Import useMolds here
import axios from "axios"
import { API_URL as BASE_URL } from "@/lib/config"
import { clientCookieStorage } from "@/lib/auth/clientCookies"
import { AUTH_CONFIG } from "@/lib/config"

/**
 * API URL for mold technologies
 */
const API_URL = `${BASE_URL}/production/molds/technologies/`

/**
 * Mock data for technologies, used as fallback
 */
const mockTechnologies = [
  "Die Casting",
  "Injection Molding",
  "Sand Casting",
  "Precision Casting",
  "Low Pressure Casting",
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
    queryFn: async () => {
      try {
        // Get token from clientCookieStorage
        const token = clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
        
        // Attempt to fetch from the real API
        const response = await axios.get(API_URL, {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        })
        
        // If successful, use the API data
        if (response.status === 200) {
          console.log("Successfully fetched technologies from API", response.data)
          
          // Check the structure of the API response
          if (Array.isArray(response.data)) {
            return response.data;
          } else if (response.data && typeof response.data === 'object') {
            // Check if response.data has a results, data, or items property that is an array
            if (Array.isArray(response.data.results)) {
              return response.data.results;
            } else if (Array.isArray(response.data.data)) {
              return response.data.data;
            } else if (Array.isArray(response.data.items)) {
              return response.data.items;
            } else if (Array.isArray(response.data.technologies)) {
              return response.data.technologies;
            } else {
              // If no recognized array structure, log and fall back to mock data
              console.warn("API response doesn't contain an array of technologies:", response.data);
            }
          }
        }
        
        // If not successful or unrecognized structure, fall back to mock data
        console.warn("Failed to fetch technologies from API, using mock data")
        return mockTechnologies
      } catch (error) {
        console.error("Error fetching technologies:", error)
        if (error.response) {
          console.error("Error response data:", error.response.data)
          console.error("Error response status:", error.response.status)
          console.error("Error response headers:", error.response.headers)
        } else if (error.request) {
          console.error("Error request:", error.request)
        } else {
          console.error("Error message:", error.message)
        }
        return mockTechnologies
      }
    },
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

