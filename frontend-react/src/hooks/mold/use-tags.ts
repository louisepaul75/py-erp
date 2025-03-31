"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { Tag } from "@/types/mold/tag"
import { useMolds } from "@/hooks/mold/use-molds"
import { mockMolds } from "@/hooks/mold/use-molds"

/**
 * Mock API functions for tags
 * In a real application, these would be replaced with actual API calls
 */
const mockTags: Tag[] = [
  {
    id: "1",
    name: "High Priority",
  },
  {
    id: "2",
    name: "Maintenance Required",
  },
  {
    id: "3",
    name: "New Design",
  },
  {
    id: "4",
    name: "Prototype",
  },
]

/**
 * Custom hook for managing tags data
 */
export function useTags() {
  const queryClient = useQueryClient()
  const { data: molds, updateMold } = useMolds()

  /**
   * Fetch all tags
   */
  const fetchTags = async (): Promise<Tag[]> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))
    return mockTags
  }

  /**
   * Create a new tag
   */
  const createTagFn = async (tag: Omit<Tag, "id">): Promise<Tag> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Generate a new ID
    const newTag: Tag = {
      ...tag,
      id: Math.random().toString(36).substring(2, 9),
    }

    // Add to mock data
    mockTags.push(newTag)

    return newTag
  }

  /**
   * Update an existing tag
   */
  const updateTagFn = async (tag: Tag): Promise<Tag> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and update the tag
    const index = mockTags.findIndex((t) => t.id === tag.id)
    if (index === -1) {
      throw new Error("Tag not found")
    }

    mockTags[index] = tag

    return tag
  }

  /**
   * Delete a tag
   */
  const deleteTagFn = async (id: string): Promise<void> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Find and remove the tag
    const index = mockTags.findIndex((t) => t.id === id)
    if (index === -1) {
      throw new Error("Tag not found")
    }

    // Get the tag name before removing it
    const tagName = mockTags[index].name

    // Remove the tag
    mockTags.splice(index, 1)

    // Update all molds to remove this tag
    if (molds) {
      const updatePromises = []

      for (const mold of molds) {
        if (mold.tags && mold.tags.includes(tagName)) {
          // Erstellen einer neuen Tags-Array ohne den gelöschten Tag
          const updatedTags = mold.tags.filter((t) => t !== tagName)

          // Direkte Aktualisierung des mockMolds-Arrays für sofortige UI-Aktualisierung
          const moldIndex = mockMolds.findIndex((m) => m.id === mold.id)
          if (moldIndex !== -1) {
            mockMolds[moldIndex].tags = updatedTags
          }

          // Aktualisieren des Molds mit den neuen Tags
          updatePromises.push(
            updateMold({
              ...mold,
              tags: updatedTags,
            }),
          )
        }
      }

      // Warten auf alle Updates
      await Promise.all(updatePromises)
    }

    // Explizit den Cache für Molds invalidieren
    queryClient.invalidateQueries({ queryKey: ["molds"] })

    // Erzwingen einer sofortigen Aktualisierung der UI
    setTimeout(() => {
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    }, 100)
  }

  /**
   * Query for fetching tags
   */
  const query = useQuery({
    queryKey: ["tags"],
    queryFn: fetchTags,
  })

  /**
   * Mutation for creating a tag
   */
  const createMutation = useMutation({
    mutationFn: createTagFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tags"] })
    },
  })

  /**
   * Mutation for updating a tag
   */
  const updateMutation = useMutation({
    mutationFn: updateTagFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tags"] })
    },
  })

  /**
   * Mutation for deleting a tag
   */
  const deleteMutation = useMutation({
    mutationFn: deleteTagFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tags"] })
      // Also invalidate molds query since we might have updated molds
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    createTag: createMutation.mutateAsync,
    updateTag: updateMutation.mutateAsync,
    deleteTag: deleteMutation.mutateAsync,
  }
}

