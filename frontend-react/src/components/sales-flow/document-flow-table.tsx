"use client"

import type React from "react"

import { useState, useEffect, useMemo } from "react"
import { useDocumentGraph } from "@/hooks/document/use-document-graph"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ChevronRight, ChevronDown, ArrowDown, ArrowUp, ExternalLink } from "lucide-react"
import { formatDate } from "@/lib/utils"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useDocuments } from "@/hooks/document/use-documents"
import type { DocumentType } from "@/types/document/document"
import { Card, CardContent } from "@/components/ui/card"

/**
 * Props for the DocumentFlowTable component
 */
interface DocumentFlowTableProps {
  initialDocumentId?: string // Optional: If provided, this document will be pre-selected
  onViewDocument?: (documentId: string) => void // Optional: Callback for viewing a document
}

/**
 * DocumentFlowTable component that displays a hierarchical tree view of document relationships
 * This provides a non-graphical alternative to the flow diagram
 */
export function DocumentFlowTable({ initialDocumentId, onViewDocument }: DocumentFlowTableProps) {
  // Fetch all documents
  const { data: allDocuments } = useDocuments()

  // State for the selected document
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(initialDocumentId || null)

  // Fetch document graph data using TanStack Query
  const { data: graphData, isLoading, isError } = useDocumentGraph()

  // State for expanded document relationships
  const [expandedDocuments, setExpandedDocuments] = useState<Record<string, boolean>>({})

  // State for search term
  const [searchTerm, setSearchTerm] = useState("")

  // Initialize with initial document expanded if provided
  useEffect(() => {
    if (initialDocumentId) {
      setExpandedDocuments((prev) => ({
        ...prev,
        [initialDocumentId]: true,
      }))
    }
  }, [initialDocumentId])

  // Handle document selection change
  const handleDocumentChange = (documentId: string) => {
    setSelectedDocumentId(documentId)
    setExpandedDocuments((prev) => ({
      ...prev,
      [documentId]: true,
    }))
  }

  // Get badge color based on document type
  const getTypeColor = (type: DocumentType) => {
    switch (type) {
      case "ORDER":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "DELIVERY":
        return "bg-green-100 text-green-800 border-green-200"
      case "INVOICE":
        return "bg-purple-100 text-purple-800 border-purple-200"
      case "CREDIT":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  // Get background color based on document type
  const getTypeBgColor = (type: DocumentType) => {
    switch (type) {
      case "ORDER":
        return "bg-blue-50"
      case "DELIVERY":
        return "bg-green-50"
      case "INVOICE":
        return "bg-purple-50"
      case "CREDIT":
        return "bg-red-50"
      default:
        return "bg-gray-50"
    }
  }

  // Get badge color based on document status
  const getStatusColor = (status: string) => {
    switch (status) {
      case "OPEN":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "COMPLETED":
        return "bg-green-100 text-green-800 border-green-200"
      case "CANCELED":
        return "bg-red-100 text-red-800 border-red-200"
      case "PAID":
        return "bg-blue-100 text-blue-800 border-blue-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  // Get badge color based on relation type
  const getRelationColor = (type: string) => {
    switch (type) {
      case "BASED_ON":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "CANCELS":
        return "bg-red-100 text-red-800 border-red-200"
      case "PARTIAL":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  // Get relationship description
  const getRelationshipDescription = (relationType: string, sourceType: DocumentType, targetType: DocumentType) => {
    if (relationType === "BASED_ON") {
      if (sourceType === "DELIVERY" && targetType === "ORDER") {
        return "Lieferschein aus Auftrag"
      } else if (sourceType === "INVOICE" && targetType === "DELIVERY") {
        return "Rechnung aus Lieferschein"
      } else if (sourceType === "CREDIT" && targetType === "INVOICE") {
        return "Gutschrift aus Rechnung"
      }
      return `${sourceType} aus ${targetType}`
    } else if (relationType === "CANCELS") {
      return `Storniert ${targetType}`
    } else if (relationType === "PARTIAL") {
      if (sourceType === "DELIVERY" && targetType === "ORDER") {
        return "Teillieferung aus Auftrag"
      } else if (sourceType === "INVOICE" && targetType === "DELIVERY") {
        return "Teilrechnung aus Lieferschein"
      } else if (sourceType === "CREDIT" && targetType === "INVOICE") {
        return "Teilgutschrift aus Rechnung"
      }
      return `Teil-${sourceType} aus ${targetType}`
    }
    return relationType
  }

  // Filter documents based on search term
  const filteredDocuments = allDocuments

  // Build document hierarchy tree
  const documentTree = useMemo(() => {
    if (!graphData || !allDocuments || !selectedDocumentId) return null

    // Function to recursively build the tree
    const buildTree = (documentId: string, visited = new Set<string>()) => {
      // Prevent infinite recursion
      if (visited.has(documentId)) return null
      visited.add(documentId)

      const document = allDocuments.find((doc) => doc.id === documentId)
      if (!document) return null

      // Find all relationships where this document is the source
      const childRelationships = graphData.relationships.filter((rel) => rel.sourceId === documentId)

      // Find all relationships where this document is the target
      const parentRelationships = graphData.relationships.filter((rel) => rel.targetId === documentId)

      // Build child nodes
      const children = childRelationships
        .map((rel) => {
          const childDoc = allDocuments.find((doc) => doc.id === rel.targetId)
          if (!childDoc) return null

          // Don't recursively build children to avoid circular references
          return {
            document: childDoc,
            relationship: rel,
            children: [], // We'll populate this later if needed
            parents: [], // We'll populate this later if needed
          }
        })
        .filter(Boolean)

      // Build parent nodes
      const parents = parentRelationships
        .map((rel) => {
          const parentDoc = allDocuments.find((doc) => doc.id === rel.sourceId)
          if (!parentDoc) return null

          // Don't recursively build parents to avoid circular references
          return {
            document: parentDoc,
            relationship: rel,
            children: [], // We'll populate this later if needed
            parents: [], // We'll populate this later if needed
          }
        })
        .filter(Boolean)

      return {
        document,
        children,
        parents,
      }
    }

    return buildTree(selectedDocumentId)
  }, [graphData, allDocuments, selectedDocumentId])

  // Function to load relationships on demand
  const loadRelationships = (documentId: string, isParent = false) => {
    if (!graphData || !allDocuments) return

    // Find the document in our tree
    const findAndUpdateNode = (node: any, targetId: string, isParentRelation = false) => {
      if (!node) return false

      // Check if this is the node we're looking for
      if (node.document.id === targetId) {
        // If we're looking for parent relationships
        if (isParentRelation && (!node.parents || node.parents.length === 0)) {
          const parentRelationships = graphData.relationships.filter((rel) => rel.targetId === targetId)

          node.parents = parentRelationships
            .map((rel) => {
              const parentDoc = allDocuments.find((doc) => doc.id === rel.sourceId)
              if (!parentDoc) return null

              return {
                document: parentDoc,
                relationship: rel,
                children: [],
                parents: [],
              }
            })
            .filter(Boolean)
        }

        // If we're looking for child relationships
        if (!isParentRelation && (!node.children || node.children.length === 0)) {
          const childRelationships = graphData.relationships.filter((rel) => rel.sourceId === targetId)

          node.children = childRelationships
            .map((rel) => {
              const childDoc = allDocuments.find((doc) => doc.id === rel.targetId)
              if (!childDoc) return null

              return {
                document: childDoc,
                relationship: rel,
                children: [],
                parents: [],
              }
            })
            .filter(Boolean)
        }

        return true
      }

      // Check children
      if (node.children) {
        for (const child of node.children) {
          if (findAndUpdateNode(child, targetId, isParentRelation)) {
            return true
          }
        }
      }

      // Check parents
      if (node.parents) {
        for (const parent of node.parents) {
          if (findAndUpdateNode(parent, targetId, isParentRelation)) {
            return true
          }
        }
      }

      return false
    }

    // Update the tree with new relationships
    if (documentTree) {
      findAndUpdateNode(documentTree, documentId, isParent)
    }
  }

  // Toggle document expansion and load relationships if needed
  const toggleDocumentExpansion = (documentId: string, isParent = false, e?: React.MouseEvent) => {
    // Verhindern der Event-Propagation, falls ein Event übergeben wurde
    if (e) {
      e.stopPropagation()
    }

    // Toggle expansion state
    setExpandedDocuments((prev) => ({
      ...prev,
      [documentId]: !prev[documentId],
    }))

    // Wenn das Dokument noch nicht expandiert ist, laden wir die Beziehungen
    if (!expandedDocuments[documentId]) {
      loadRelationships(documentId, isParent)
    }
  }

  // Loading state
  if (isLoading) {
    return <div className="flex justify-center p-8">Dokumentenbeziehungen werden geladen...</div>
  }

  // Error state
  if (isError) {
    return <div className="flex justify-center p-8 text-red-500">Fehler beim Laden der Dokumentenbeziehungen</div>
  }

  // Render a document node
  const renderDocumentNode = (
    doc: any,
    relationship: any = null,
    level = 0,
    isParent = false,
    isLast = false,
    path: string[] = [],
  ) => {
    const isExpanded = expandedDocuments[doc.document.id]
    const hasChildren = doc.children && doc.children.length > 0
    const hasParents = doc.parents && doc.parents.length > 0
    const showChildren = isExpanded && hasChildren
    const showParents = isExpanded && hasParents
    const nodePath = [...path, doc.document.id]
    const nodePathKey = nodePath.join("-")

    return (
      <div key={nodePathKey} className="relative">
        {/* Connection lines */}
        {level > 0 && (
          <div
            className={`absolute left-4 ${isParent ? "bottom-1/2" : "top-0"} w-px h-8 border-l-2 ${
              isParent ? "border-dashed border-gray-300" : "border-gray-300"
            }`}
          />
        )}

        {level > 0 && (
          <div
            className={`absolute top-4 left-4 w-6 h-px border-t-2 ${
              isParent ? "border-dashed border-gray-300" : "border-gray-300"
            }`}
          />
        )}

        {/* Document node */}
        <div
          className={`relative ml-${level * 10} ${level > 0 ? "pl-10" : ""} mb-2`}
          style={{ marginLeft: level > 0 ? `${level * 20}px` : "0" }}
        >
          <div
            className={`border rounded-md p-3 ${getTypeBgColor(doc.document.type)} ${
              doc.document.id === selectedDocumentId ? "ring-2 ring-primary" : ""
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {(hasChildren || hasParents) && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 p-0"
                    onClick={(e) => toggleDocumentExpansion(doc.document.id, isParent, e)}
                  >
                    {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  </Button>
                )}

                <Badge className={getTypeColor(doc.document.type)}>{doc.document.type}</Badge>

                <span className="font-medium">{doc.document.number}</span>

                {relationship && (
                  <div className="flex items-center gap-1">
                    {isParent ? (
                      <ArrowUp className="h-3 w-3 text-gray-500" />
                    ) : (
                      <ArrowDown className="h-3 w-3 text-gray-500" />
                    )}
                    <Badge className={getRelationColor(relationship.type)} variant="outline">
                      {isParent
                        ? getRelationshipDescription(
                            relationship.type,
                            doc.document.type,
                            selectedDocumentId
                              ? allDocuments?.find((d) => d.id === selectedDocumentId)?.type || "ORDER"
                              : "ORDER",
                          )
                        : getRelationshipDescription(
                            relationship.type,
                            selectedDocumentId
                              ? allDocuments?.find((d) => d.id === selectedDocumentId)?.type || "ORDER"
                              : "ORDER",
                            doc.document.type,
                          )}
                    </Badge>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                <Badge className={getStatusColor(doc.document.status)}>{doc.document.status}</Badge>

                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 p-0"
                  onClick={() => handleDocumentChange(doc.document.id)}
                >
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-2 text-sm">
              <div>
                <span className="text-muted-foreground">Kunde:</span> {doc.document.customer.name}
              </div>
              <div>
                <span className="text-muted-foreground">Datum:</span> {formatDate(doc.document.date)}
              </div>
              <div>
                <span className="text-muted-foreground">Betrag:</span> {doc.document.amount.toFixed(2)} €
              </div>
            </div>
          </div>
        </div>

        {/* Children nodes */}
        {showChildren &&
          doc.children &&
          doc.children.map((child: any, index: number) =>
            renderDocumentNode(
              child,
              child.relationship,
              level + 1,
              false,
              index === doc.children.length - 1,
              nodePath,
            ),
          )}

        {/* Parent nodes */}
        {showParents &&
          doc.parents &&
          doc.parents.map((parent: any, index: number) =>
            renderDocumentNode(
              parent,
              parent.relationship,
              level + 1,
              true,
              index === doc.parents.length - 1,
              nodePath,
            ),
          )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="flex-1">
          <Select value={selectedDocumentId || ""} onValueChange={handleDocumentChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Dokument auswählen" />
            </SelectTrigger>
            <SelectContent>
              {filteredDocuments?.map((doc) => (
                <SelectItem key={doc.id} value={doc.id}>
                  {doc.type} - {doc.number} - {doc.customer.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {selectedDocumentId && documentTree ? (
        <div className="border rounded-md p-4 overflow-auto max-h-[70vh]">
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded-full bg-blue-100 border border-blue-200"></div>
                <span className="text-sm">Auftrag</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded-full bg-green-100 border border-green-200"></div>
                <span className="text-sm">Lieferschein</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded-full bg-purple-100 border border-purple-200"></div>
                <span className="text-sm">Rechnung</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-4 rounded-full bg-red-100 border border-red-200"></div>
                <span className="text-sm">Gutschrift</span>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <ArrowDown className="h-3 w-3" />
                <span>Abgeleitete Dokumente</span>
              </div>
              <div className="flex items-center gap-1">
                <ArrowUp className="h-3 w-3" />
                <span>Basisdokumente</span>
              </div>
            </div>
          </div>

          {/* Document tree */}
          {renderDocumentNode(documentTree, null, 0, false, false)}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-6 text-center">
            <p className="text-muted-foreground mb-4">
              Bitte wählen Sie ein Dokument aus, um dessen Beziehungen anzuzeigen.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
