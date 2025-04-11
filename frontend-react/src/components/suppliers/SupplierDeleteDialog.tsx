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
import { Button } from "@/components/ui/button" // For potential styling consistency
import type { Supplier } from "@/types/supplier"

interface SupplierDeleteDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  supplier: Supplier | null // Supplier to delete (can be null if dialog closed)
  onConfirmDelete: () => void // Function to call when delete is confirmed
  isDeleting: boolean // Flag to disable buttons during deletion
}

/**
 * Confirmation dialog for deleting a supplier.
 */
export function SupplierDeleteDialog({
  open,
  onOpenChange,
  supplier,
  onConfirmDelete,
  isDeleting,
}: SupplierDeleteDialogProps) {

  // Don't render anything if the supplier is null (safer rendering)
  if (!supplier) {
    return null;
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. This will permanently delete the supplier
            <span className="font-semibold"> {supplier.name}</span>.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isDeleting} onClick={() => onOpenChange(false)}>
            Cancel
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirmDelete} // Call the passed confirmation handler
            disabled={isDeleting}
            // Apply destructive variant styling if available or use className
            // Assuming destructive variant exists for AlertDialogAction or Button
            // variant="destructive"
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isDeleting ? "Deleting..." : "Yes, delete supplier"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
} 