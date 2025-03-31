"use client"

import { useQuery } from "@tanstack/react-query"
import axios from "axios"
import { API_URL as BASE_URL } from "@/lib/config"
import { clientCookieStorage } from "@/lib/auth/clientCookies"
import { AUTH_CONFIG } from "@/lib/config"

/**
 * API URL for mold tags
 */
const API_URL = `${BASE_URL}/production/molds/tags/`

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
          console.log("Successfully fetched tags from API", response.data)
          
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
            } else if (Array.isArray(response.data.tags)) {
              return response.data.tags;
            } else {
              // If no recognized array structure, log and fall back to mock data
              console.warn("API response doesn't contain an array of tags:", response.data);
            }
          }
        }
        
        // If not successful or unrecognized structure, fall back to mock data
        console.warn("Failed to fetch tags from API, using mock data")
        return mockTags
      } catch (error) {
        console.error("Error fetching tags:", error)
        return mockTags
      }
    },
  })
}

