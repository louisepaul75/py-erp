"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Mold } from "@/types/mold/mold"
import { MoldActivityStatus } from "@/types/mold/mold"
import { generateMoldNumber } from "@/lib/mold/utils"
import { ArticleStatus } from "@/types/mold/article"
import { mockArticles } from "@/hooks/mold/use-articles"
import { useActivityLog } from "@/hooks/mold/use-activity-log"
import { ActivityType, EntityType } from "@/types/mold/activity-log"
import axios from "axios"

/**
 * Mock API functions for molds
 * Kept as a fallback in case the real API is not available
 */
const mockMolds: Mold[] = [
  {
    id: "1",
    legacyMoldNumber: "M-123",
    moldNumber: "F10001",
    technology: "Die Casting",
    alloy: "Aluminum",
    warehouseLocation: "Warehouse A",
    numberOfArticles: 5,
    isActive: true,
    activityStatus: MoldActivityStatus.ACTIVE, // Dies wird später überschrieben
    tags: ["High Priority", "New Design"],
    createdDate: new Date("2023-01-15").toISOString(),
  },
  {
    id: "2",
    legacyMoldNumber: "M-456",
    moldNumber: "F10002",
    technology: "Injection Molding",
    alloy: "Steel",
    warehouseLocation: "Warehouse B",
    numberOfArticles: 3,
    isActive: false,
    activityStatus: MoldActivityStatus.INACTIVE,
    tags: ["Maintenance Required"],
    createdDate: new Date("2023-02-20").toISOString(),
  },
  {
    id: "3",
    legacyMoldNumber: "M-789",
    moldNumber: "F10003",
    technology: "Sand Casting",
    alloy: "Brass",
    warehouseLocation: "Warehouse A",
    numberOfArticles: 8,
    isActive: true,
    activityStatus: MoldActivityStatus.ACTIVE,
    tags: ["Prototype"],
    createdDate: new Date("2023-03-10").toISOString(),
  },
]

/**
 * Determines the mold activity status based on its articles
 */
function determineMoldActivityStatus(articles: any[] | undefined): MoldActivityStatus {
  if (!articles || articles.length === 0) {
    return MoldActivityStatus.INACTIVE
  }

  const activeCount = articles.filter(
    (a) => a.status === ArticleStatus.ACTIVE || a.status === ArticleStatus.MIXED,
  ).length

  if (activeCount === 0) {
    return MoldActivityStatus.INACTIVE
  } else if (activeCount === articles.length) {
    // Prüfen, ob alle Artikel vollständig aktiv sind
    const fullyActiveCount = articles.filter((a) => a.status === ArticleStatus.ACTIVE).length
    if (fullyActiveCount === articles.length) {
      return MoldActivityStatus.ACTIVE
    } else {
      return MoldActivityStatus.MIXED
    }
  } else {
    return MoldActivityStatus.MIXED
  }
}

/**
 * API URL for molds
 */
const API_URL = "/api/production/molds/"

/**
 * Custom hook for managing molds data
 */
export function useMolds() {
  const queryClient = useQueryClient()
  const { createActivityLog } = useActivityLog()

  /**
   * Fetch all molds from the API or use mock data as fallback
   */
  const fetchMolds = async (): Promise<Mold[]> => {
    try {
      // Attempt to fetch from the real API
      const response = await axios.get(API_URL)
      
      // If successful, use the API data
      if (response.status === 200) {
        console.log("Successfully fetched molds from API", response.data)
        return response.data
      }
      
      // If not successful, fall back to mock data
      console.warn("Failed to fetch molds from API, using mock data")
      
      // Use mock data as fallback
      for (const mold of mockMolds) {
        const moldArticles = mockArticles.filter((article) => article.moldId === mold.id)
        const status = determineMoldActivityStatus(moldArticles)
        mold.activityStatus = status
        mold.isActive = status !== MoldActivityStatus.INACTIVE
        mold.numberOfArticles = moldArticles.length
      }
      return mockMolds
    } catch (error) {
      console.error("Error fetching molds:", error)
      
      // Use mock data as fallback
      for (const mold of mockMolds) {
        const moldArticles = mockArticles.filter((article) => article.moldId === mold.id)
        const status = determineMoldActivityStatus(moldArticles)
        mold.activityStatus = status
        mold.isActive = status !== MoldActivityStatus.INACTIVE
        mold.numberOfArticles = moldArticles.length
      }
      return mockMolds
    }
  }

  /**
   * Create a new mold
   */
  const createMoldFn = async (mold: Omit<Mold, "id" | "createdDate">): Promise<Mold> => {
    try {
      // Attempt to create via the API
      const response = await axios.post(API_URL, mold)
      
      // If successful, return the created mold
      if (response.status === 201) {
        console.log("Successfully created mold via API", response.data)
        
        // Log the activity
        await createActivityLog({
          activityType: ActivityType.CREATE,
          entityType: EntityType.MOLD,
          entityId: response.data.id,
          entityName: response.data.moldNumber,
          details: `Created new mold ${response.data.moldNumber}`,
        })
        
        return response.data
      }
      
      // Fall back to mock implementation
      console.warn("Failed to create mold via API, using mock implementation")
    } catch (error) {
      console.error("Error creating mold:", error)
      // Fall back to mock implementation
    }
    
    // Mock implementation as fallback
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Generate a new ID and created date
    const newMold: Mold = {
      ...mold,
      id: Math.random().toString(36).substring(2, 9),
      createdDate: new Date().toISOString(),
      activityStatus: mold.isActive ? MoldActivityStatus.ACTIVE : MoldActivityStatus.INACTIVE,
    }

    // Add to mock data
    mockMolds.push(newMold)

    // Log the activity
    await createActivityLog({
      activityType: ActivityType.CREATE,
      entityType: EntityType.MOLD,
      entityId: newMold.id,
      entityName: newMold.moldNumber,
      details: `Created new mold ${newMold.moldNumber}`,
    })

    return newMold
  }

  /**
   * Update an existing mold
   */
  const updateMoldFn = async (mold: Mold): Promise<Mold> => {
    try {
      // Attempt to update via the API
      const response = await axios.put(`${API_URL}${mold.id}/`, mold)
      
      // If successful, return the updated mold
      if (response.status === 200) {
        console.log("Successfully updated mold via API", response.data)
        
        // Log the activity
        await createActivityLog({
          activityType: ActivityType.UPDATE,
          entityType: EntityType.MOLD,
          entityId: response.data.id,
          entityName: response.data.moldNumber,
          details: `Updated mold ${response.data.moldNumber}`,
        })
        
        return response.data
      }
      
      // Fall back to mock implementation
      console.warn("Failed to update mold via API, using mock implementation")
    } catch (error) {
      console.error("Error updating mold:", error)
      // Fall back to mock implementation
    }
    
    // Mock implementation as fallback
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and update the mold
    const index = mockMolds.findIndex((m) => m.id === mold.id)
    if (index === -1) {
      throw new Error("Mold not found")
    }

    // Get the old mold for comparison
    const oldMold = { ...mockMolds[index] }

    // Track changes for activity log
    const changes = []

    // Check for changes in fields
    if (oldMold.legacyMoldNumber !== mold.legacyMoldNumber) {
      changes.push({
        field: "legacyMoldNumber",
        oldValue: oldMold.legacyMoldNumber,
        newValue: mold.legacyMoldNumber,
      })
    }

    if (oldMold.technology !== mold.technology) {
      changes.push({
        field: "technology",
        oldValue: oldMold.technology,
        newValue: mold.technology,
      })
    }

    if (oldMold.alloy !== mold.alloy) {
      changes.push({
        field: "alloy",
        oldValue: oldMold.alloy,
        newValue: mold.alloy,
      })
    }

    if (oldMold.warehouseLocation !== mold.warehouseLocation) {
      changes.push({
        field: "warehouseLocation",
        oldValue: oldMold.warehouseLocation,
        newValue: mold.warehouseLocation,
      })
    }

    if (oldMold.moldSize !== mold.moldSize) {
      changes.push({
        field: "moldSize",
        oldValue: oldMold.moldSize || "None",
        newValue: mold.moldSize || "None",
      })
    }

    // Check for changes in tags
    const oldTags = oldMold.tags || []
    const newTags = mold.tags || []
    if (JSON.stringify(oldTags) !== JSON.stringify(newTags)) {
      changes.push({
        field: "tags",
        oldValue: oldTags.join(", "),
        newValue: newTags.join(", "),
      })
    }

    // Wenn der Benutzer den Status manuell ändert
    if (mold.isActive !== oldMold.isActive) {
      changes.push({
        field: "isActive",
        oldValue: oldMold.isActive ? "Active" : "Inactive",
        newValue: mold.isActive ? "Active" : "Inactive",
      })

      // Aktualisiere den activityStatus basierend auf isActive
      mold.activityStatus = mold.isActive ? MoldActivityStatus.ACTIVE : MoldActivityStatus.INACTIVE

      // Wenn Artikel vorhanden sind
      const moldArticles = mockArticles.filter((article) => article.moldId === mold.id)
      if (moldArticles.length > 0) {
        // Aktualisiere den Status aller Artikel basierend auf dem neuen Mold-Status
        for (const article of moldArticles) {
          // Finde den Index des Artikels in der mockArticles-Liste
          const articleIndex = mockArticles.findIndex((a) => a.id === article.id)
          if (articleIndex !== -1) {
            // Log article status change
            await createActivityLog({
              activityType: ActivityType.UPDATE,
              entityType: EntityType.ARTICLE,
              entityId: article.id,
              entityName: article.newArticleNumber,
              details: `Updated article ${article.newArticleNumber} status due to mold ${mold.moldNumber} status change`,
              changes: [
                {
                  field: "status",
                  oldValue: mockArticles[articleIndex].status,
                  newValue: mold.isActive ? ArticleStatus.ACTIVE : ArticleStatus.INACTIVE,
                },
              ],
            })

            if (mold.isActive) {
              // Wenn die Form aktiv wird, setze alle Artikel auf aktiv
              mockArticles[articleIndex].status = ArticleStatus.ACTIVE
              if (mockArticles[articleIndex].instances) {
                mockArticles[articleIndex].instances = mockArticles[articleIndex].instances?.map((instance) => ({
                  ...instance,
                  isActive: true,
                }))
              }
            } else {
              // Wenn die Form inaktiv wird, setze alle Artikel auf inaktiv
              mockArticles[articleIndex].status = ArticleStatus.INACTIVE
              if (mockArticles[articleIndex].instances) {
                mockArticles[articleIndex].instances = mockArticles[articleIndex].instances?.map((instance) => ({
                  ...instance,
                  isActive: false,
                }))
              }
            }
          }
        }

        // Invalidiere den Artikel-Cache
        queryClient.invalidateQueries({ queryKey: ["articles"] })
      }
    } else {
      // Wenn der Status nicht manuell geändert wurde, berechne ihn basierend auf den Artikeln
      const moldArticles = mockArticles.filter((article) => article.moldId === mold.id)
      mold.activityStatus = determineMoldActivityStatus(moldArticles)
      mold.isActive = mold.activityStatus !== MoldActivityStatus.INACTIVE

      // Aktualisiere die Anzahl der Artikel
      mold.numberOfArticles = moldArticles.length
    }

    mockMolds[index] = mold

    // Log the activity if there were changes
    if (changes.length > 0) {
      await createActivityLog({
        activityType: ActivityType.UPDATE,
        entityType: EntityType.MOLD,
        entityId: mold.id,
        entityName: mold.moldNumber,
        details: `Updated mold ${mold.moldNumber}`,
        changes,
      })
    }

    return mold
  }

  /**
   * Duplicate a mold with a new mold number
   */
  const duplicateMoldFn = async (mold: Mold | Omit<Mold, "id" | "createdDate">): Promise<Mold> => {
    try {
      // For duplicating, we'll just do a POST to create a new mold
      // but we'll modify the data to indicate it's a duplicate
      const moldData = {
        ...(mold as Mold),
        legacyMoldNumber: `Copy of ${(mold as Mold).legacyMoldNumber}`,
        moldNumber: generateMoldNumber(),
      }
      
      // Remove the ID so it creates a new one
      delete (moldData as any).id
      delete (moldData as any).createdDate
      
      const response = await axios.post(API_URL, moldData)
      
      // If successful, return the duplicated mold
      if (response.status === 201) {
        console.log("Successfully duplicated mold via API", response.data)
        
        // Log the activity
        await createActivityLog({
          activityType: ActivityType.CREATE,
          entityType: EntityType.MOLD,
          entityId: response.data.id,
          entityName: response.data.moldNumber,
          details: `Duplicated mold ${(mold as Mold).moldNumber} to create ${response.data.moldNumber}`,
        })
        
        return response.data
      }
      
      // Fall back to mock implementation
      console.warn("Failed to duplicate mold via API, using mock implementation")
    } catch (error) {
      console.error("Error duplicating mold:", error)
      // Fall back to mock implementation
    }
    
    // Mock implementation as fallback
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Generate a new mold number
    const newMoldNumber = generateMoldNumber()

    // Create a new mold with the same properties but a new ID, mold number, and created date
    const newMold: Mold = {
      ...(mold as Mold),
      id: Math.random().toString(36).substring(2, 9),
      moldNumber: newMoldNumber,
      createdDate: new Date().toISOString(),
      activityStatus: (mold as Mold).activityStatus || MoldActivityStatus.INACTIVE,
    }

    // Add to mock data
    mockMolds.push(newMold)

    // Log the activity
    await createActivityLog({
      activityType: ActivityType.CREATE,
      entityType: EntityType.MOLD,
      entityId: newMold.id,
      entityName: newMold.moldNumber,
      details: `Duplicated mold ${(mold as Mold).moldNumber} to create ${newMold.moldNumber}`,
    })

    return newMold
  }

  /**
   * Delete a mold
   */
  const deleteMoldFn = async (id: string): Promise<void> => {
    try {
      // Attempt to delete via the API
      const response = await axios.delete(`${API_URL}${id}/`)
      
      // If successful, log the activity
      if (response.status === 204) {
        console.log("Successfully deleted mold via API")
        
        // Since we don't have the mold data anymore after deletion,
        // we'll need to find it in our cache
        const cachedMolds = queryClient.getQueryData<Mold[]>(["molds"])
        const deletedMold = cachedMolds?.find(m => m.id === id)
        
        if (deletedMold) {
          // Log the activity
          await createActivityLog({
            activityType: ActivityType.DELETE,
            entityType: EntityType.MOLD,
            entityId: id,
            entityName: deletedMold.moldNumber,
            details: `Deleted mold ${deletedMold.moldNumber}`,
          })
        }
        
        return
      }
      
      // Fall back to mock implementation
      console.warn("Failed to delete mold via API, using mock implementation")
    } catch (error) {
      console.error("Error deleting mold:", error)
      // Fall back to mock implementation
    }
    
    // Mock implementation as fallback
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and remove the mold
    const index = mockMolds.findIndex((m) => m.id === id)
    if (index === -1) {
      throw new Error("Mold not found")
    }

    const deletedMold = mockMolds[index]
    mockMolds.splice(index, 1)

    // Log the activity
    await createActivityLog({
      activityType: ActivityType.DELETE,
      entityType: EntityType.MOLD,
      entityId: id,
      entityName: deletedMold.moldNumber,
      details: `Deleted mold ${deletedMold.moldNumber}`,
    })
  }

  /**
   * Query for fetching molds
   */
  const query = useQuery({
    queryKey: ["molds"],
    queryFn: fetchMolds,
    // Wichtig: Stellen Sie sicher, dass die Daten immer aktualisiert werden
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    staleTime: 0, // Daten immer als veraltet betrachten
  })

  /**
   * Mutation for creating a mold
   */
  const createMutation = useMutation({
    mutationFn: createMoldFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for updating a mold
   */
  const updateMutation = useMutation({
    mutationFn: updateMoldFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for duplicating a mold
   */
  const duplicateMutation = useMutation({
    mutationFn: duplicateMoldFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for deleting a mold
   */
  const deleteMutation = useMutation({
    mutationFn: deleteMoldFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    createMold: createMutation.mutateAsync,
    updateMold: updateMutation.mutateAsync,
    duplicateMold: duplicateMutation.mutateAsync,
    deleteMold: deleteMutation.mutateAsync,
  }
}

export { mockMolds }

