"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface StorageLocationPopupProps {
  onClose: () => void
  onConfirm: (storageLocation: string) => void
  binCode?: string
  isCompleted?: boolean
}

export function StorageLocationPopup({ onClose, onConfirm, binCode, isCompleted = false }: StorageLocationPopupProps) {
  const [storageLocation, setStorageLocation] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Fokus auf das Input-Feld setzen, wenn das Popup geöffnet wird
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (storageLocation.trim()) {
      onConfirm(storageLocation.trim())
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-xl font-bold">{isCompleted ? "Picking abgeschlossen" : "Neue Schütte"}</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-4 w-4" />
            <span className="sr-only">Schließen</span>
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <p className="text-center font-medium text-lg">
              Bitte geben Sie an, an welchen Lagerplatz Sie die Schütte stellen:
            </p>

            {binCode && (
              <div className="bg-gray-100 p-3 rounded-md text-center mb-4">
                <p className="text-sm text-gray-500">Schüttencode</p>
                <p className="text-xl font-bold">{binCode}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="storageLocation">Lagerplatz</Label>
                <Input
                  id="storageLocation"
                  ref={inputRef}
                  value={storageLocation}
                  onChange={(e) => setStorageLocation(e.target.value)}
                  placeholder="z.B. LA123"
                  required
                  className="text-center text-lg py-6"
                  pattern="LA\d+"
                  title="Bitte geben Sie eine gültige Lagerplatz-Nummer ein (Format: LA + Zahlen)"
                />
                <p className="text-xs text-gray-500 text-center">Format: LA + Nummer (z.B. LA123)</p>
              </div>

              <Button
                type="submit"
                className="w-full py-6 text-lg"
                disabled={!storageLocation.trim() || !/^LA\d+$/.test(storageLocation)}
              >
                {isCompleted ? "Abschließen" : "Bestätigen"}
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

