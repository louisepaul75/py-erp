"use client"

import { useQuery } from "@tanstack/react-query"
import type { WarehouseLocation } from "@/types/mold/warehouse-location"

/**
 * Mock data for warehouse locations
 */
const mockWarehouseLocations: WarehouseLocation[] = [
  {
    id: "1",
    laNumber: "LA001",
    location: "1",
    description: "Main warehouse area 1",
  },
  {
    id: "2",
    laNumber: "LA002",
    location: "2",
    description: "Main warehouse area 2",
  },
  {
    id: "3",
    laNumber: "LA003",
    location: "4",
    description: "External warehouse",
  },
  {
    id: "4",
    laNumber: "LA004",
    location: "1",
    description: "Production warehouse",
  },
  {
    id: "5",
    laNumber: "LA005",
    location: "2",
    description: "Quality assurance",
  },
  {
    id: "6",
    laNumber: "LA006",
    location: "4",
    description: "Shipping warehouse",
  },
]

/**
 * Hook for managing warehouse locations
 */
export function useWarehouseLocations() {
  /**
   * Function to fetch all warehouse locations
   */
  const fetchWarehouseLocations = async (): Promise<WarehouseLocation[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockWarehouseLocations
  }

  /**
   * Query for fetching warehouse locations
   */
  const query = useQuery({
    queryKey: ["warehouseLocations"],
    queryFn: fetchWarehouseLocations,
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
  }
}

