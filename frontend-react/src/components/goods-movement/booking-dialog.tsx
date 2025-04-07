"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import type { Item, BookingItem } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Loader2 } from "lucide-react"
import { useMobile } from "@/hooks/use-mobile"
import {
  CorrectionDialog,
  type CorrectionType,
  type CorrectionAction,
  type CorrectionReason,
} from "./correction-dialog"
import { ItemDetails } from "./booking-dialog/item-details"
import { CompartmentsInput } from "./booking-dialog/compartments-input"
import { QuantitySelector } from "./booking-dialog/quantity-selector"
import { useToast } from "@/hooks/use-toast"
import { useHistory } from "./history-context"

interface BookingDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  items: Item[]
  onBookItems: (items: BookingItem[]) => void
  tolerancePercentage: number
}

// Mock data for bins (replace with actual data fetching)
const mockBins = [
  { id: "bin1", weight: 0.9 },
  { id: "bin2", weight: 1.0 },
  { id: "bin3", weight: 1.1 },
]

export function BookingDialog({
  open,
  onOpenChange,
  items,
  onBookItems,
  tolerancePercentage = 10, // Default-Wert, falls nicht übergeben
}: BookingDialogProps) {
  const isMobile = useMobile()
  const { toast } = useToast()
  const { addHistoryEntry } = useHistory()

  const [currentItemIndex, setCurrentItemIndex] = useState(0)
  const [compartment1, setCompartment1] = useState("")
  const [compartment2, setCompartment2] = useState("")
  const [compartment3, setCompartment3] = useState("")
  const [compartment4, setCompartment4] = useState("")
  const [quantityType, setQuantityType] = useState<"all" | "scale" | "manual">("all")
  const [manualQuantity, setManualQuantity] = useState<number | "">("")
  const [bookedItems, setBookedItems] = useState<BookingItem[]>([])
  const [compartment1InputRef, setCompartment1InputRef] = useState<HTMLInputElement | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  // States for weighing process
  const [scaleStep, setScaleStep] = useState<"scan" | "tara" | "weigh" | "result">("scan")
  const [binId, setBinId] = useState("")
  const [taraType, setTaraType] = useState<"manual" | "auto">("auto")
  const [manualTara, setManualTara] = useState<number | "">("")
  const [weighResult, setWeighResult] = useState<number | null>(null)
  const [calculatedQuantity, setCalculatedQuantity] = useState<number>(0)
  const [isMeasuringTara, setIsMeasuringTara] = useState(false)

  // States for correction dialog
  const [showCorrectionDialog, setShowCorrectionDialog] = useState(false)
  const [correctionType, setCorrectionType] = useState<CorrectionType>("excess")
  const [correctionQuantity, setCorrectionQuantity] = useState(0)

  const currentItem = items[currentItemIndex]

  // Reset state when dialog opens
  useEffect(() => {
    if (open) {
      setCurrentItemIndex(0)
      setCompartment1("")
      setCompartment2("")
      setCompartment3("")
      setCompartment4("")
      setQuantityType("all")
      setManualQuantity("")
      setBookedItems([])
      setIsProcessing(false)
      resetScaleProcess()
    }
  }, [open])

  // Focus compartment1 input when current item changes
  useEffect(() => {
    if (open && compartment1InputRef) {
      compartment1InputRef.focus()
    }
  }, [open, currentItemIndex, compartment1InputRef])

  const resetScaleProcess = () => {
    setScaleStep("scan")
    setBinId("")
    setTaraType("auto")
    setManualTara("")
    setWeighResult(null)
    setCalculatedQuantity(0)
    setIsMeasuringTara(false)
  }

  if (!currentItem) {
    return null
  }

  const getQuantityToBook = (): number => {
    switch (quantityType) {
      case "all":
        return currentItem.quantity
      case "scale":
        return calculatedQuantity > 0 ? Math.min(calculatedQuantity, currentItem.quantity) : 0
      case "manual":
        return typeof manualQuantity === "number" ? manualQuantity : 0
      default:
        return 0
    }
  }

  const checkForQuantityDiscrepancy = (quantityToBook: number): boolean => {
    // Prüfen, ob die Menge von der Systemmenge abweicht
    if (quantityToBook > currentItem.quantity) {
      // Überschuss: Benutzer will mehr entnehmen als im System vorhanden
      setCorrectionType("excess")
      setCorrectionQuantity(quantityToBook)
      setShowCorrectionDialog(true)
      return true
    } else if (quantityToBook < currentItem.quantity) {
      // Mangel: Benutzer will weniger entnehmen als im System vorhanden

      // Berechne die Differenz in Prozent
      const difference = currentItem.quantity - quantityToBook
      const differencePercentage = (difference / currentItem.quantity) * 100

      // Wenn die Differenz größer als der Toleranzwert ist, automatisch als Teilentnahme buchen
      if (differencePercentage > tolerancePercentage) {
        // Automatische Teilentnahme ohne Dialog
        toast({
          title: "Teilentnahme",
          description: `Automatische Teilentnahme: ${quantityToBook} von ${currentItem.quantity} Stück`,
        })

        // Direkt buchen ohne Dialog anzuzeigen
        processBooking(quantityToBook)
        return true
      } else {
        // Bei kleinen Differenzen (innerhalb der Toleranz) den Dialog anzeigen
        setCorrectionType("shortage")
        setCorrectionQuantity(quantityToBook)
        setShowCorrectionDialog(true)
        return true
      }
    }

    // Keine Abweichung
    return false
  }

  const handleConfirmBooking = async () => {
    const quantityToBook = getQuantityToBook()

    if (quantityToBook <= 0 || !compartment1) {
      return
    }

    // Prüfen, ob eine Bestandskorrektur erforderlich ist
    if (checkForQuantityDiscrepancy(quantityToBook)) {
      return // Dialog wird angezeigt oder automatisch gebucht, Funktion hier beenden
    }

    // Normale Buchung ohne Korrektur
    await processBooking(quantityToBook)
  }

  const handleCorrectionConfirm = async (action: CorrectionAction, reason?: CorrectionReason, note?: string) => {
    const quantityToBook = correctionQuantity

    if (correctionType === "excess") {
      if (action === "adjust") {
        // Bestandskorrektur: Bestand erhöhen und dann buchen
        console.log(
          `Bestandskorrektur: +${quantityToBook - currentItem.quantity} wegen ${reason}. Notiz: ${note || "keine"}`,
        )

        // Erstelle ein BookingItem mit Korrekturinformationen
        const newBookingItem: BookingItem = {
          id: `${currentItem.id}-${Date.now()}`,
          articleOld: currentItem.articleOld,
          articleNew: currentItem.articleNew,
          description: currentItem.description,
          quantity: quantityToBook,
          boxNumber: currentItem.boxNumber,
          targetSlot: compartment1,
          compartments: [
            compartment1,
            compartment2 ? compartment2 : null,
            compartment3 ? compartment3 : null,
            compartment4 ? compartment4 : null,
          ]
            .filter(Boolean)
            .join(", "),
          timestamp: new Date().toISOString(),
          correction: {
            type: "excess",
            reason: reason || "additional_found",
            amount: quantityToBook - currentItem.quantity,
            note: note,
          },
        }

        // Nach der Korrektur normal buchen
        await processBooking(quantityToBook, newBookingItem)
      }
    } else if (correctionType === "shortage") {
      if (action === "adjust") {
        // Bestandskorrektur: Bestand verringern und dann buchen
        console.log(
          `Bestandskorrektur: -${currentItem.quantity - quantityToBook} wegen ${reason}. Notiz: ${note || "keine"}`,
        )

        // Erstelle ein BookingItem mit Korrekturinformationen
        const newBookingItem: BookingItem = {
          id: `${currentItem.id}-${Date.now()}`,
          articleOld: currentItem.articleOld,
          articleNew: currentItem.articleNew,
          description: currentItem.description,
          quantity: quantityToBook,
          boxNumber: currentItem.boxNumber,
          targetSlot: compartment1,
          compartments: [
            compartment1,
            compartment2 ? compartment2 : null,
            compartment3 ? compartment3 : null,
            compartment4 ? compartment4 : null,
          ]
            .filter(Boolean)
            .join(", "),
          timestamp: new Date().toISOString(),
          correction: {
            type: "shortage",
            reason: reason || "loss",
            amount: currentItem.quantity - quantityToBook,
            note: note,
          },
        }

        // Nach der Korrektur normal buchen
        await processBooking(quantityToBook, newBookingItem)
      } else if (action === "partial") {
        // Teilentnahme: Normal buchen ohne Korrektur
        await processBooking(quantityToBook)
      }
    }
  }

  const processBooking = async (quantityToBook: number, customBookingItem?: BookingItem) => {
    setIsProcessing(true)

    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    const newBookedItem: BookingItem = customBookingItem || {
      id: `${currentItem.id}-${Date.now()}`,
      articleOld: currentItem.articleOld,
      articleNew: currentItem.articleNew,
      description: currentItem.description,
      quantity: quantityToBook,
      boxNumber: currentItem.boxNumber,
      targetSlot: compartment1,
      compartments: [
        compartment1,
        compartment2 ? compartment2 : null,
        compartment3 ? compartment3 : null,
        compartment4 ? compartment4 : null,
      ]
        .filter(Boolean)
        .join(", "),
      timestamp: new Date().toISOString(),
    }

    setBookedItems((prev) => [...prev, newBookedItem])
    setIsProcessing(false)

    // Move to next item or finish
    if (currentItemIndex < items.length - 1) {
      setCurrentItemIndex((prev) => prev + 1)
      setCompartment1("")
      setCompartment2("")
      setCompartment3("")
      setCompartment4("")
      setQuantityType("all")
      setManualQuantity("")
      resetScaleProcess()
    } else {
      // All items processed
      onBookItems([...bookedItems, newBookedItem])
    }
  }

  const handleCancel = () => {
    if (bookedItems.length > 0) {
      // If some items were already booked, submit those
      onBookItems(bookedItems)
    } else {
      // Otherwise just close the dialog
      onOpenChange(false)
    }
  }

  // Weighing process handlers
  const handleBinScan = () => {
    if (binId) {
      setScaleStep("tara")
    }
  }

  const handleTaraSelection = (type: "manual" | "auto") => {
    setTaraType(type)
  }

  const handleMeasureTara = () => {
    setIsMeasuringTara(true)

    // Simulate tara measurement
    setTimeout(() => {
      // Random tara weight between 0.8 and 1.5 kg
      const taraWeight = Math.random() * 0.7 + 0.8
      setManualTara(Number.parseFloat(taraWeight.toFixed(2)))
      setIsMeasuringTara(false)
    }, 1500)
  }

  const handleWeighing = () => {
    setScaleStep("weigh")

    // Simulate weighing process
    setTimeout(() => {
      // Mock weight between 0.5 and 5 kg
      const grossWeight = Math.random() * 4.5 + 0.5
      setWeighResult(grossWeight)

      // Calculate net weight and quantity
      let netWeight = grossWeight

      if (taraType === "auto") {
        const bin = mockBins.find((b) => b.id === binId)
        if (bin) {
          netWeight -= bin.weight
        }
      } else if (taraType === "manual" && typeof manualTara === "number") {
        netWeight -= manualTara
      }

      // Assumption: 1 piece weighs approx. 0.2 kg
      const estimatedQuantity = Math.max(0, Math.round(netWeight / 0.2))
      setCalculatedQuantity(estimatedQuantity)

      setScaleStep("result")
    }, 1500)
  }

  const handleQuantityAccept = () => {
    // Accept the calculated quantity and complete the weighing process
    setQuantityType("scale")
    // Visually complete the weighing process by returning to the main dialog
    setScaleStep("result")
  }

  const handleScaleBack = (step: "scan" | "tara") => {
    setScaleStep(step)
  }

  const progressPercentage = ((currentItemIndex + 1) / items.length) * 100

  // Prepare weighing props for the QuantitySelector component
  const weighingProps = {
    binId,
    setBinId,
    taraType,
    setTaraType,
    manualTara,
    setManualTara,
    weighResult,
    isMeasuringTara,
    handleBinScan,
    handleTaraSelection,
    handleMeasureTara,
    handleWeighing,
    handleQuantityAccept,
    handleScaleBack,
    resetScaleProcess,
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className={`${isMobile ? "w-[95vw] max-w-none" : "sm:max-w-xl"} overflow-y-auto max-h-[90vh]`}>
          <div className="absolute top-0 left-0 h-1 bg-primary" style={{ width: `${progressPercentage}%` }}></div>

          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span>
                Move Item ({currentItemIndex + 1}/{items.length})
              </span>
              <Badge variant="outline" className="ml-2">
                {currentItem.articleNew}
              </Badge>
            </DialogTitle>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Item Details */}
            <ItemDetails item={currentItem} />

            {/* Target Bin Input */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:gap-2 items-start">
              <Label className="sm:text-right">Target Bin:</Label>
              <div className="sm:col-span-3">
                <CompartmentsInput
                  compartment1={compartment1}
                  setCompartment1={setCompartment1}
                  compartment2={compartment2}
                  setCompartment2={setCompartment2}
                  compartment3={compartment3}
                  setCompartment3={setCompartment3}
                  compartment4={compartment4}
                  setCompartment4={setCompartment4}
                  setCompartment1InputRef={setCompartment1InputRef}
                />
              </div>
            </div>

            {/* Quantity Selection */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:gap-2 items-start">
              <Label className="sm:text-right pt-2">Quantity:</Label>
              <div className="sm:col-span-3">
                <QuantitySelector
                  quantityType={quantityType}
                  setQuantityType={setQuantityType}
                  manualQuantity={manualQuantity}
                  setManualQuantity={setManualQuantity}
                  itemQuantity={currentItem.quantity}
                  calculatedQuantity={calculatedQuantity}
                  scaleStep={scaleStep}
                  weighingProps={weighingProps}
                />
              </div>
            </div>
          </div>

          <DialogFooter className="flex flex-col sm:flex-row sm:justify-between gap-2">
            <Button variant="outline" onClick={handleCancel} className="w-full sm:w-auto">
              {bookedItems.length > 0 ? "Finish" : "Cancel"}
            </Button>
            <Button
              id="confirm-booking"
              onClick={handleConfirmBooking}
              disabled={
                !compartment1 ||
                getQuantityToBook() <= 0 ||
                isProcessing ||
                (quantityType === "scale" && calculatedQuantity === 0)
              }
              className="w-full sm:w-auto"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : currentItemIndex < items.length - 1 ? (
                <>
                  Book & Next
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              ) : (
                "Complete Booking"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Correction Dialog */}
      <CorrectionDialog
        open={showCorrectionDialog}
        onOpenChange={setShowCorrectionDialog}
        type={correctionType}
        systemQuantity={currentItem?.quantity || 0}
        enteredQuantity={correctionQuantity}
        onConfirm={handleCorrectionConfirm}
        tolerancePercentage={tolerancePercentage}
      />
    </>
  )
}
