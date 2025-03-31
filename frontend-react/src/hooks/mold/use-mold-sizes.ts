"use client"

import { useQuery } from "@tanstack/react-query"
import axios from "axios"
import type { MoldSize } from "@/types/mold/mold-size"

/**
 * API URL for mold sizes
 */
const API_URL = "/api/production/molds/mold_sizes/"

/**
 * Mock data for mold sizes, used as fallback
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
 * Hook to fetch mold sizes
 */
export function useMoldSizes() {
  return useQuery({
    queryKey: ["moldSizes"],
    queryFn: async () => {
      try {
        // Attempt to fetch from the real API
        const response = await axios.get(API_URL)
        
        // If successful, use the API data
        if (response.status === 200) {
          console.log("Successfully fetched mold sizes from API", response.data)
          return response.data
        }
        
        // If not successful, fall back to mock data
        console.warn("Failed to fetch mold sizes from API, using mock data")
        return mockMoldSizes
      } catch (error) {
        console.error("Error fetching mold sizes:", error)
        return mockMoldSizes
      }
    },
  })
}

