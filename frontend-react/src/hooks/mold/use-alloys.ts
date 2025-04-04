"use client"

import { useQuery } from "@tanstack/react-query"
import { instance } from "@/lib/api"
import { API_URL as BASE_URL } from "@/lib/config"

/**
 * API URL for mold alloys
 */
const API_URL = '/api/production/molds/alloys/'

/**
 * Mock data for alloys, used as fallback
 */
const mockAlloys = [
  "Aluminum",
  "Steel",
  "Brass",
  "Bronze",
  "Zinc",
  "Magnesium"
]

/**
 * Hook to fetch mold alloys
 */
export function useAlloys() {
  return useQuery({
    queryKey: ["alloys"],
    queryFn: async () => {
      try {
        // Attempt to fetch from the real API using the shared ky instance
        const response = await instance.get(API_URL).json()
        
        // If successful, use the API data
        console.log("Successfully fetched alloys from API", response)
        
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
          } else if (Array.isArray(response.alloys)) {
            return response.alloys;
          } else {
            // If no recognized array structure, log and fall back to mock data
            console.warn("API response doesn't contain an array of alloys:", response);
          }
        }
        
        // If not successful or unrecognized structure, fall back to mock data
        console.warn("Failed to fetch alloys from API, using mock data")
        return mockAlloys
      } catch (error) {
        console.error("Error fetching alloys:", error)
        if (error.response) {
          console.error("Error response data:", await error.response.text())
          console.error("Error response status:", error.response.status)
        }
        return mockAlloys
      }
    },
  })
}

