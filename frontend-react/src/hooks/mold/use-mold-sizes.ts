"use client"

import { useQuery } from "@tanstack/react-query"
import axios from "axios"
import type { MoldSize } from "@/types/mold/mold-size"
import { API_URL as BASE_URL } from "@/lib/config"
import { clientCookieStorage } from "@/lib/auth/clientCookies"
import { AUTH_CONFIG } from "@/lib/config"

/**
 * API URL for mold sizes
 */
const API_URL = `${BASE_URL}/production/molds/mold_sizes/`

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
          console.log("Successfully fetched mold sizes from API", response.data)
          
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
            } else if (Array.isArray(response.data.moldSizes)) {
              return response.data.moldSizes;
            } else if (Array.isArray(response.data.mold_sizes)) {
              return response.data.mold_sizes;
            } else {
              // If no recognized array structure, log and fall back to mock data
              console.warn("API response doesn't contain an array of mold sizes:", response.data);
            }
          }
        }
        
        // If not successful or unrecognized structure, fall back to mock data
        console.warn("Failed to fetch mold sizes from API, using mock data")
        return mockMoldSizes
      } catch (error) {
        console.error("Error fetching mold sizes:", error)
        return mockMoldSizes
      }
    },
  })
}

