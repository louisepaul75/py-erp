"use client"

import { useQuery } from "@tanstack/react-query"
import axios from "axios"
import { API_URL as BASE_URL } from "@/lib/config"
import { clientCookieStorage } from "@/lib/auth/clientCookies"
import { AUTH_CONFIG } from "@/lib/config"

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
          console.log("Successfully fetched alloys from API", response.data)
          
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
            } else if (Array.isArray(response.data.alloys)) {
              return response.data.alloys;
            } else {
              // If no recognized array structure, log and fall back to mock data
              console.warn("API response doesn't contain an array of alloys:", response.data);
            }
          }
        }
        
        // If not successful or unrecognized structure, fall back to mock data
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

