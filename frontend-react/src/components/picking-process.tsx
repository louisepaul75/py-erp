"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { X, ArrowLeft, ArrowRight, Pause, Layers, ImageIcon, Scale, User, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { OrderItem, BinLocation, PickingMethod } from "@/types/types"
import { StorageLocationPopup } from "@/components/storage-location-popup"
import { TimerHeader } from "@/components/time-header"

interface PickingProcessProps {
  onClose: () => void
  onComplete: () => void
  onInterrupt: () => void
  orderNumber: string
  customerInfo: string
  customerType?: "private" | "partner"
  items: OrderItem[]
  binLocations: BinLocation[]
  currentItemIndex?: number
  initialBinLocation?: BinLocation
  picklistPosition?: number
  totalPicklistItems?: number
  pickingMethod?: PickingMethod
}

export function PickingProcess({
  onClose,
  onComplete,
  onInterrupt,
  orderNumber,
  customerInfo,
  customerType = "partner",
  items,
  binLocations,
  currentItemIndex = 0,
  initialBinLocation,
  picklistPosition = 2,
  totalPicklistItems = 5,
  pickingMethod = "manual",
}: PickingProcessProps) {
  const [currentIndex, setCurrentIndex] = useState(currentItemIndex)
  const [scannedBin, setScannedBin] = useState("")
  const [currentBinIndex, setCurrentBinIndex] = useState(0)
  const [pickedQuantity, setPickedQuantity] = useState(0)
  const [showStorageLocationPopup, setShowStorageLocationPopup] = useState(false)
  const [isPickingCompleted, setIsPickingCompleted] = useState(false)
  const scanInputRef = useRef<HTMLInputElement>(null)
  const modalRef = useRef<HTMLDivElement>(null);

  const isScaleMethod = pickingMethod === "scale"

  const currentItem = items[currentIndex]
  const totalItems = items.length

  // Finde alle Schütten für das aktuelle Item
  const itemBinLocations =
    (currentItem?.binLocations
      .map((binId) => binLocations.find((bin) => bin.id === binId))
      .filter(Boolean) as BinLocation[]) || []

  const currentBin = itemBinLocations[currentBinIndex] || initialBinLocation
  const hasMultipleBins = itemBinLocations.length > 1

  // Extrahiere Regal, Fach, Boden aus der Location (Format: "Regal/Fach/Boden")
  const [shelf, compartment, floor] = currentBin?.location.split("/") || ["", "", ""]

  // Dummy-Werte für Gewicht (in der echten Anwendung würden diese aus der API kommen)
  const weightPerItem = 250 // g (vorher: 0.25 kg)

  useEffect(() => {
    // Fokus auf das Scan-Feld setzen
    if (scanInputRef.current) {
      scanInputRef.current.focus()
    }

    if (modalRef.current) {
      modalRef.current.scrollTop = 0;
    }
  }, [currentIndex, currentBinIndex])

  const handlePreviousItem = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
      setPickedQuantity(0)
      setCurrentBinIndex(0)
    }
  }

  const handleNextItem = () => {
    if (currentIndex < items.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setPickedQuantity(0)
      setCurrentBinIndex(0)
    } else {
      // Wenn alle Items gepickt wurden, zeige das Popup an
      setIsPickingCompleted(true)
      setShowStorageLocationPopup(true)
    }
  }

  const handleSwitchBin = () => {
    if (hasMultipleBins) {
      setCurrentBinIndex((currentBinIndex + 1) % itemBinLocations.length)
    }
  }

  const handleNewBin = () => {
    // Zeige das Popup für eine neue Schütte an
    setIsPickingCompleted(false)
    setShowStorageLocationPopup(true)
  }

  const handleBinScan = (e: React.FormEvent) => {
    e.preventDefault()

    // Wenn kein Wert eingegeben wurde, trotzdem fortfahren
    if (!scannedBin.trim()) {
      console.log("Keine Schütte gescannt, trotzdem fortfahren")
      incrementPickedQuantity()
      return
    }

    // Überprüfe, ob die gescannte Schütte korrekt ist
    const isCorrectBin = currentBin && scannedBin === currentBin.binCode

    if (isCorrectBin) {
      // Hier würde die Logik für das erfolgreiche Scannen implementiert werden
      console.log(`Schütte ${scannedBin} erfolgreich gescannt`)
      incrementPickedQuantity()
      setScannedBin("")
    } else {
      // Hier würde die Fehlerbehandlung implementiert werden
      console.log(`Falsche Schütte gescannt: ${scannedBin}`)
      setScannedBin("")
    }
  }

  const incrementPickedQuantity = () => {
    if (pickedQuantity < currentItem.quantityTotal) {
      setPickedQuantity(pickedQuantity + 1)
    }

    // Wenn alle Items gepickt wurden, automatisch zum nächsten Item wechseln
    if (pickedQuantity + 1 >= currentItem.quantityTotal) {
      setTimeout(() => {
        if (currentIndex < items.length - 1) {
          handleNextItem()
        } else {
          // Wenn alle Items gepickt wurden, zeige das Popup an
          setIsPickingCompleted(true)
          setShowStorageLocationPopup(true)
        }
      }, 500)
    }
  }

  const handleStorageLocationConfirm = (storageLocation: string) => {
    // Hier würde die Logik für das Speichern des Lagerplatzes implementiert werden
    console.log("Schütte wird an folgenden Lagerplatz gestellt:", storageLocation)

    setShowStorageLocationPopup(false)

    if (isPickingCompleted) {
      // Wenn das Picking abgeschlossen ist, rufe die onComplete-Funktion auf
      onComplete()
    }
    // Andernfalls wurde nur eine neue Schütte geholt, und wir machen mit dem Picking weiter
  }

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div  
      ref={modalRef}
      className="w-full max-w-4xl bg-white dark:bg-background rounded-lg shadow-lg max-h-[96vh] overflow-y-auto">
        {/* Header mit Kundeninformationen und Timer */}
        <TimerHeader userName={customerInfo.split(" ")[0]} />
        <div className="p-3 flex items-center justify-between border-b bg-gray-50 dark:bg-background">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-gray-500" />
            <div className="text-sm">
              <span className="font-medium">{customerInfo}</span>
              <Badge variant="outline" className="ml-2 text-xs">
                {customerType === "private" ? "Privat" : "Partner"}
              </Badge>
            </div>
          </div>

          <div className="text-sm">
            <span className="text-gray-500">Pickliste:</span>
            <span className="font-medium ml-1">
              {picklistPosition}/{totalPicklistItems}
            </span>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-4 w-4" />
            <span className="sr-only">Schließen</span>
          </Button>
        </div>

        {/* Hauptinhalt */}
        <div className="p-4 space-y-4">
          {/* Lagerort */}
          <div className="bg-gray-50 dark:bg-background rounded-lg border">
            <div className="p-2 border-b bg-gray-100 dark:bg-background">
              <h3 className="font-medium">Lagerort</h3>
            </div>
            <div className="grid grid-cols-4 divide-x">
              <div className="p-3 flex flex-col items-center">
                <span className="text-sm text-gray-500">Regal</span>
                <span className="text-4xl font-bold">{shelf}</span>
              </div>
              <div className="p-3 flex flex-col items-center">
                <span className="text-sm text-gray-500">Fach</span>
                <span className="text-4xl font-bold">{compartment}</span>
              </div>
              <div className="p-3 flex flex-col items-center">
                <span className="text-sm text-gray-500">Boden</span>
                <span className="text-4xl font-bold">{floor}</span>
              </div>
              <div className="p-3 flex flex-col items-center">
                <span className="text-sm text-gray-500">Slot</span>
                <span className="text-4xl font-bold">-</span>
              </div>
            </div>
          </div>

          {/* Fortschritt unter dem Lagerort */}
          <div className="flex items-center bg-gray-50 dark:bg-background p-3 rounded-lg border">
            <Layers className="h-5 w-5 text-gray-500 mr-2" />
            <span className="font-medium">Stückzahl:</span>
            <div className="ml-auto flex items-center gap-1 text-xl font-bold">
              <span
                className={cn(
                  pickedQuantity === 0
                    ? "text-gray-700"
                    : pickedQuantity === currentItem?.quantityTotal
                      ? "text-green-600"
                      : "text-yellow-600",
                )}
              >
                {pickedQuantity}
              </span>
              <span className="text-gray-500">/</span>
              <span>{currentItem?.quantityTotal}</span>
            </div>
          </div>

          {/* Artikelbild und Informationen */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Artikelbild */}
            <div className="bg-gray-50 dark:bg-background rounded-lg border">
              <div className="p-2 border-b bg-gray-100 dark:bg-background">
                <h3 className="font-medium">Artikelbild</h3>
              </div>
              <div className="p-4">
                <div className="aspect-square bg-gray-100 dark:bg-background rounded-lg flex items-center justify-center max-h-[200px]">
                  <div className="flex flex-col items-center justify-center text-gray-400">
                    <ImageIcon className="h-16 w-16 mb-2" />
                    <span className="text-sm text-gray-400">Artikelbild {currentItem?.oldArticleNumber}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Artikelinformationen */}
            <div className="bg-gray-50 dark:bg-background rounded-lg border">
              <div className="p-2 border-b bg-gray-100 dark:bg-background">
                <h3 className="font-medium">Artikelinformationen</h3>
              </div>
              <div className="p-4 space-y-3">
                <div>
                  <span className="text-sm text-gray-500">Bezeichnung</span>
                  <div className="font-medium">
                    {currentItem?.description || `Artikel ${currentIndex + 1} (${currentItem?.oldArticleNumber})`}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-500">Artikelnummer (Alt)</span>
                    <div className="bg-white dark:bg-background border rounded-full px-3 py-1 text-center mt-1">
                      {currentItem?.oldArticleNumber}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">Artikelnummer (Neu)</span>
                    <div className="bg-white dark:bg-background border rounded-full px-3 py-1 text-center mt-1">
                      {currentItem?.newArticleNumber}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-500">Bestand</span>
                    <div className="font-medium mt-1">{currentItem?.quantityTotal} Stück</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">Gewicht/Stück</span>
                    <div className="font-medium mt-1 flex items-center gap-1">
                      <Scale className="h-4 w-4 text-gray-500" />
                      {weightPerItem} g
                    </div>
                  </div>
                </div>

                <div>
                  <span className="text-sm text-gray-500">Gesamtgewicht</span>
                  <div className="font-medium mt-1">{(weightPerItem * currentItem?.quantityTotal).toFixed(0)} g</div>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation und Schüttenwechsel - GEÄNDERT: Jetzt 4 Spalten statt 3 */}
          <div className="grid grid-cols-4 gap-2">
            <Button
              variant="outline"
              onClick={handlePreviousItem}
              disabled={currentIndex === 0}
              className="flex items-center justify-center gap-1 py-2 h-auto"
            >
              <ArrowLeft className="h-4 w-4" />
              Zurück
            </Button>

            {/* Nächste Schütte Button - immer anzeigen wenn mehrere Schütten vorhanden sind */}
            <Button
              variant="outline"
              onClick={handleSwitchBin}
              disabled={!hasMultipleBins}
              className="flex items-center justify-center py-2 h-auto"
            >
              Nächste Schütte {hasMultipleBins ? `(${currentBinIndex + 1}/${itemBinLocations.length})` : ""}
            </Button>

            {/* Neue Schütte Button - immer anzeigen */}
            <Button
              variant="outline"
              onClick={handleNewBin}
              className="flex items-center justify-center gap-1 py-2 h-auto"
            >
              <Plus className="h-4 w-4" />
              Neue Schütte
            </Button>

            <Button
              variant="outline"
              onClick={handleNextItem}
              disabled={currentIndex === items.length - 1}
              className="flex items-center justify-center gap-1 py-2 h-auto"
            >
              Weiter
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>

          {/* Scan-Bereich */}
          <div className="mt-4">
            <div className="text-center font-medium mb-2">Schütte scannen:</div>
            <form onSubmit={handleBinScan} className="space-y-4">
              <Input
                id="binScan"
                ref={scanInputRef}
                type="text"
                placeholder="Schüttencode scannen..."
                value={scannedBin}
                onChange={(e) => setScannedBin(e.target.value)}
                className="text-center py-6 text-lg border-2"
                autoComplete="off"
              />

              <Button type="submit" className="w-full py-4 h-auto text-lg bg-green-500 hover:bg-green-600 text-white">
                Bestätigen
              </Button>
            </form>
          </div>

          {/* Unterbrechen-Button */}
          <div className="flex justify-center mt-2">
            <Button variant="outline" onClick={onInterrupt} className="flex items-center gap-2">
              <Pause className="h-4 w-4" />
              Unterbrechen
            </Button>
          </div>
        </div>
      </div>

      {/* Storage Location Popup */}
      {showStorageLocationPopup && (
        <StorageLocationPopup
          onClose={() => setShowStorageLocationPopup(false)}
          onConfirm={handleStorageLocationConfirm}
          binCode={currentBin?.binCode}
          isCompleted={isPickingCompleted}
        />
      )}
    </div>
  )
}

