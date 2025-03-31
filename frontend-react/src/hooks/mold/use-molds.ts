"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Mold } from "@/types/mold/mold"
import { MoldActivityStatus } from "@/types/mold/mold"
import { generateMoldNumber } from "@/lib/mold/utils"
import { ArticleStatus } from "@/types/mold/article"
import { mockArticles } from "@/hooks/mold/use-articles"
import { useActivityLog } from "@/hooks/mold/use-activity-log"
import { ActivityType, EntityType } from "@/types/mold/activity-log"

/**
 * Mock API functions for molds
 * In a real application, these would be replaced with actual API calls
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
 * Custom hook for managing molds data
 */
export function useMolds() {
  const queryClient = useQueryClient()
  const { createActivityLog } = useActivityLog()

  /**
   * Fetch all molds
   */
  const fetchMolds = async (): Promise<Mold[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Direkt die mockArticles verwenden, um den Status zu berechnen
    for (const mold of mockMolds) {
      const moldArticles = mockArticles.filter((article) => article.moldId === mold.id)

      // Berechne den Status für jede Form basierend auf ihren Artikeln
      const status = determineMoldActivityStatus(moldArticles)

      // Wichtig: Immer den Status aktualisieren
      mold.activityStatus = status
      mold.isActive = status !== MoldActivityStatus.INACTIVE

      // Berechne die Anzahl der unterschiedlichen Artikel (unabhängig von Instanzen)
      mold.numberOfArticles = moldArticles.length
    }

    return mockMolds
  }

  /**
   * Create a new mold
   */
  const createMoldFn = async (mold: Omit<Mold, "id" | "createdDate">): Promise<Mold> => {
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

