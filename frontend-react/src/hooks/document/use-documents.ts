"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { Document } from "@/types/document/document"
import { mockDocuments } from "@/lib/mock-data/mock-document-data"

/**
 * Custom hook for fetching documents
 * In a real application, this would make an API call to fetch documents
 */
export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: async () => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 500))
      return mockDocuments
    },
  })
}

/**
 * Custom hook for creating a document
 * In a real application, this would make an API call to create a document
 */
export function useCreateDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (newDocument: Omit<Document, "id">) => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Generate a new document with an ID
      const document: Document = {
        id: `doc-${Date.now()}`,
        ...newDocument,
        // Add any missing properties with default values
        customer: {
          id: newDocument.customerId,
          name: mockDocuments.find((d) => d.customer.id === newDocument.customerId)?.customer.name || "Unknown",
        },
        items: newDocument.items || [],
        amount: newDocument.items?.reduce((sum, item) => sum + item.price * item.quantity, 0) || 0,
      }

      return document
    },
    onSuccess: (newDocument) => {
      // Update the documents query with the new document
      queryClient.setQueryData(["documents"], (oldData: Document[] = []) => [...oldData, newDocument])

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ["document-graph"] })
    },
  })
}

/**
 * Custom hook for updating a document
 * In a real application, this would make an API call to update a document
 */
export function useUpdateDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (updatedDocument: Partial<Document> & { id: string }) => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Get the current documents
      const currentDocuments = queryClient.getQueryData<Document[]>(["documents"]) || []

      // Find the document to update
      const documentIndex = currentDocuments.findIndex((d) => d.id === updatedDocument.id)

      if (documentIndex === -1) {
        throw new Error("Document not found")
      }

      // Update the document
      const document: Document = {
        ...currentDocuments[documentIndex],
        ...updatedDocument,
        // Update customer if customerId changed
        customer: updatedDocument.customerId
          ? {
              id: updatedDocument.customerId,
              name: mockDocuments.find((d) => d.customer.id === updatedDocument.customerId)?.customer.name || "Unknown",
            }
          : currentDocuments[documentIndex].customer,
        // Update amount if items changed
        amount: updatedDocument.items
          ? updatedDocument.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
          : currentDocuments[documentIndex].amount,
      }

      return document
    },
    onSuccess: (updatedDocument) => {
      // Update the documents query with the updated document
      queryClient.setQueryData(["documents"], (oldData: Document[] = []) => {
        return oldData.map((doc) => (doc.id === updatedDocument.id ? updatedDocument : doc))
      })

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ["document-graph"] })
    },
  })
}

/**
 * Custom hook for deleting a document
 * In a real application, this would make an API call to delete a document
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (documentId: string) => {
      // Simulate API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      return documentId
    },
    onSuccess: (documentId) => {
      // Update the documents query by removing the deleted document
      queryClient.setQueryData(["documents"], (oldData: Document[] = []) => {
        return oldData.filter((doc) => doc.id !== documentId)
      })

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ["document-graph"] })
      queryClient.invalidateQueries({ queryKey: ["document-relationships"] })
    },
  })
}
