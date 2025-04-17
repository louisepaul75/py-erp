"use client"

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { DocumentViewModal } from "@/components/document/document-view-modal"
import { DocumentEditModal } from "@/components/document/document-edit-modal"
import { DocumentDeleteDialog } from "@/components/document/document-delete-dialog"
import { DocumentCreateModal } from "@/components/document/document-create-modal"
import { CollectiveInvoiceHierarchicalView } from "@/components/document/collective-invoice-hierarchical-view"
import { OrderSplitView } from "@/components/document/order-split-view"
import { OrderMergeView } from "@/components/document/order-merge-view"
import { CreditNoteCreateView } from "@/components/document/credit-note-create-view"
import { DeliveryNoteCreateView } from "@/components/document/delivery-note-create-view"
import type { Document } from "@/types/document/document"

/**
 * Props for the DocumentModals component
 */
interface DocumentModalsProps {
  selectedDocument: Document | null
  showViewModal: boolean
  setShowViewModal: (show: boolean) => void
  showEditModal: boolean
  setShowEditModal: (show: boolean) => void
  showDeleteDialog: boolean
  setShowDeleteDialog: (show: boolean) => void
  showCreateModal: boolean
  setShowCreateModal: (show: boolean) => void
  showCollectiveInvoiceView: boolean
  setShowCollectiveInvoiceView: (show: boolean) => void
  showOrderSplitView: boolean
  setShowOrderSplitView: (show: boolean) => void
  showOrderMergeView: boolean
  setShowOrderMergeView: (show: boolean) => void
  showCreditNoteCreateView: boolean
  setShowCreditNoteCreateView: (show: boolean) => void
  showDeliveryNoteCreateView: boolean
  setShowDeliveryNoteCreateView: (show: boolean) => void
  actionDialogOpen: boolean
  setActionDialogOpen: (open: boolean) => void
  currentAction: {
    title: string
    description: string
    action: () => Promise<void>
  } | null
  handleConfirm: () => Promise<void>
}

/**
 * DocumentModals component that displays all modals for document actions
 */
export function DocumentModals({
  selectedDocument,
  showViewModal,
  setShowViewModal,
  showEditModal,
  setShowEditModal,
  showDeleteDialog,
  setShowDeleteDialog,
  showCreateModal,
  setShowCreateModal,
  showCollectiveInvoiceView,
  setShowCollectiveInvoiceView,
  showOrderSplitView,
  setShowOrderSplitView,
  showOrderMergeView,
  setShowOrderMergeView,
  showCreditNoteCreateView,
  setShowCreditNoteCreateView,
  showDeliveryNoteCreateView,
  setShowDeliveryNoteCreateView,
  actionDialogOpen,
  setActionDialogOpen,
  currentAction,
  handleConfirm,
}: DocumentModalsProps) {
  return (
    <>
      {/* Modals for viewing, editing, and canceling documents */}
      {selectedDocument && (
        <>
          <DocumentViewModal open={showViewModal} onOpenChange={setShowViewModal} document={selectedDocument} />
          <DocumentEditModal open={showEditModal} onOpenChange={setShowEditModal} document={selectedDocument} />
          <DocumentDeleteDialog
            open={showDeleteDialog}
            onOpenChange={setShowDeleteDialog}
            document={selectedDocument}
          />
        </>
      )}

      {/* Create Document Modal */}
      <DocumentCreateModal
        open={showCreateModal}
        onOpenChange={(open) => {
          setShowCreateModal(open)
        }}
      />

      {/* Collective Invoice Hierarchical View */}
      {selectedDocument && (
        <Dialog open={showCollectiveInvoiceView} onOpenChange={setShowCollectiveInvoiceView}>
          <DialogContent className="max-w-[95vw] h-[95vh] max-h-[95vh] flex flex-col p-0">
            <CollectiveInvoiceHierarchicalView
              onClose={() => setShowCollectiveInvoiceView(false)}
              sourceDocumentId={selectedDocument.id}
            />
          </DialogContent>
        </Dialog>
      )}

      {/* Order Split View */}
      {selectedDocument && (
        <Dialog open={showOrderSplitView} onOpenChange={setShowOrderSplitView}>
          <DialogContent className="max-w-[95vw] h-[95vh] max-h-[95vh] flex flex-col p-0">
            <OrderSplitView onClose={() => setShowOrderSplitView(false)} sourceDocumentId={selectedDocument.id} />
          </DialogContent>
        </Dialog>
      )}

      {/* Order Merge View */}
      {selectedDocument && (
        <Dialog open={showOrderMergeView} onOpenChange={setShowOrderMergeView}>
          <DialogContent className="max-w-[95vw] h-[95vh] max-h-[95vh] flex flex-col p-0">
            <OrderMergeView onClose={() => setShowOrderMergeView(false)} sourceDocumentId={selectedDocument.id} />
          </DialogContent>
        </Dialog>
      )}

      {/* Credit Note Create View */}
      {selectedDocument && (
        <Dialog open={showCreditNoteCreateView} onOpenChange={setShowCreditNoteCreateView}>
          <DialogContent className="max-w-[95vw] h-[95vh] max-h-[95vh] flex flex-col p-0">
            <CreditNoteCreateView
              onClose={() => setShowCreditNoteCreateView(false)}
              sourceDocumentId={selectedDocument.id}
            />
          </DialogContent>
        </Dialog>
      )}

      {/* Delivery Note Create View */}
      {selectedDocument && (
        <Dialog open={showDeliveryNoteCreateView} onOpenChange={setShowDeliveryNoteCreateView}>
          <DialogContent className="max-w-[95vw] h-[95vh] max-h-[95vh] flex flex-col p-0">
            <DeliveryNoteCreateView
              onClose={() => setShowDeliveryNoteCreateView(false)}
              sourceDocumentId={selectedDocument.id}
            />
          </DialogContent>
        </Dialog>
      )}

      {/* Confirmation Dialog for Actions */}
      <Dialog open={actionDialogOpen} onOpenChange={setActionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{currentAction?.title}</DialogTitle>
            <DialogDescription>{currentAction?.description}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setActionDialogOpen(false)}>
              Abbrechen
            </Button>
            <Button onClick={handleConfirm}>Bestätigen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
