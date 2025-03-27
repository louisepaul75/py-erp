"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { X, Scale } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface ScanPopupProps {
  title: string
  onClose: () => void
  onSubmit: (value: string) => void
  onSkip?: () => void
  skipButtonText?: string
  placeholder?: string
  orderNumber?: string
  customerInfo?: string
  pickingMethod?: "manual" | "scale"
  onTare?: () => void
}

export function ScanPopup({
  title,
  onClose,
  onSubmit,
  onSkip,
  skipButtonText = "Keine Schütte",
  placeholder = "Schüttencode scannen...",
  orderNumber = "",
  customerInfo = "",
  pickingMethod = "manual",
  onTare,
}: ScanPopupProps) {
  const [value, setValue] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)
  const isScaleMethod = pickingMethod === "scale"

  useEffect(() => {
    // Fokus auf das Input-Feld setzen, wenn das Popup geöffnet wird
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim()) {
      onSubmit(value.trim())
    }
  }

  const handleTare = () => {
    if (onTare) {
      onTare()
    } else {
      console.log("Waage tarieren")
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div className="w-full max-w-md bg-white dark:bg-background rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">{title}</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-5 w-5" />
            <span className="sr-only">Schließen</span>
          </Button>
        </div>

        {/* Auftragsinformationen */}
        <div className="bg-gray-100 dark:bg-background p-3 mb-4 rounded-md">
          <div className="flex flex-wrap justify-between mb-2">
            {orderNumber && <div className="font-medium">Auftrags-Nr.: {orderNumber}</div>}
            {customerInfo && <div className="font-medium">Kunde: {customerInfo}</div>}
          </div>

          {isScaleMethod && (
            <ol className="list-decimal pl-5 text-sm space-y-2 mt-4">
              <li>
                Bitte Tarieren Sie die Waage in dem Sie eine leere Schütte auf die Waage Stellen. Dann den Button "Waage
                Tarieren" Drücken
              </li>
              <li>Scannen Sie den Barcode der Schütte.</li>
            </ol>
          )}
        </div>

        {/* Tara-Button für Waage-Picking */}
        {isScaleMethod && (
          <div className="mb-4">
            <Button type="button" onClick={handleTare} className="w-full flex items-center justify-center gap-2">
              <Scale className="h-4 w-4" />
              Waage Tarieren
            </Button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="barcode" className="font-medium">
              Schütten Barcode:
            </label>
            <Input
              id="barcode"
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="w-full text-lg py-6"
              autoComplete="off"
            />
          </div>

          <div className="flex justify-between">
            {onSkip && (
              <Button type="button" variant="outline" onClick={onSkip} className="px-6 py-2 text-base">
                {skipButtonText}
              </Button>
            )}
            <Button
              type="submit"
              disabled={!value.trim()}
              className="px-6 py-2 text-base bg-gray-500 hover:bg-gray-600 ml-auto"
            >
              Bestätigen
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

