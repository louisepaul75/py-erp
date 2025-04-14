"use client"

import { useQuery } from "@tanstack/react-query"
import { mockDocuments, mockRelationships } from "@/lib/mock-data/mock-document-data"
import type { Document } from "@/types/document/document"

/**
 * Interface for the document graph data
 */
interface DocumentGraph {
  documents: (Document & { position: { x: number; y: number } })[]
  relationships: {
    id: string
    sourceId: string
    targetId: string
    type: string
  }[]
}

/**
 * Custom hook for fetching the document graph data
 * In a real application, this would make an API call to fetch the graph data
 */
export function useDocumentGraph() {
  return useQuery<DocumentGraph>({
    queryKey: ["document-graph"],
    queryFn: async () => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Calculate positions for the documents in the graph
      const documents = mockDocuments.map((doc, index) => ({
        ...doc,
        position: calculatePosition(doc, index, mockDocuments.length),
      }))

      // Map relationships to the format expected by the graph
      const relationships = mockRelationships.map((rel) => ({
        id: rel.id,
        sourceId: rel.sourceId,
        targetId: rel.targetId,
        type: rel.relationType,
      }))

      return { documents, relationships }
    },
  })
}

/**
 * Calculate a position for a document in the graph
 * This is a simple algorithm that places documents in a circle
 */
function calculatePosition(document: Document, index: number, totalDocuments: number): { x: number; y: number } {
  // Place documents in a circle
  const radius = 300
  const angle = (index / totalDocuments) * 2 * Math.PI

  // Calculate x and y coordinates
  const x = radius * Math.cos(angle)
  const y = radius * Math.sin(angle)

  return { x, y }
}
