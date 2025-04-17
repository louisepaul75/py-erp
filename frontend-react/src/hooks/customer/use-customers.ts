"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchCustomersAPI } from "@/lib/api" // Assuming fetchCustomersAPI is exported from lib/api
import type { Customer } from "@/types/document/document" // Assuming Customer type is here

/**
 * Custom hook for fetching customers
 * Fetches customers from the backend API
 */
export function useCustomers() {
  return useQuery<{ results: Customer[] }, Error>({ 
    queryKey: ["customers"],
    queryFn: async () => {
      try {
        // Fetch data from the API endpoint
        // fetchCustomersAPI now returns Promise<Customer[]>
        const customers = await fetchCustomersAPI(); 
        
        // Wrap the array in the structure expected by useQuery
        return { results: customers || [] }; 

      } catch (error) {
        console.error("Error fetching customers:", error)
        // Re-throw error for React Query error handling
        throw new Error("Failed to fetch customers"); 
      }
    },
  })
} 