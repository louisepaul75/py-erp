"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { Document, DocumentType } from "@/types/document/document"
import { instance } from "@/lib/api" // Use the shared API instance
import { useToast } from "@/hooks/use-toast"

const API_URL = "sales/records/"

/**
 * Custom hook for fetching documents
 * Fetches documents from the backend API
 */
export function useDocuments() {
  return useQuery<Document[], Error>({ // Add explicit types
    queryKey: ["documents"],
    queryFn: async () => {
      try {
        // Fetch data from the API endpoint using the shared instance
        const response = await instance.get(API_URL).json<any>() // Use any temporarily for mapping
        let results: any[] = []

        // Handle paginated response common in DRF
        if (response && Array.isArray(response.results)) {
           results = response.results;
        } else if (Array.isArray(response)) {
           // Handle non-paginated response if applicable
           results = response;
        } else {
           console.warn("Unexpected API response structure:", response);
           return [] // Return empty array if structure is wrong
        }

        // Map API response to Document type
        const mappedDocuments: Document[] = results.map(doc => ({
          id: doc.id.toString(), // Ensure ID is string
          type: doc.record_type as DocumentType, // Assuming record_type maps to DocumentType
          number: doc.record_number,
          date: doc.record_date,
          status: doc.payment_status, // Assuming payment_status maps to status
          customer: {
            id: doc.customer.toString(), // Map customer ID
            name: doc.customer_details?.name || "Unknown Customer" // Provide a fallback name
            // TODO: Fetch full customer details if needed separately or adjust API
          },
          amount: parseFloat(doc.total_amount) || 0, // Parse amount, default to 0
          items: [], // TODO: Map items if available and needed in the table
          notes: doc.notes,
          // TODO: Map paymentInfo if available and needed
          paymentInfo: undefined, 
        }));

        return mappedDocuments;

      } catch (error) {
        console.error("Error fetching documents:", error)
        throw new Error("Failed to fetch documents") // Re-throw error for React Query
      }
    },
  })
}

/**
 * Custom hook for creating a document
 * Makes an API call to create a document
 */
export function useCreateDocument() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation<Document, Error, any>({ 
    mutationFn: async (newDocumentData: any) => {
      try {
        const response = await instance.post(API_URL, { json: newDocumentData }).json<Document>()
        return response
      } catch (error) {
        console.error("Error creating document:", error)
        toast({
          title: "Error Creating Document",
          description: error instanceof Error ? error.message : "Could not create document.",
          variant: "destructive",
        })
        throw error // Re-throw error for mutation state
      }
    },
    onSuccess: (newDocument) => {
      // Update the documents query with the new document
      queryClient.setQueryData(["documents"], (oldData: Document[] = []) => [...oldData, newDocument])
      // Invalidate to refetch if necessary, or just add optimistically
      queryClient.invalidateQueries({ queryKey: ["documents"] })
      queryClient.invalidateQueries({ queryKey: ["document-graph"] }) // Invalidate related graph
      toast({
        title: "Document Created",
        description: `Document ${newDocument.number} created successfully.`,
      })
    },
    onError: (error) => {
        // Toast is handled in mutationFn's catch block, but you could add more specific handling here
        console.error("Mutation error:", error)
    }
  })
}

/**
 * Custom hook for updating a document
 * Makes an API call to update a document
 */
export function useUpdateDocument() {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation<Document, Error, Partial<Document> & { id: string }>({ 
    mutationFn: async (updatedDocumentData) => {
      const { id, ...dataToUpdate } = updatedDocumentData
      try {
        const updateUrl = `${API_URL.endsWith('/') ? API_URL : API_URL + '/'}${id}/`
        const response = await instance.put(updateUrl, { json: dataToUpdate }).json<Document>()
        return response
      } catch (error) {
        console.error("Error updating document:", error)
        toast({
          title: "Error Updating Document",
          description: error instanceof Error ? error.message : "Could not update document.",
          variant: "destructive",
        })
        throw error
      }
    },
    onSuccess: (updatedDocument) => {
      // Update the documents query optimistically
      queryClient.setQueryData(["documents"], (oldData: Document[] = []) =>
        oldData.map((doc) => (doc.id === updatedDocument.id ? updatedDocument : doc)),
      )
      // Invalidate to ensure consistency or just rely on optimistic update
      queryClient.invalidateQueries({ queryKey: ["documents"] })
      queryClient.invalidateQueries({ queryKey: ["document-graph"] }) // Invalidate related graph
       toast({
        title: "Document Updated",
        description: `Document ${updatedDocument.number} updated successfully.`,
      })
    },
     onError: (error) => {
        console.error("Mutation error:", error)
    }
  })
}

/**
 * Custom hook for deleting a document
 * Makes an API call to delete a document
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient()
   const { toast } = useToast()

  return useMutation<void, Error, string>({ // Return void on success
    mutationFn: async (documentId: string) => {
       try {
         const deleteUrl = `${API_URL.endsWith('/') ? API_URL : API_URL + '/'}${documentId}/`
         await instance.delete(deleteUrl)
       } catch (error) {
         console.error("Error deleting document:", error)
         toast({
            title: "Error Deleting Document",
            description: error instanceof Error ? error.message : "Could not delete document.",
            variant: "destructive",
        })
         throw error
       }
    },
    onSuccess: (_, documentId) => { // Get documentId from variables
      // Update the documents query optimistically
      queryClient.setQueryData(["documents"], (oldData: Document[] = []) =>
        oldData.filter((doc) => doc.id !== documentId),
      )
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ["documents"] })
      queryClient.invalidateQueries({ queryKey: ["document-graph"] })
      queryClient.invalidateQueries({ queryKey: ["document-relationships"] })
      toast({
        title: "Document Deleted",
        description: `Document deleted successfully.`,
      })
    },
     onError: (error) => {
        console.error("Mutation error:", error)
    }
  })
}
