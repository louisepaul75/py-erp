"use client"

import { X } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import type { WarehouseLocation } from "@/types/warehouse-types"

interface DeleteConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  location: WarehouseLocation
}

export default function DeleteConfirmDialog({ isOpen, onClose, onConfirm, location }: DeleteConfirmDialogProps) {
  // Safety check to prevent null reference errors
  if (!location) {
    return null
  }

  const canDelete = location.containerCount === 0

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">Lagerort löschen</Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-4 space-y-4">
            {canDelete ? (
              <>
                <p>
                  Sind Sie sicher, dass Sie den Lagerort <strong>{location.laNumber}</strong> löschen möchten?
                </p>
                <p className="text-sm text-gray-500">Diese Aktion kann nicht rückgängig gemacht werden.</p>
              </>
            ) : (
              <>
                <p className="text-red-500">
                  Der Lagerort <strong>{location.laNumber}</strong> kann nicht gelöscht werden, da er noch{" "}
                  {location.containerCount} Schütten enthält.
                </p>
                <p className="text-sm text-gray-500">Bitte entfernen Sie zuerst alle Schütten aus diesem Lagerort.</p>
              </>
            )}

            <div className="pt-4 flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              {canDelete && (
                <Button type="button" variant="destructive" onClick={onConfirm}>
                  Löschen
                </Button>
              )}
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

