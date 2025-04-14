"use client"

import { useQuery } from "@tanstack/react-query"
import { generateMockHistoryEntries } from "@/lib/mock-history-data"

/**
 * Custom hook for fetching document history
 * In a real application, this would make an API call to fetch history entries
 */
export function useDocumentHistory(documentId: string) {
  return useQuery({
    queryKey: ["document-history", documentId],
    queryFn: async () => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Generate mock history entries for the document
      const historyEntries = generateMockHistoryEntries(documentId)

      // Sort by timestamp (newest first)
      return historyEntries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    },
  })
}
