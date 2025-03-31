"use client"

import { useQuery } from "@tanstack/react-query"
import axios from "axios"

/**
 * API URL for mold tags
 */
const API_URL = "/api/production/molds/tags/"

/**
 * Mock data for tags, used as fallback
 */
const mockTags = [
  "High Priority",
  "New Design",
  "Maintenance Required",
  "Prototype",
  "Critical",
  "Research",
  "Development"
]

/**
 * Hook to fetch mold tags
 */
export function useTags() {
  return useQuery({
    queryKey: ["tags"],
    queryFn: async () => {
      try {
        // Attempt to fetch from the real API
        const response = await axios.get(API_URL)
        
        // If successful, use the API data
        if (response.status === 200) {
          console.log("Successfully fetched tags from API", response.data)
          return response.data
        }
        
        // If not successful, fall back to mock data
        console.warn("Failed to fetch tags from API, using mock data")
        return mockTags
      } catch (error) {
        console.error("Error fetching tags:", error)
        return mockTags
      }
    },
  })
}

