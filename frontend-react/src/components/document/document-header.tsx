"use client"

import { Button } from "@/components/ui/button"
import { PlusCircle } from "lucide-react"
import { useState } from "react"
import { DocumentCreateModal } from "@/components/document/document-create-modal"

/**
 * DocumentHeader component that displays the header of the document management section
 * It includes the title and a button to create a new document
 */
export function DocumentHeader() {
  // State to control the visibility of the create document modal
  const [showCreateModal, setShowCreateModal] = useState(false)

  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Document Management</h1>
        <p className="text-muted-foreground">Manage your documents and visualize their relationships</p>
      </div>

      <Button onClick={() => setShowCreateModal(true)}>
        <PlusCircle className="mr-2 h-4 w-4" />
        New Document
      </Button>

      {/* Modal for creating a new document */}
      {showCreateModal && <DocumentCreateModal open={showCreateModal} onOpenChange={setShowCreateModal} />}
    </div>
  )
}
