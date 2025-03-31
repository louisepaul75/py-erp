"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Article, ArticleInstance } from "@/types/mold/article"
import { ArticleStatus } from "@/types/mold/article"
import { useActivityLog } from "@/hooks/mold/use-activity-log"
import { ActivityType, EntityType } from "@/types/mold/activity-log"

/**
 * Mock API functions for articles
 * In a real application, these would be replaced with actual API calls
 */
const mockArticles: Article[] = [
  {
    id: "1",
    oldArticleNumber: "A-123",
    newArticleNumber: "N-456",
    description: "Porcelain figurine - Dog",
    frequency: 4,
    status: ArticleStatus.ACTIVE, // Wird später überschrieben
    moldId: "1",
    instances: [
      { id: "1-1", position: 1, isActive: true },
      { id: "1-2", position: 2, isActive: true },
      { id: "1-3", position: 3, isActive: true },
      { id: "1-4", position: 4, isActive: true },
    ],
  },
  {
    id: "2",
    oldArticleNumber: "A-124",
    newArticleNumber: "N-457",
    description: "Porcelain figurine - Cat",
    frequency: 2,
    status: ArticleStatus.INACTIVE, // Wird später überschrieben
    moldId: "1",
    instances: [
      { id: "2-1", position: 1, isActive: false },
      { id: "2-2", position: 2, isActive: false },
    ],
  },
  // Füge einen dritten Artikel für Mold 1 hinzu
  {
    id: "4",
    oldArticleNumber: "A-126",
    newArticleNumber: "N-459",
    description: "Porcelain figurine - Rabbit",
    frequency: 3,
    status: ArticleStatus.ACTIVE,
    moldId: "1",
    instances: [
      { id: "4-1", position: 1, isActive: true },
      { id: "4-2", position: 2, isActive: true },
      { id: "4-3", position: 3, isActive: true },
    ],
  },
  {
    id: "3",
    oldArticleNumber: "A-125",
    newArticleNumber: "N-458",
    description: "Porcelain figurine - Bird",
    frequency: 6,
    status: ArticleStatus.DISCONTINUED, // Wird später überschrieben
    moldId: "2",
    instances: [
      { id: "3-1", position: 1, isActive: false },
      { id: "3-2", position: 2, isActive: false },
      { id: "3-3", position: 3, isActive: false },
      { id: "3-4", position: 4, isActive: false },
      { id: "3-5", position: 5, isActive: false },
      { id: "3-6", position: 6, isActive: false },
    ],
  },
]

// Initialisiere die Status der Artikel basierend auf ihren Instanzen
for (const article of mockArticles) {
  if (article.instances) {
    const activeCount = article.instances.filter((i) => i.isActive).length
    if (activeCount === 0) {
      article.status = ArticleStatus.INACTIVE
    } else if (activeCount === article.instances.length) {
      article.status = ArticleStatus.ACTIVE
    } else {
      article.status = ArticleStatus.MIXED
    }
  }
}

export { mockArticles }

/**
 * Determines the article status based on its instances
 */
function determineArticleStatus(instances: ArticleInstance[] | undefined): ArticleStatus {
  if (!instances || instances.length === 0) {
    return ArticleStatus.INACTIVE
  }

  const activeCount = instances.filter((i) => i.isActive).length

  if (activeCount === 0) {
    return ArticleStatus.INACTIVE
  } else if (activeCount === instances.length) {
    return ArticleStatus.ACTIVE
  } else {
    return ArticleStatus.MIXED
  }
}

/**
 * Updates all instances based on the article status
 */
function updateInstancesBasedOnStatus(
  instances: ArticleInstance[] | undefined,
  status: ArticleStatus,
): ArticleInstance[] {
  if (!instances) return []

  return instances.map((instance) => ({
    ...instance,
    isActive: status === ArticleStatus.ACTIVE,
  }))
}

/**
 * Custom hook for managing articles data
 */
export function useArticles(moldId?: string) {
  const queryClient = useQueryClient()
  const { createActivityLog } = useActivityLog()

  /**
   * Fetch all articles for a specific mold or all articles if no moldId is provided
   */
  const fetchArticles = async (): Promise<Article[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Aktualisiere den Status aller Artikel basierend auf ihren Instanzen
    for (const article of mockArticles) {
      article.status = determineArticleStatus(article.instances)
    }

    // If moldId is provided, filter articles by moldId
    if (moldId) {
      return mockArticles.filter((article) => article.moldId === moldId)
    }

    return mockArticles
  }

  /**
   * Create a new article
   */
  const createArticleFn = async (article: Omit<Article, "id" | "instances">): Promise<Article> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Generate a new ID
    const newId = Math.random().toString(36).substring(2, 9)

    // Create instances based on frequency
    const instances: ArticleInstance[] = Array.from({ length: article.frequency }).map((_, index) => ({
      id: `${newId}-${index + 1}`,
      position: index + 1,
      isActive: article.status === ArticleStatus.ACTIVE,
    }))

    // Add to mock data
    const newArticle: Article = {
      ...article,
      id: newId,
      instances,
    }

    mockArticles.push(newArticle)

    // Log the activity
    await createActivityLog({
      activityType: ActivityType.CREATE,
      entityType: EntityType.ARTICLE,
      entityId: newArticle.id,
      entityName: newArticle.newArticleNumber,
      details: `Created new article ${newArticle.newArticleNumber} for mold ${article.moldId}`,
    })

    return newArticle
  }

  /**
   * Update an existing article
   */
  const updateArticleFn = async (article: Article): Promise<Article> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and update the article
    const index = mockArticles.findIndex((a) => a.id === article.id)
    if (index === -1) {
      throw new Error("Article not found")
    }

    // Get the old article for comparison
    const oldArticle = { ...mockArticles[index] }

    // Track changes for activity log
    const changes = []

    // Check for changes in fields
    if (oldArticle.oldArticleNumber !== article.oldArticleNumber) {
      changes.push({
        field: "oldArticleNumber",
        oldValue: oldArticle.oldArticleNumber,
        newValue: article.oldArticleNumber,
      })
    }

    if (oldArticle.newArticleNumber !== article.newArticleNumber) {
      changes.push({
        field: "newArticleNumber",
        oldValue: oldArticle.newArticleNumber,
        newValue: article.newArticleNumber,
      })
    }

    if (oldArticle.description !== article.description) {
      changes.push({
        field: "description",
        oldValue: oldArticle.description,
        newValue: article.description,
      })
    }

    if (oldArticle.frequency !== article.frequency) {
      changes.push({
        field: "frequency",
        oldValue: oldArticle.frequency,
        newValue: article.frequency,
      })
    }

    if (oldArticle.status !== article.status) {
      changes.push({
        field: "status",
        oldValue: oldArticle.status,
        newValue: article.status,
      })
    }

    // If frequency changed, update instances
    if (article.frequency !== oldArticle.frequency) {
      // If frequency increased, add new instances
      if (article.frequency > oldArticle.frequency) {
        const newInstances: ArticleInstance[] = Array.from({
          length: article.frequency - oldArticle.frequency,
        }).map((_, index) => ({
          id: `${article.id}-${oldArticle.frequency + index + 1}`,
          position: oldArticle.frequency + index + 1,
          isActive: article.status === ArticleStatus.ACTIVE,
        }))

        article.instances = [...(oldArticle.instances || []), ...newInstances]

        // Log instance creation
        for (const instance of newInstances) {
          await createActivityLog({
            activityType: ActivityType.CREATE,
            entityType: EntityType.ARTICLE_INSTANCE,
            entityId: instance.id,
            entityName: `${article.newArticleNumber} Position ${instance.position}`,
            details: `Added new instance at position ${instance.position} for article ${article.newArticleNumber}`,
          })
        }
      }
      // If frequency decreased, remove excess instances
      else if (article.frequency < oldArticle.frequency) {
        const removedInstances = oldArticle.instances?.slice(article.frequency)
        article.instances = oldArticle.instances?.slice(0, article.frequency)

        // Log instance deletion
        if (removedInstances) {
          for (const instance of removedInstances) {
            await createActivityLog({
              activityType: ActivityType.DELETE,
              entityType: EntityType.ARTICLE_INSTANCE,
              entityId: instance.id,
              entityName: `${article.newArticleNumber} Position ${instance.position}`,
              details: `Removed instance at position ${instance.position} from article ${article.newArticleNumber}`,
            })
          }
        }
      }
    }

    // If status changed, update all instance statuses
    if (article.status !== oldArticle.status) {
      // Update all instances based on the new status
      if (article.status === ArticleStatus.ACTIVE) {
        // If active, all instances should be active
        article.instances = updateInstancesBasedOnStatus(oldArticle.instances, ArticleStatus.ACTIVE)
      } else if (article.status === ArticleStatus.INACTIVE || article.status === ArticleStatus.DISCONTINUED) {
        // If inactive or discontinued, all instances should be inactive
        article.instances = updateInstancesBasedOnStatus(oldArticle.instances, ArticleStatus.INACTIVE)
      }
    } else if (!article.instances) {
      // If instances not provided but status didn't change, keep old instances
      article.instances = oldArticle.instances
    }

    mockArticles[index] = article

    // Log the activity if there were changes
    if (changes.length > 0) {
      await createActivityLog({
        activityType: ActivityType.UPDATE,
        entityType: EntityType.ARTICLE,
        entityId: article.id,
        entityName: article.newArticleNumber,
        details: `Updated article ${article.newArticleNumber}`,
        changes,
      })
    }

    return article
  }

  /**
   * Update a specific instance of an article
   */
  const updateArticleInstanceFn = async ({
    articleId,
    instanceId,
    isActive,
  }: {
    articleId: string
    instanceId: string
    isActive: boolean
  }): Promise<Article> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find the article
    const articleIndex = mockArticles.findIndex((a) => a.id === articleId)
    if (articleIndex === -1) {
      throw new Error("Article not found")
    }

    const article = { ...mockArticles[articleIndex] }

    // Find and update the instance
    if (article.instances) {
      const instanceIndex = article.instances.findIndex((i) => i.id === instanceId)
      if (instanceIndex === -1) {
        throw new Error("Instance not found")
      }

      const oldInstance = article.instances[instanceIndex]

      // Update the instance
      article.instances = [...article.instances]
      article.instances[instanceIndex] = {
        ...article.instances[instanceIndex],
        isActive,
      }

      // Update the article status based on instances
      article.status = determineArticleStatus(article.instances)

      mockArticles[articleIndex] = article

      // Log the activity
      await createActivityLog({
        activityType: ActivityType.UPDATE,
        entityType: EntityType.ARTICLE_INSTANCE,
        entityId: instanceId,
        entityName: `${article.newArticleNumber} Position ${oldInstance.position}`,
        details: `Updated instance status at position ${oldInstance.position} for article ${article.newArticleNumber}`,
        changes: [
          {
            field: "isActive",
            oldValue: oldInstance.isActive ? "Active" : "Inactive",
            newValue: isActive ? "Active" : "Inactive",
          },
        ],
      })
    }

    return article
  }

  /**
   * Update article status and all its instances
   */
  const updateArticleStatusFn = async ({
    articleId,
    status,
  }: {
    articleId: string
    status: ArticleStatus
  }): Promise<Article> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find the article
    const articleIndex = mockArticles.findIndex((a) => a.id === articleId)
    if (articleIndex === -1) {
      throw new Error("Article not found")
    }

    const article = { ...mockArticles[articleIndex] }
    const oldStatus = article.status

    // Update the article status
    article.status = status

    // Update all instances based on the new status
    if (article.instances) {
      if (status === ArticleStatus.ACTIVE) {
        // If active, all instances should be active
        article.instances = article.instances.map((instance) => ({
          ...instance,
          isActive: true,
        }))
      } else if (status === ArticleStatus.INACTIVE || status === ArticleStatus.DISCONTINUED) {
        // If inactive or discontinued, all instances should be inactive
        article.instances = article.instances.map((instance) => ({
          ...instance,
          isActive: false,
        }))
      }
    }

    mockArticles[articleIndex] = article

    // Log the activity
    await createActivityLog({
      activityType: ActivityType.UPDATE,
      entityType: EntityType.ARTICLE,
      entityId: articleId,
      entityName: article.newArticleNumber,
      details: `Updated status for article ${article.newArticleNumber}`,
      changes: [
        {
          field: "status",
          oldValue: oldStatus,
          newValue: status,
        },
      ],
    })

    return article
  }

  /**
   * Delete an article
   */
  const deleteArticleFn = async (id: string): Promise<void> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and remove the article
    const index = mockArticles.findIndex((a) => a.id === id)
    if (index === -1) {
      throw new Error("Article not found")
    }

    const deletedArticle = mockArticles[index]
    mockArticles.splice(index, 1)

    // Log the activity
    await createActivityLog({
      activityType: ActivityType.DELETE,
      entityType: EntityType.ARTICLE,
      entityId: id,
      entityName: deletedArticle.newArticleNumber,
      details: `Deleted article ${deletedArticle.newArticleNumber}`,
    })
  }

  /**
   * Query for fetching articles
   */
  const query = useQuery({
    queryKey: ["articles", moldId],
    queryFn: fetchArticles,
    // Wichtig: Stellen Sie sicher, dass die Daten immer aktualisiert werden
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    staleTime: 0, // Daten immer als veraltet betrachten
  })

  /**
   * Mutation for creating an article
   */
  const createMutation = useMutation({
    mutationFn: createArticleFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] })
      // Auch die Molds invalidieren, da sich der Status geändert haben könnte
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for updating an article
   */
  const updateMutation = useMutation({
    mutationFn: updateArticleFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] })
      // Auch die Molds invalidieren, da sich der Status geändert haben könnte
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for updating an article instance
   */
  const updateInstanceMutation = useMutation({
    mutationFn: updateArticleInstanceFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] })
      // Auch die Molds invalidieren, da sich der Status geändert haben könnte
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for updating article status
   */
  const updateStatusMutation = useMutation({
    mutationFn: updateArticleStatusFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] })
      // Auch die Molds invalidieren, da sich der Status geändert haben könnte
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  /**
   * Mutation for deleting an article
   */
  const deleteMutation = useMutation({
    mutationFn: deleteArticleFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] })
      // Auch die Molds invalidieren, da sich der Status geändert haben könnte
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    createArticle: createMutation.mutateAsync,
    updateArticle: updateMutation.mutateAsync,
    updateArticleInstance: updateInstanceMutation.mutateAsync,
    updateArticleStatus: updateStatusMutation.mutateAsync,
    deleteArticle: deleteMutation.mutateAsync,
  }
}

