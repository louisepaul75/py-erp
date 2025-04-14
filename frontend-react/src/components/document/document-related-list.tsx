"use client"

import { useDocumentRelationships } from "@/hooks/use-document-relationships"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Eye, Plus } from "lucide-react"
import { useState } from "react"
import type { DocumentType } from "@/types/document/document"
import { DocumentRelationCreateModal } from "@/components/sales-flow/document-relation-create-modal"
import { formatDate } from "@/lib/utils"

/**
 * Props for the DocumentRelatedList component
 */
interface DocumentRelatedListProps {
  documentId: string
}

/**
 * DocumentRelatedList component that displays a list of related documents
 */
export function DocumentRelatedList({ documentId }: DocumentRelatedListProps) {
  // Fetch document relationships using TanStack Query
  const { data, isLoading, isError } = useDocumentRelationships(documentId)

  // State for the create relation modal
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Get badge color based on document type
  const getTypeColor = (type: DocumentType) => {
    switch (type) {
      case "ORDER":
        return "bg-blue-100 text-blue-800"
      case "DELIVERY":
        return "bg-green-100 text-green-800"
      case "INVOICE":
        return "bg-purple-100 text-purple-800"
      case "CREDIT":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  // Get badge color based on relation type
  const getRelationColor = (type: string) => {
    switch (type) {
      case "BASED_ON":
        return "bg-blue-100 text-blue-800"
      case "CANCELS":
        return "bg-red-100 text-red-800"
      case "PARTIAL":
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  // Loading state
  if (isLoading) {
    return <div className="flex justify-center p-8">Loading related documents...</div>
  }

  // Error state
  if (isError) {
    return <div className="flex justify-center p-8 text-red-500">Error loading related documents</div>
  }

  return (
    <div className="space-y-4 py-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Related Documents</h3>
        <Button size="sm" onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Relation
        </Button>
      </div>

      {data && data.length > 0 ? (
        <div className="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Relation</TableHead>
                <TableHead>Document</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((relation) => (
                <TableRow key={relation.id}>
                  <TableCell>
                    <Badge className={getRelationColor(relation.relationType)}>{relation.relationType}</Badge>
                  </TableCell>
                  <TableCell className="font-medium">{relation.relatedDocument.number}</TableCell>
                  <TableCell>
                    <Badge className={getTypeColor(relation.relatedDocument.type)}>
                      {relation.relatedDocument.type}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatDate(relation.relatedDocument.date)}</TableCell>
                  <TableCell>{relation.relatedDocument.status}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : (
        <div className="border rounded-md p-8 text-center text-muted-foreground">
          No related documents found. Add a relation using the button above.
        </div>
      )}

      {showCreateModal && (
        <DocumentRelationCreateModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
          sourceDocumentId={documentId}
        />
      )}
    </div>
  )
}
