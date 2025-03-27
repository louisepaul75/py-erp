"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { X, ArrowLeft, ArrowRight, Pause, Layers, ImageIcon, Scale, User, Plus, Filter } from "lucide-react"
import { format, isToday } from "date-fns"
import { de } from "date-fns/locale"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { cn } from "@/lib/utils"
import type { Order, BinLocation, PickingMethod } from "@/types/types"
import { StorageLocationPopup } from "@/components/storage-location-popup"
import { ScanPopup } from "@/components/scan-popup"
import { TimerHeader } from "@/components/time-header"

interface MultiPickingProcessProps {
  onClose: () => void
  onComplete: () => void
  onInterrupt: () => void
  orders: Order[]
  uniqueDeliveryDates: string[]
  onDeliveryDateChange: (date: string | null) => void
  selectedDeliveryDate: string | null
  filteredOrders: Order[]
  pickingMethod?: PickingMethod
}

// Helper function to format the date for display
const formatDateForDisplay = (date: string): string => {
  const parsedDate = new Date(date)
  if (isToday(parsedDate)) {
    return `Heute, ${format(parsedDate, "dd.MM.yyyy", { locale: de })}`
  } else {
    return format(parsedDate, "dd.MM.yyyy", { locale: de })
  }
}

export function MultiPickingProcess({
  onClose,
  onComplete,
  onInterrupt,
  orders,
  uniqueDeliveryDates,
  onDeliveryDateChange,
  selectedDeliveryDate,
  filteredOrders,
  pickingMethod = "manual",
}: MultiPickingProcessProps) {
  const [currentOrderIndex, setCurrentOrderIndex] = useState(0)
  const [currentItemIndex, setCurrentItemIndex] = useState(0)
  const [scannedBin, setScannedBin] = useState("")
  const [currentBinIndex, setCurrentBinIndex] = useState(0)
  const [pickedQuantity, setPickedQuantity] = useState(0)
  const [showStorageLocationPopup, setShowStorageLocationPopup] = useState(false)
  const [showScanPopup, setShowScanPopup] = useState(false)
  const [isPickingCompleted, setIsPickingCompleted] = useState(false)
  const [previousDeliveryDate, setPreviousDeliveryDate] = useState<string | null>(null)
  const scanInputRef = useRef<HTMLInputElement>(null)
  const [showScanAfterStorage, setShowScanAfterStorage] = useState(false)
  const isScaleMethod = pickingMethod === "scale"

  // Wenn keine Liefertermine ausgewählt sind, standardmäßig "past" auswählen
  useEffect(() => {
    if (!selectedDeliveryDate && uniqueDeliveryDates.length > 0) {
      onDeliveryDateChange("past")
    }
  }, [selectedDeliveryDate, uniqueDeliveryDates, onDeliveryDateChange])

  // Effekt für Datum-Änderung
  useEffect(() => {
    // Nur ausführen, wenn es eine tatsächliche Änderung gibt und nicht beim ersten Laden
    if (previousDeliveryDate !== null && selectedDeliveryDate !== previousDeliveryDate) {
      // Zuerst das StorageLocationPopup anzeigen
      setShowStorageLocationPopup(true)
      // Markieren, dass das ScanPopup danach angezeigt werden soll
      setShowScanAfterStorage(true)
    }

    // Aktuelles Datum als vorheriges Datum speichern
    setPreviousDeliveryDate(selectedDeliveryDate)
  }, [selectedDeliveryDate, previousDeliveryDate])

  const currentOrder = filteredOrders[currentOrderIndex] || null
  const currentItem = currentOrder?.items[currentItemIndex] || null
  const totalOrders = filteredOrders.length
  const totalItems = currentOrder?.items.length || 0

  // Finde alle Schütten für das aktuelle Item
  const itemBinLocations =
    (currentItem?.binLocations
      .map((binId) => currentOrder?.binLocations.find((bin) => bin.id === binId))
      .filter(Boolean) as BinLocation[]) || []

  const currentBin = itemBinLocations[currentBinIndex] || null
  const hasMultipleBins = itemBinLocations.length > 1

  // Extrahiere Regal, Fach, Boden aus der Location (Format: "Regal/Fach/Boden")
  const [shelf, compartment, floor] = currentBin?.location?.split("/") || ["", "", ""]

  // Dummy-Werte für Gewicht (in der echten Anwendung würden diese aus der API kommen)
  const weightPerItem = 250 // g (vorher: 0.25 kg)

  useEffect(() => {
    // Fokus auf das Scan-Feld setzen
    if (scanInputRef.current) {
      scanInputRef.current.focus()
    }
  }, [currentOrderIndex, currentItemIndex, currentBinIndex])

  const handlePreviousItem = () => {
    if (currentItemIndex > 0) {
      setCurrentItemIndex(currentItemIndex - 1)
      setPickedQuantity(0)
      setCurrentBinIndex(0)
    } else if (currentOrderIndex > 0) {
      setCurrentOrderIndex(currentOrderIndex - 1)
      const prevOrder = filteredOrders[currentOrderIndex - 1]
      setCurrentItemIndex(prevOrder.items.length - 1)
      setPickedQuantity(0)
      setCurrentBinIndex(0)
    }
  }

  const handleNextItem = () => {
    if (currentItemIndex < totalItems - 1) {
      setCurrentItemIndex(currentItemIndex + 1)
      setPickedQuantity(0)
      setCurrentBinIndex(0)
    } else if (currentOrderIndex < totalOrders - 1) {
      setCurrentOrderIndex(currentOrderIndex + 1)
      setCurrentItemIndex(0)
      setPickedQuantity(0)
      setCurrentBinIndex(0)
    } else {
      // Wenn alle Items in allen Aufträgen gepickt wurden, zeige das Popup an
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
    if (currentItem && pickedQuantity < currentItem.quantityTotal) {
      setPickedQuantity(pickedQuantity + 1)
    }

    // Wenn alle Items gepickt wurden, automatisch zum nächsten Item wechseln
    if (currentItem && pickedQuantity + 1 >= currentItem.quantityTotal) {
      setTimeout(() => {
        handleNextItem()
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
    } else if (showScanAfterStorage) {
      // Wenn das ScanPopup nach dem StorageLocationPopup angezeigt werden soll
      setShowScanAfterStorage(false)
      // Kurze Verzögerung, damit das StorageLocationPopup vollständig geschlossen wird
      setTimeout(() => {
        setShowScanPopup(true)
      }, 100)
    }
    // Andernfalls wurde nur eine neue Schütte geholt, und wir machen mit dem Picking weiter
  }

  const handleScanSubmit = (binCode: string) => {
    console.log(`Scanning bin code: ${binCode} for multi-picking with date ${selectedDeliveryDate}`)
    setScannedBin(binCode)
    setShowScanPopup(false)
  }

  const handleSkipScan = () => {
    console.log(`Skipping scan for multi-picking with date ${selectedDeliveryDate}`)
    setShowScanPopup(false)
  }

  const handleTare = () => {
    console.log("Waage wird tariert...")
    // Hier würde die tatsächliche Tarierungs-Logik implementiert werden
  }

  // Wenn keine Aufträge gefiltert wurden, zeige eine Meldung an
  if (filteredOrders.length === 0) {
    return (
      <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
        <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Mehrfach-Picking</h2>
            <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
              <X className="h-4 w-4" />
              <span className="sr-only">Schließen</span>
            </Button>
          </div>

          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="font-medium">Liefertermin filtern:</span>
              <Select value={selectedDeliveryDate || "all"} onValueChange={onDeliveryDateChange}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Alle Liefertermine" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Liefertermine</SelectItem>
                  <SelectItem value="past">Vergangene Termine</SelectItem>
                  {uniqueDeliveryDates.map((date) => (
                    <SelectItem key={date} value={date}>
                      {formatDateForDisplay(date)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="text-center py-8">
              <p className="text-gray-500">Keine Aufträge für den ausgewählten Liefertermin gefunden.</p>
              <p className="text-gray-500 mt-2">
                Bitte wählen Sie einen anderen Liefertermin oder kehren Sie zur Übersicht zurück.
              </p>
            </div>

            <Button onClick={onClose} className="w-full">
              Zurück zur Übersicht
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg">
        {/* Header mit Kundeninformationen, Timer und Liefertermin-Filter */}
        <TimerHeader userName={currentOrder ? currentOrder.customerName.split(" ")[0] : "Mitarbeiter"} />
        <div className="p-3 flex items-center justify-between border-b bg-gray-50">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-gray-500" />
            <div className="text-sm">
              <span className="font-medium">
                {currentOrder ? `${currentOrder.customerNumber} ${currentOrder.customerName}` : ""}
              </span>
              <Badge variant="outline" className="ml-2 text-xs">
                Partner
              </Badge>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <Select value={selectedDeliveryDate || "all"} onValueChange={onDeliveryDateChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Alle Liefertermine" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle Liefertermine</SelectItem>
                <SelectItem value="past">Vergangene Termine</SelectItem>
                {uniqueDeliveryDates.map((date) => (
                  <SelectItem key={date} value={date}>
                    {formatDateForDisplay(date)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-4 w-4" />
            <span className="sr-only">Schließen</span>
          </Button>
        </div>

        {/* Fortschrittsanzeige für Mehrfach-Picking */}
        <div className="p-3 bg-gray-100 border-b">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">
              Auftrag {currentOrderIndex + 1} von {totalOrders}
            </span>
            <span className="text-sm font-medium">
              Artikel {currentItemIndex + 1} von {totalItems}
            </span>
          </div>
        </div>

        {/* Hauptinhalt */}
        <div className="p-4 space-y-4">
          {/* Lagerort */}
          <div className="bg-gray-50 rounded-lg border">
            <div className="p-2 border-b bg-gray-100">
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
          <div className="flex items-center bg-gray-50 p-3 rounded-lg border">
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
            <div className="bg-gray-50 rounded-lg border">
              <div className="p-2 border-b bg-gray-100">
                <h3 className="font-medium">Artikelbild</h3>
              </div>
              <div className="p-4">
                <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center max-h-[200px]">
                  <div className="flex flex-col items-center justify-center text-gray-400">
                    <ImageIcon className="h-16 w-16 mb-2" />
                    <span className="text-sm text-gray-400">Artikelbild {currentItem?.oldArticleNumber}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Artikelinformationen */}
            <div className="bg-gray-50 rounded-lg border">
              <div className="p-2 border-b bg-gray-100">
                <h3 className="font-medium">Artikelinformationen</h3>
              </div>
              <div className="p-4 space-y-3">
                <div>
                  <span className="text-sm text-gray-500">Bezeichnung</span>
                  <div className="font-medium">
                    {currentItem?.description || `Artikel ${currentItemIndex + 1} (${currentItem?.oldArticleNumber})`}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-gray-500">Artikelnummer (Alt)</span>
                    <div className="bg-white border rounded-full px-3 py-1 text-center mt-1">
                      {currentItem?.oldArticleNumber}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-500">Artikelnummer (Neu)</span>
                    <div className="bg-white border rounded-full px-3 py-1 text-center mt-1">
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
                  <div className="font-medium mt-1">
                    {currentItem ? weightPerItem * currentItem.quantityTotal : "0"} g
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation und Schüttenwechsel */}
          <div className="grid grid-cols-4 gap-2">
            <Button
              variant="outline"
              onClick={handlePreviousItem}
              disabled={currentOrderIndex === 0 && currentItemIndex === 0}
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
              disabled={currentOrderIndex === totalOrders - 1 && currentItemIndex === totalItems - 1}
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

      {/* Scan Popup */}
      {showScanPopup && (
        <ScanPopup
          title="Schütte scannen"
          onClose={() => setShowScanPopup(false)}
          onSubmit={handleScanSubmit}
          onSkip={handleSkipScan}
          skipButtonText="Keine Schütte"
          placeholder="Schüttencode scannen..."
          orderNumber={currentOrder?.orderNumber || ""}
          customerInfo={currentOrder ? `${currentOrder.customerNumber} ${currentOrder.customerName}` : ""}
          pickingMethod={pickingMethod}
          onTare={handleTare}
        />
      )}
    </div>
  )
}

