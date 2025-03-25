"use client"

import { X, AlertTriangle } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import type { ContainerItem } from "@/types/warehouse-types"

interface RemoveContainerDialogProps {
  isOpen: boolean
  onClose: () => void
  container: ContainerItem
  onConfirm: () => void
}

export default function RemoveContainerDialog({ isOpen, onClose, container, onConfirm }: RemoveContainerDialogProps) {
  const isMultipleContainers = container.id === "multiple"

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Schütte entfernen
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-4 space-y-4">
            {isMultipleContainers ? (
              <p>
                Sind Sie sicher, dass Sie <strong>{container.containerCode}</strong> aus diesem Lagerort entfernen
                möchten?
              </p>
            ) : (
              <p>
                Sind Sie sicher, dass Sie die Schütte <strong>{container.containerCode}</strong> aus diesem Lagerort
                entfernen möchten?
              </p>
            )}
            <p className="text-sm text-gray-500">
              Die Schütte{isMultipleContainers ? "n werden" : " wird"} nicht gelöscht, sondern nur aus diesem Lagerort
              entfernt. Sie können die Schütte{isMultipleContainers ? "n" : ""} später wieder einem Lagerort zuweisen.
            </p>

            <div className="pt-4 flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              <Button type="button" onClick={onConfirm}>
                Entfernen
              </Button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

