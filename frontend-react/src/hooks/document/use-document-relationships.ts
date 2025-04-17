"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { DocumentRelationship } from "@/types/document/document"
import { mockRelationships } from "@/lib/mock-data/mock-document-data"

/**
 * Custom hook for fetching document relationships
 * In a real application, this would make an API call to fetch relationships
 */
export function useDocumentRelationships(documentId: string) {
  return useQuery({
    queryKey: ["document-relationships", documentId],
    queryFn: async () => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Filter relationships where the document is the source
      return mockRelationships.filter((rel) => rel.sourceId === documentId)
    },
  })
}

/**
 * Custom hook for creating a document relationship
 * In a real application, this would make an API call to create a relationship
 */
export function useCreateRelationship() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (newRelationship: {
      sourceDocumentId: string
      targetDocumentId: string
      relationType: string
    }) => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Get the documents to create the relationship
      const documents = queryClient.getQueryData<any[]>(["documents"]) || []
      const sourceDocument = documents.find((doc) => doc.id === newRelationship.sourceDocumentId)
      const targetDocument = documents.find((doc) => doc.id === newRelationship.targetDocumentId)

      if (!sourceDocument || !targetDocument) {
        throw new Error("Source or target document not found")
      }

      // Generate a new relationship with an ID
      const relationship: DocumentRelationship = {
        id: `rel-${Date.now()}`,
        sourceId: newRelationship.sourceDocumentId,
        targetId: newRelationship.targetDocumentId,
        relationType: newRelationship.relationType,
        relatedDocument: targetDocument,
      }

      return relationship
    },
    onSuccess: (newRelationship) => {
      // Update the relationships query with the new relationship
      queryClient.setQueryData(
        ["document-relationships", newRelationship.sourceId],
        (oldData: DocumentRelationship[] = []) => [...oldData, newRelationship],
      )

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ["document-graph"] })
    },
  })
}
