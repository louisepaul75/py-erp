"use client"

import { useState } from "react"
import { X, Printer } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import type { ContainerItem } from "./warehouse-location-list"

interface PrintContainerDialogProps {
  isOpen: boolean
  onClose: () => void
  selectedContainers: ContainerItem[]
  selectedPrinter: string
  multiplier: number
}

export default function PrintContainerDialog({
  isOpen,
  onClose,
  selectedContainers,
  selectedPrinter,
  multiplier,
}: PrintContainerDialogProps) {
  const [isPrinting, setIsPrinting] = useState(false)

  const handlePrint = () => {
    if (!selectedPrinter) return

    setIsPrinting(true)

    // Simulate printing process
    setTimeout(() => {
      setIsPrinting(false)
      onClose()
      // In a real application, you would send the print job to the server here
    }, 1500)
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">Schütten Etiketten drucken</Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-4 space-y-4">
            <p className="text-sm text-gray-500">
              Sie haben {selectedContainers.length} Schütte{selectedContainers.length !== 1 ? "n" : ""} zum Drucken
              ausgewählt mit einem Multiplikator von {multiplier}.
            </p>

            <div className="max-h-40 overflow-y-auto border rounded-md p-2">
              <ul className="space-y-1">
                {selectedContainers.map((container) => (
                  <li key={container.id} className="text-sm">
                    {container.containerCode} - {container.type} - {container.description}
                  </li>
                ))}
              </ul>
            </div>

            <div className="space-y-2 pt-2">
              <label className="text-sm font-medium">Ausgewählter Drucker</label>
              <div className="p-2 border rounded-md bg-gray-50">{selectedPrinter}</div>
            </div>

            <div className="pt-4 flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              <Button onClick={handlePrint} disabled={isPrinting} className="flex items-center gap-2">
                {isPrinting ? (
                  <>Druckt...</>
                ) : (
                  <>
                    <Printer className="h-4 w-4" />
                    Drucken
                  </>
                )}
              </Button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

