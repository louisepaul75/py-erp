"use client"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { useUpdateDocument } from "@/hooks/document/use-documents"
import type { Document } from "@/types/document/document"
import { useState } from "react"
import { Label } from "@/components/ui/label"
import { cancellationReasons } from "@/lib/mock-data/mock-document-history-data"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

/**
 * Props for the DocumentDeleteDialog component
 */
interface DocumentDeleteDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  document: Document
}

/**
 * DocumentDeleteDialog component that displays a confirmation dialog for canceling a document
 * (renamed from delete to cancel functionality)
 */
export function DocumentDeleteDialog({ open, onOpenChange, document }: DocumentDeleteDialogProps) {
  // Mutation for updating a document
  const updateDocument = useUpdateDocument()

  // Ändern Sie den Zustand für den Stornierungsgrund
  const [cancelReasonId, setCancelReasonId] = useState("")

  // Handle cancel confirmation
  const handleCancel = () => {
    if (!cancelReasonId) {
      return // Don't allow cancellation without a reason
    }

    const selectedReason = cancellationReasons.find((r) => r.id === cancelReasonId)
    const reasonText = selectedReason ? selectedReason.description : "Unbekannter Grund"

    updateDocument.mutate(
      {
        id: document.id,
        status: "CANCELED",
        notes: document.notes ? `${document.notes}\n\nStorniert: ${reasonText}` : `Storniert: ${reasonText}`,
      },
      {
        onSuccess: () => {
          onOpenChange(false)
          setCancelReasonId("")
        },
      },
    )
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Dokument stornieren</AlertDialogTitle>
          <AlertDialogDescription>
            Möchten Sie das Dokument <strong>{document.number}</strong> wirklich stornieren? Diese Aktion kann nicht
            rückgängig gemacht werden.
          </AlertDialogDescription>
        </AlertDialogHeader>

        {/* Ersetzen Sie die Textarea durch ein Select */}
        <div className="py-4">
          <Label htmlFor="cancelReason" className="mb-2 block">
            Stornierungsgrund (erforderlich)
          </Label>
          <Select value={cancelReasonId} onValueChange={setCancelReasonId}>
            <SelectTrigger id="cancelReason">
              <SelectValue placeholder="Stornierungsgrund auswählen" />
            </SelectTrigger>
            <SelectContent>
              {cancellationReasons.map((reason) => (
                <SelectItem key={reason.id} value={reason.id}>
                  {reason.description}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel>Abbrechen</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleCancel}
            className="bg-red-600 hover:bg-red-700"
            // Aktualisieren Sie die disabled-Bedingung im AlertDialogAction-Button
            disabled={!cancelReasonId || updateDocument.isPending}
          >
            {updateDocument.isPending ? "Wird storniert..." : "Stornieren"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
