"use client"

import { useState, Suspense } from "react"
import { DocumentList } from "@/components/document/document-list" // Assuming this exists or will be created
import { SalesFlow } from "@/components/sales-flow/document-flow" // Updated path
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SearchFilters } from "@/components/search/search-filters" // Updated path
import { DocumentHeader } from "@/components/document/document-header" // Updated path
import { useMediaQuery } from "@/hooks/document/use-media-query" // Updated path

/**
 * Sales Flow Page
 * Displays sales documents in list and flow views.
 */
export default function SalesFlowPage() {
  const [activeView, setActiveView] = useState<"list" | "flow">("list")
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | undefined>(undefined)
  const isTablet = useMediaQuery("(max-width: 1024px)") // This hook might need adjustment depending on project standards

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocumentId(documentId)
    setActiveView("flow")
  }

  return (
    // Consider using a standard PageWrapper or Layout component if available in the main app
    <div className="container mx-auto px-4 py-6"> 
      {/* Use a standardized header component if available */}
      <DocumentHeader /> 

      <div className="my-6">
        <Suspense fallback={<div className="p-4 border rounded-md">Loading Filters...</div>}>
          <SearchFilters />
        </Suspense>
      </div>

      <Tabs defaultValue="list" value={activeView} onValueChange={(value) => setActiveView(value as "list" | "flow")}>
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="list">Document List</TabsTrigger>
          <TabsTrigger value="flow">Document Flow</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-0">
          {/* Ensure DocumentList component exists and is correctly imported/placed */}
          <DocumentList onDocumentSelect={handleDocumentSelect} />
        </TabsContent>

        <TabsContent value="flow" className="mt-0">
          <SalesFlow initialDocumentId={selectedDocumentId} />
        </TabsContent>
      </Tabs>
    </div>
  )
} 