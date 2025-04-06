"use client"

import { useQuery } from "@tanstack/react-query"
import { instance } from "@/lib/api"
import { API_URL as BASE_URL } from "@/lib/config"

/**
 * API URL for mold tags
 */
const API_URL = `/production/molds/tags/`

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
        // Attempt to fetch from the real API using the shared ky instance
        const response = await instance.get(API_URL).json()
        
        // If successful, use the API data
        console.log("Successfully fetched tags from API", response)
        
        // Check the structure of the API response
        if (Array.isArray(response)) {
          return response;
        } else if (response && typeof response === 'object') {
          // Check if response has a results, data, or items property that is an array
          if (Array.isArray(response.results)) {
            return response.results;
          } else if (Array.isArray(response.data)) {
            return response.data;
          } else if (Array.isArray(response.items)) {
            return response.items;
          } else if (Array.isArray(response.tags)) {
            return response.tags;
          } else {
            // If no recognized array structure, log and fall back to mock data
            console.warn("API response doesn't contain an array of tags:", response);
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

