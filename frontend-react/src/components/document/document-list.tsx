"use client"

import { useState, useMemo } from "react"
import { useDocuments } from "@/hooks/document/use-documents"
import { useCustomers } from "@/hooks/customer/use-customers"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import type { Document } from "@/types/document/document"
import { DocumentTable } from "@/components/document/document-table"
import { DocumentModals } from "@/components/document/document-modals"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { OrderCancelView } from "@/components/document/order-cancel-view"

/**
 * Props for the DocumentList component
 */
interface DocumentListProps {
  onDocumentSelect?: (documentId: string) => void
}

/**
 * DocumentList component that displays a table of documents
 * It includes functionality to view, edit, and cancel documents
 */
export function DocumentList({ onDocumentSelect }: DocumentListProps) {
  // Fetch documents using TanStack Query
  const { data: documentsData, isLoading: isLoadingDocuments, isError: isErrorDocuments } = useDocuments()
  // Fetch customers using TanStack Query
  const { data: customersData, isLoading: isLoadingCustomers, isError: isErrorCustomers } = useCustomers()
  const { toast } = useToast()

  // State for the selected document and modal visibility
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showCancelDialog, setShowCancelDialog] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showCollectiveInvoiceView, setShowCollectiveInvoiceView] = useState(false)
  const [showOrderSplitView, setShowOrderSplitView] = useState(false)
  const [showOrderMergeView, setShowOrderMergeView] = useState(false)
  const [showCreditNoteCreateView, setShowCreditNoteCreateView] = useState(false)
  const [showDeliveryNoteCreateView, setShowDeliveryNoteCreateView] = useState(false)
  const [showOrderCancelView, setShowOrderCancelView] = useState(false)

  // State for action confirmation dialog
  const [actionDialogOpen, setActionDialogOpen] = useState(false)
  const [currentAction, setCurrentAction] = useState<{
    title: string
    description: string
    action: () => Promise<void>
  } | null>(null)

  // Handle view document
  const handleView = (document: Document) => {
    setSelectedDocument(document)
    setShowViewModal(true)
  }

  // Handle edit document
  const handleEdit = (document: Document) => {
    setSelectedDocument(document)
    setShowEditModal(true)
  }

  // Handle cancel document
  const handleCancelDocument = (document: Document) => {
    setSelectedDocument(document)
    setShowCancelDialog(true)
  }

  // Handle creating a collective invoice
  const handleCreateCollectiveInvoice = (document: Document) => {
    setSelectedDocument(document)
    setShowCollectiveInvoiceView(true)
  }

  // Handle splitting an order
  const handleSplitOrder = (document: Document) => {
    setSelectedDocument(document)
    setShowOrderSplitView(true)
  }

  // Handle merging orders
  const handleMergeOrders = (document: Document) => {
    setSelectedDocument(document)
    setShowOrderMergeView(true)
  }

  // Handle creating a credit note
  const handleCreateCreditNote = (document: Document) => {
    setSelectedDocument(document)
    setShowCreditNoteCreateView(true)
  }

  // Handle creating a delivery note
  const handleCreateDeliveryNote = (document: Document) => {
    setSelectedDocument(document)
    setShowDeliveryNoteCreateView(true)
  }

  // Handle canceling an order or its positions
  const handleCancelOrder = (document: Document) => {
    setSelectedDocument(document)
    setShowOrderCancelView(true)
  }

  // Handle viewing document flow
  const handleViewFlow = (document: Document) => {
    if (onDocumentSelect) {
      onDocumentSelect(document.id)
    }
  }

  // Helper function to execute an action with confirmation
  const executeAction = (document: Document, title: string, description: string, action: () => Promise<void>) => {
    setSelectedDocument(document)
    setCurrentAction({
      title,
      description,
      action,
    })
    setActionDialogOpen(true)
  }

  // Handle confirmation of the action
  const handleConfirm = async () => {
    if (!currentAction) return

    try {
      await currentAction.action()
      toast({
        title: "Aktion erfolgreich",
        description: `${currentAction.title} wurde erfolgreich durchgeführt.`,
      })
    } catch (error) {
      toast({
        title: "Fehler",
        description: `Fehler bei der Aktion: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`,
        variant: "destructive",
      })
    } finally {
      setActionDialogOpen(false)
      setCurrentAction(null)
    }
  }

  // Combine loading and error states
  const isLoading = isLoadingDocuments || isLoadingCustomers;
  const isError = isErrorDocuments || isErrorCustomers;

  // Re-introduce the customer map for efficient lookup
  const customerMap = useMemo(() => {
    let customersArray: any[] = [];
    if (Array.isArray(customersData)) {
      customersArray = customersData;
    } else if (customersData?.results && Array.isArray(customersData.results)) {
      customersArray = customersData.results;
    }
    return new Map(
      customersArray.map((c) => [c.id?.toString?.(), c.name])
    );
  }, [customersData]);

  // Enrich documents with customer names once both data sets are loaded
  const enrichedDocuments = useMemo(() => {
    console.log("[DocumentList] Enriching documents..."); // Log entry
    console.log("[DocumentList] Customer Map:", customerMap); // Log the map
    if (!documentsData || !customersData) {
       console.log("[DocumentList] Missing documentsData or customersData");
       return [];
    }

    return documentsData.map(doc => {
      const customerIdStr = doc.customer?.id?.toString(); // Safely get ID as string
      // Use the map for lookup
      const foundName = customerIdStr ? customerMap.get(customerIdStr) : undefined; 
      console.log(`[DocumentList] Doc ${doc.id}: Looking up Customer ID: ${customerIdStr}, Found Name: ${foundName}`); // Log lookup
      
      return {
        ...doc,
        customer: {
          id: doc.customer.id,
          name: foundName || "Unknown Customer" // Get name from map
        }
      }
    });
  // Remove customerMap from dependency array
  }, [documentsData, customersData]);

  // Loading state
  if (isLoading) {
    return <div className="flex justify-center p-8">Loading documents...</div>
  }

  // Error state
  if (isError) {
    return <div className="flex justify-center p-8 text-red-500">Error loading documents</div>
  }

  return (
    <div className="rounded-md border">
      <div className="p-4 flex justify-end">
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Document
        </Button>
      </div>

      <DocumentTable
        documents={enrichedDocuments || []}
        onView={handleView}
        onEdit={handleEdit}
        onCancelDocument={handleCancelDocument}
        onViewFlow={onDocumentSelect ? handleViewFlow : undefined}
        onSplitOrder={handleSplitOrder}
        onMergeOrders={handleMergeOrders}
        onCreateCollectiveInvoice={handleCreateCollectiveInvoice}
        onCreateDeliveryNote={handleCreateDeliveryNote}
        onCreateCreditNote={handleCreateCreditNote}
        onCancelOrder={handleCancelOrder}
        onExecuteAction={executeAction}
      />

      <DocumentModals
        selectedDocument={selectedDocument}
        showViewModal={showViewModal}
        setShowViewModal={setShowViewModal}
        showEditModal={showEditModal}
        setShowEditModal={setShowEditModal}
        showDeleteDialog={showCancelDialog} // Reusing the delete dialog for cancel
        setShowDeleteDialog={setShowCancelDialog}
        showCreateModal={showCreateModal}
        setShowCreateModal={setShowCreateModal}
        showCollectiveInvoiceView={showCollectiveInvoiceView}
        setShowCollectiveInvoiceView={setShowCollectiveInvoiceView}
        showOrderSplitView={showOrderSplitView}
        setShowOrderSplitView={setShowOrderSplitView}
        showOrderMergeView={showOrderMergeView}
        setShowOrderMergeView={setShowOrderMergeView}
        showCreditNoteCreateView={showCreditNoteCreateView}
        setShowCreditNoteCreateView={setShowCreditNoteCreateView}
        showDeliveryNoteCreateView={showDeliveryNoteCreateView}
        setShowDeliveryNoteCreateView={setShowDeliveryNoteCreateView}
        actionDialogOpen={actionDialogOpen}
        setActionDialogOpen={setActionDialogOpen}
        currentAction={currentAction}
        handleConfirm={handleConfirm}
      />

      {/* Order Cancel View */}
      {selectedDocument && (
        <Dialog open={showOrderCancelView} onOpenChange={setShowOrderCancelView}>
          <DialogContent className="max-w-[95vw] h-[95vh] max-h-[95vh] flex flex-col p-0">
            <OrderCancelView onClose={() => setShowOrderCancelView(false)} sourceDocumentId={selectedDocument.id} />
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}
