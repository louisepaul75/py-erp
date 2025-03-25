"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { X, Barcode } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface ScannerInputDialogProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (scannerCode: string) => void
  title?: string
}

export default function ScannerInputDialog({
  isOpen,
  onClose,
  onSubmit,
  title = "Schütte mit Scanner platzieren",
}: ScannerInputDialogProps) {
  const [scannerCode, setScannerCode] = useState("")
  const [error, setError] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  // Focus the input field when the dialog opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
    }
  }, [isOpen])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!scannerCode.trim()) {
      setError("Bitte geben Sie einen Scanner-Code ein")
      return
    }

    // Validiere den Scanner-Code (z.B. muss mit SC beginnen)
    if (!scannerCode.trim().toUpperCase().startsWith("SC")) {
      setError("Der Scanner-Code muss mit SC beginnen")
      return
    }

    onSubmit(scannerCode.trim())
    setScannerCode("")
    setError("")
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-md translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">{title}</Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="scannerCode">Scanner-Code</Label>
              <div className="relative">
                <Input
                  id="scannerCode"
                  ref={inputRef}
                  value={scannerCode}
                  onChange={(e) => setScannerCode(e.target.value)}
                  placeholder="SC123456"
                  className={`pl-10 ${error ? "border-red-500" : ""}`}
                  autoFocus
                />
                <Barcode className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
              {error && <p className="text-red-500 text-sm">{error}</p>}
              <p className="text-sm text-gray-500">
                Scannen Sie den Barcode der Schütte oder geben Sie den Code manuell ein.
              </p>
            </div>

            <div className="pt-4 flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={onClose}>
                Abbrechen
              </Button>
              <Button type="submit">Bestätigen</Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

