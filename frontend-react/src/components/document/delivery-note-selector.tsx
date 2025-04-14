"use client"

import { useState, useEffect, useRef, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { formatDate } from "@/lib/utils"
import { useDocuments } from "@/hooks/document/use-documents"
import { ChevronDown, ChevronRight, X, Package, Calendar, DollarSign, User } from "lucide-react"
import { format } from "date-fns"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent } from "@/components/ui/card"

/**
 * Props for the DeliveryNoteSelector component
 */
interface DeliveryNoteSelectorProps {
  selectedDocumentIds: string[]
  onDocumentSelectionChange: (documentIds: string[]) => void
  selectedItems: Record<string, boolean>
  onItemSelectionChange: (items: Record<string, boolean>) => void
  sourceDocumentId?: string // Optional: If provided, this document will be pre-selected
}

/**
 * DeliveryNoteSelector component that displays a list of delivery notes for selection
 * This component is used in the collective invoice creation process
 */
export function DeliveryNoteSelector({
  selectedDocumentIds,
  onDocumentSelectionChange,
  selectedItems,
  onItemSelectionChange,
  sourceDocumentId,
}: DeliveryNoteSelectorProps) {
  const { data: documents } = useDocuments()

  // State for expanded documents
  const [expandedDocuments, setExpandedDocuments] = useState<Record<string, boolean>>({})

  // State for search and filters
  const [searchTerm, setSearchTerm] = useState("")
  const [customerFilter, setCustomerFilter] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string | null>(null)
  const [dateRangeFilter, setDateRangeFilter] = useState<{
    from: Date | undefined
    to: Date | undefined
  }>({
    from: undefined,
    to: undefined,
  })
  const [minAmountFilter, setMinAmountFilter] = useState<number | null>(null)
  const [maxAmountFilter, setMaxAmountFilter] = useState<number | null>(null)

  // State for pagination
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  // Filter documents to only show delivery notes
  const allDeliveryNotes = useMemo(() => {
    return documents?.filter((doc) => doc.type === "DELIVERY") || []
  }, [documents])

  // Get unique customers for filter dropdown
  const uniqueCustomers = useMemo(() => {
    const customers = allDeliveryNotes.map((doc) => doc.customer)
    return Array.from(new Map(customers.map((customer) => [customer.id, customer])).values())
  }, [allDeliveryNotes])

  // Get unique statuses for filter dropdown
  const uniqueStatuses = useMemo(() => {
    const statuses = allDeliveryNotes.map((doc) => doc.status)
    return Array.from(new Set(statuses))
  }, [allDeliveryNotes])

  // Apply filters and search
  const filteredDeliveryNotes = useMemo(() => {
    return allDeliveryNotes.filter((doc) => {
      // Apply search term
      const matchesSearch =
        searchTerm === "" ||
        doc.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.notes?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.items.some(
          (item) =>
            item.productId.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.description.toLowerCase().includes(searchTerm.toLowerCase()),
        )

      // Apply customer filter
      const matchesCustomer = customerFilter === null || doc.customer.id === customerFilter

      // Apply status filter
      const matchesStatus = statusFilter === null || doc.status === statusFilter

      // Apply date range filter
      const docDate = new Date(doc.date)
      const matchesDateFrom = !dateRangeFilter.from || docDate >= dateRangeFilter.from
      const matchesDateTo = !dateRangeFilter.to || docDate <= dateRangeFilter.to

      // Apply amount filters
      const matchesMinAmount = minAmountFilter === null || doc.amount >= minAmountFilter
      const matchesMaxAmount = maxAmountFilter === null || doc.amount <= maxAmountFilter

      return (
        matchesSearch &&
        matchesCustomer &&
        matchesStatus &&
        matchesDateFrom &&
        matchesDateTo &&
        matchesMinAmount &&
        matchesMaxAmount
      )
    })
  }, [allDeliveryNotes, searchTerm, customerFilter, statusFilter, dateRangeFilter, minAmountFilter, maxAmountFilter])

  // Paginate the filtered delivery notes
  const paginatedDeliveryNotes = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return filteredDeliveryNotes.slice(startIndex, startIndex + itemsPerPage)
  }, [filteredDeliveryNotes, currentPage, itemsPerPage])

  // Calculate total pages
  const totalPages = Math.ceil(filteredDeliveryNotes.length / itemsPerPage)

  // Initialize with source document expanded if provided
  useEffect(() => {
    if (sourceDocumentId) {
      setExpandedDocuments((prev) => ({
        ...prev,
        [sourceDocumentId]: true,
      }))
    }
  }, [sourceDocumentId])

  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, customerFilter, statusFilter, dateRangeFilter, minAmountFilter, maxAmountFilter])

  // Toggle document selection
  const toggleDocumentSelection = (documentId: string) => {
    const isSelected = selectedDocumentIds.includes(documentId)
    const newSelectedDocumentIds = isSelected
      ? selectedDocumentIds.filter((id) => id !== documentId)
      : [...selectedDocumentIds, documentId]

    onDocumentSelectionChange(newSelectedDocumentIds)

    // If document is selected, also select all its items
    // If document is deselected, also deselect all its items
    const document = allDeliveryNotes.find((doc) => doc.id === documentId)
    if (document) {
      const newSelectedItems = { ...selectedItems }
      document.items.forEach((item) => {
        newSelectedItems[item.id] = !isSelected
      })
      onItemSelectionChange(newSelectedItems)
    }

    // Expand the document when selected
    if (!expandedDocuments[documentId]) {
      setExpandedDocuments((prev) => ({
        ...prev,
        [documentId]: true,
      }))
    }
  }

  // Toggle document expansion
  const toggleDocumentExpansion = (documentId: string) => {
    setExpandedDocuments((prev) => ({
      ...prev,
      [documentId]: !prev[documentId],
    }))
  }

  // Toggle item selection
  const toggleItemSelection = (itemId: string) => {
    onItemSelectionChange({
      ...selectedItems,
      [itemId]: !selectedItems[itemId],
    })
  }

  // Toggle all items from a document
  const toggleAllItemsFromDocument = (documentId: string, value: boolean) => {
    const document = allDeliveryNotes.find((doc) => doc.id === documentId)
    if (document) {
      const newSelectedItems = { ...selectedItems }
      document.items.forEach((item) => {
        newSelectedItems[item.id] = value
      })
      onItemSelectionChange(newSelectedItems)
    }
  }

  // Check if all items from a document are selected
  const areAllItemsFromDocumentSelected = (documentId: string): boolean => {
    const document = allDeliveryNotes.find((doc) => doc.id === documentId)
    if (!document || document.items.length === 0) return false
    return document.items.every((item) => selectedItems[item.id])
  }

  // Check if some items from a document are selected
  const areSomeItemsFromDocumentSelected = (documentId: string): boolean => {
    const document = allDeliveryNotes.find((doc) => doc.id === documentId)
    if (!document || document.items.length === 0) return false
    return document.items.some((item) => selectedItems[item.id]) && !areAllItemsFromDocumentSelected(documentId)
  }

  // Select all documents and items
  const selectAllDocuments = () => {
    onDocumentSelectionChange(filteredDeliveryNotes.map((doc) => doc.id))

    const newSelectedItems = { ...selectedItems }
    filteredDeliveryNotes.forEach((doc) => {
      doc.items.forEach((item) => {
        newSelectedItems[item.id] = true
      })
    })
    onItemSelectionChange(newSelectedItems)
  }

  // Deselect all documents and items
  const deselectAllDocuments = () => {
    onDocumentSelectionChange([])

    const newSelectedItems = { ...selectedItems }
    filteredDeliveryNotes.forEach((doc) => {
      doc.items.forEach((item) => {
        newSelectedItems[item.id] = false
      })
    })
    onItemSelectionChange(newSelectedItems)
  }

  // Reset all filters
  const resetFilters = () => {
    setSearchTerm("")
    setCustomerFilter(null)
    setStatusFilter(null)
    setDateRangeFilter({ from: undefined, to: undefined })
    setMinAmountFilter(null)
    setMaxAmountFilter(null)
  }

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  // Get status badge color
  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "DELIVERED":
        return "bg-green-100 text-green-800 border-green-200"
      case "SHIPPED":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "OPEN":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  return (
    <div className="space-y-4">
      {/* Filter Summary */}
      {(customerFilter ||
        statusFilter ||
        dateRangeFilter.from ||
        dateRangeFilter.to ||
        minAmountFilter ||
        maxAmountFilter) && (
        <div className="flex flex-wrap gap-2 text-sm mb-4">
          {customerFilter && (
            <Badge variant="outline" className="flex items-center gap-1 py-1 px-2">
              <User className="h-3 w-3 mr-1" />
              {uniqueCustomers.find((c) => c.id === customerFilter)?.name}
              <Button variant="ghost" size="icon" className="h-4 w-4 p-0 ml-1" onClick={() => setCustomerFilter(null)}>
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          )}

          {statusFilter && (
            <Badge variant="outline" className="flex items-center gap-1 py-1 px-2">
              <Package className="h-3 w-3 mr-1" />
              {statusFilter}
              <Button variant="ghost" size="icon" className="h-4 w-4 p-0 ml-1" onClick={() => setStatusFilter(null)}>
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          )}

          {(dateRangeFilter.from || dateRangeFilter.to) && (
            <Badge variant="outline" className="flex items-center gap-1 py-1 px-2">
              <Calendar className="h-3 w-3 mr-1" />
              {dateRangeFilter.from ? format(dateRangeFilter.from, "dd.MM.yyyy") : "..."} -{" "}
              {dateRangeFilter.to ? format(dateRangeFilter.to, "dd.MM.yyyy") : "..."}
              <Button
                variant="ghost"
                size="icon"
                className="h-4 w-4 p-0 ml-1"
                onClick={() => setDateRangeFilter({ from: undefined, to: undefined })}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          )}

          {(minAmountFilter !== null || maxAmountFilter !== null) && (
            <Badge variant="outline" className="flex items-center gap-1 py-1 px-2">
              <DollarSign className="h-3 w-3 mr-1" />
              {minAmountFilter !== null ? `${minAmountFilter} €` : "..."} -{" "}
              {maxAmountFilter !== null ? `${maxAmountFilter} €` : "..."}
              <Button
                variant="ghost"
                size="icon"
                className="h-4 w-4 p-0 ml-1"
                onClick={() => {
                  setMinAmountFilter(null)
                  setMaxAmountFilter(null)
                }}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          )}

          <Button variant="ghost" size="sm" className="h-7 px-2 text-xs" onClick={resetFilters}>
            Filter zurücksetzen
          </Button>
        </div>
      )}

      <div className="space-y-3">
        {paginatedDeliveryNotes.length > 0 ? (
          paginatedDeliveryNotes.map((document) => {
            const isExpanded = expandedDocuments[document.id]
            const allItemsSelected = areAllItemsFromDocumentSelected(document.id)
            const someItemsSelected = areSomeItemsFromDocumentSelected(document.id)

            return (
              <Card key={document.id} className="mb-3 overflow-hidden">
                <div
                  className={`p-3 flex justify-between items-center cursor-pointer border-b ${
                    selectedDocumentIds.includes(document.id) ? "bg-primary/5" : "bg-white"
                  }`}
                  onClick={() => toggleDocumentExpansion(document.id)}
                >
                  <div className="flex items-center gap-3">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6 p-0"
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleDocumentExpansion(document.id)
                      }}
                    >
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </Button>
                    <Checkbox
                      checked={selectedDocumentIds.includes(document.id)}
                      onCheckedChange={() => toggleDocumentSelection(document.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="h-5 w-5"
                    />
                    <div>
                      <div className="font-medium">{document.number}</div>
                      <div className="text-sm text-muted-foreground">{document.customer.name}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className={`${getStatusBadgeColor(document.status)}`}>
                      {document.status}
                    </Badge>
                    <div className="text-right">
                      <div className="text-sm">{formatDate(document.date)}</div>
                      <div className="font-medium">{document.amount.toFixed(2)} €</div>
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <CardContent className="p-3 pt-4 bg-gray-50">
                    <div className="flex items-center mb-3">
                      <IndeterminateCheckbox
                        checked={allItemsSelected}
                        indeterminate={someItemsSelected}
                        onCheckedChange={(checked) => toggleAllItemsFromDocument(document.id, !!checked)}
                        className="mr-2"
                      />
                      <span className="text-sm font-medium">Alle Positionen ({document.items.length})</span>
                    </div>
                    {document.items.length > 0 ? (
                      <div className="border rounded-md overflow-hidden bg-white">
                        <Table>
                          <TableHeader className="bg-muted">
                            <TableRow>
                              <TableHead className="w-[50px]"></TableHead>
                              <TableHead>Artikel-Nr.</TableHead>
                              <TableHead>Beschreibung</TableHead>
                              <TableHead className="text-right">Menge</TableHead>
                              <TableHead className="text-right">Preis</TableHead>
                              <TableHead className="text-right">Gesamt</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {document.items.map((item) => (
                              <TableRow key={item.id}>
                                <TableCell className="p-2">
                                  <Checkbox
                                    checked={selectedItems[item.id] || false}
                                    onCheckedChange={() => toggleItemSelection(item.id)}
                                  />
                                </TableCell>
                                <TableCell className="p-2 font-medium">{item.productId}</TableCell>
                                <TableCell className="p-2">{item.description}</TableCell>
                                <TableCell className="p-2 text-right">{item.quantity}</TableCell>
                                <TableCell className="p-2 text-right">{item.price.toFixed(2)} €</TableCell>
                                <TableCell className="p-2 text-right font-medium">
                                  {(item.quantity * item.price).toFixed(2)} €
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    ) : (
                      <div className="text-sm text-muted-foreground p-4 text-center bg-white border rounded-md">
                        Keine einzelnen Positionen verfügbar. Gesamtbetrag: {document.amount.toFixed(2)} €
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            )
          })
        ) : (
          <div className="text-center py-8 text-muted-foreground border rounded-md bg-gray-50">
            Keine Lieferscheine gefunden
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-1 mt-6">
          <Button variant="outline" size="sm" onClick={() => handlePageChange(1)} disabled={currentPage === 1}>
            «
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            ‹
          </Button>

          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            let pageNum
            if (totalPages <= 5) {
              pageNum = i + 1
            } else if (currentPage <= 3) {
              pageNum = i + 1
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i
            } else {
              pageNum = currentPage - 2 + i
            }

            return (
              <Button
                key={pageNum}
                variant={currentPage === pageNum ? "default" : "outline"}
                size="sm"
                onClick={() => handlePageChange(pageNum)}
              >
                {pageNum}
              </Button>
            )
          })}

          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            ›
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
          >
            »
          </Button>
        </div>
      )}
    </div>
  )
}

/**
 * IndeterminateCheckbox component that properly handles the indeterminate state
 */
interface IndeterminateCheckboxProps {
  checked: boolean
  indeterminate: boolean
  onCheckedChange: (checked: boolean) => void
  className?: string
}

function IndeterminateCheckbox({ checked, indeterminate, onCheckedChange, className }: IndeterminateCheckboxProps) {
  const checkboxRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (checkboxRef.current) {
      checkboxRef.current.indeterminate = indeterminate
    }
  }, [indeterminate])

  return (
    <Checkbox
      ref={checkboxRef}
      checked={checked}
      onCheckedChange={(checked) => onCheckedChange(!!checked)}
      className={className}
    />
  )
}
