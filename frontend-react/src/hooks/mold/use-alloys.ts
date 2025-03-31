"use client"

import { useQuery } from "@tanstack/react-query"
import axios from "axios"

/**
 * API URL for mold alloys
 */
const API_URL = "/api/production/molds/alloys/"

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
        // Attempt to fetch from the real API
        const response = await axios.get(API_URL)
        
        // If successful, use the API data
        if (response.status === 200) {
          console.log("Successfully fetched alloys from API", response.data)
          return response.data
        }
        
        // If not successful, fall back to mock data
        console.warn("Failed to fetch alloys from API, using mock data")
        return mockAlloys
      } catch (error) {
        console.error("Error fetching alloys:", error)
        if (error.response) {
          console.error("Error response data:", error.response.data)
          console.error("Error response status:", error.response.status)
          console.error("Error response headers:", error.response.headers)
        } else if (error.request) {
          console.error("Error request:", error.request)
        } else {
          console.error("Error message:", error.message)
        }
        return mockAlloys
      }
    },
  })
}

