"use client"

import * as Dialog from "@radix-ui/react-dialog"
import { AlertTriangle, X } from "lucide-react" 
import { Button } from "@/components/ui/button"
import { Product } from "../types/product"

interface DeleteConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  product: Product | null
}

export default function DeleteConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  product,
}: DeleteConfirmDialogProps) {
  if (!product) return null

  const handleConfirm = () => {
    onConfirm()
    onClose()
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white dark:bg-slate-800 p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b dark:border-slate-700">
            <Dialog.Title className="text-xl font-semibold flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Produkt löschen
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-4 space-y-4">
            <p>
              Sind Sie sicher, dass Sie das Produkt <strong>{product.name}</strong> (SKU: {product.sku}) löschen möchten? 
              Diese Aktion kann nicht rückgängig gemacht werden.
            </p>

            <div className="pt-4 flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              <Button type="button" variant="destructive" onClick={handleConfirm}>
                Löschen
              </Button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
} 