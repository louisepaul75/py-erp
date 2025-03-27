"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertCircle, ClipboardEdit } from "lucide-react"
import type { Item } from "@/lib/types"
import { Badge } from "@/components/ui/badge"

// Positive Korrekturgründe (Bestand höher als erwartet)
export type PositiveCorrectionReason =
  | "additional_found" // Zusätzliche Ware gefunden
  | "wrong_previous_booking" // Falsche frühere Buchung
  | "return_from_repair" // Rückkehr aus Reparatur
  | "other_positive" // Sonstiges (positiv)

// Negative Korrekturgründe (Bestand niedriger als erwartet)
export type NegativeCorrectionReason =
  | "loss" // Verlust / Schwund
  | "wrong_previous_booking" // Falsche frühere Buchung
  | "damage_paint_repairable" // Beschädigung – Bemalungsfehler (reparabel)
  | "damage_paint_irrepairable" // Beschädigung – Bemalungsfehler (irreparabel)
  | "damage_broken_repairable" // Beschädigung – Abgebrochene oder verbogene Teile (reparabel)
  | "damage_broken_irrepairable" // Beschädigung – Abgebrochene oder verbogene Teile (irreparabel)
  | "other_negative" // Sonstiges (negativ)

export type CorrectionReason = PositiveCorrectionReason | NegativeCorrectionReason

interface InventoryCorrectionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  item: Item | null
  onConfirm: (itemId: string, newQuantity: number, reason: CorrectionReason, note: string) => void
}

export function InventoryCorrectionDialog({ open, onOpenChange, item, onConfirm }: InventoryCorrectionDialogProps) {
  const [newQuantity, setNewQuantity] = useState<number | "">("")
  const [reason, setReason] = useState<CorrectionReason>("additional_found")
  const [note, setNote] = useState("")
  const [isPositiveCorrection, setIsPositiveCorrection] = useState(true)

  // Reset state when dialog opens or item changes
  useEffect(() => {
    if (open && item) {
      setNewQuantity(item.quantity)
      setNote("")

      // Standardmäßig positive Korrekturgründe anzeigen
      setIsPositiveCorrection(true)
      setReason("additional_found")
    }
  }, [open, item])

  // Wenn sich die Menge ändert, aktualisiere den Korrekturtyp
  useEffect(() => {
    if (item && typeof newQuantity === "number") {
      const isPositive = newQuantity > item.quantity
      setIsPositiveCorrection(isPositive)

      // Setze einen Standardgrund basierend auf dem Korrekturtyp
      if (isPositive && !isPositiveCorrectionReason(reason)) {
        setReason("additional_found")
      } else if (!isPositive && isPositiveCorrectionReason(reason)) {
        setReason("loss")
      }
    }
  }, [newQuantity, item, reason])

  if (!item) return null

  const handleConfirm = () => {
    if (typeof newQuantity === "number" && item) {
      onConfirm(item.id, newQuantity, reason, note)
      onOpenChange(false)
    }
  }

  // Hilfsfunktion zur Überprüfung, ob ein Grund ein positiver Korrekturgrund ist
  function isPositiveCorrectionReason(reason: CorrectionReason): reason is PositiveCorrectionReason {
    return ["additional_found", "wrong_previous_booking", "return_from_repair", "other_positive"].includes(reason)
  }

  const difference = typeof newQuantity === "number" ? Math.abs(newQuantity - item.quantity) : 0
  const isDifferent = typeof newQuantity === "number" && newQuantity !== item.quantity

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <ClipboardEdit className="h-5 w-5 mr-2" />
            Bestandskorrektur
          </DialogTitle>
        </DialogHeader>

        <div className="py-4 space-y-4">
          <div className="bg-muted/50 p-3 rounded-md">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-center">
              <Label className="sm:text-right text-sm text-muted-foreground">Artikel:</Label>
              <div className="sm:col-span-3 font-medium">
                {item.articleNew} <span className="text-muted-foreground">({item.articleOld})</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-center mt-1">
              <Label className="sm:text-right text-sm text-muted-foreground">Beschreibung:</Label>
              <div className="sm:col-span-3">{item.description}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:gap-2 items-center">
            <Label htmlFor="current-quantity" className="sm:text-right">
              Aktueller Bestand:
            </Label>
            <div className="sm:col-span-3">
              <Badge variant="outline" className="text-base px-3 py-1">
                {item.quantity} Stück
              </Badge>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:gap-2 items-center">
            <Label htmlFor="new-quantity" className="sm:text-right">
              Tatsächlicher Bestand:
            </Label>
            <div className="sm:col-span-3">
              <Input
                id="new-quantity"
                type="number"
                min="0"
                value={newQuantity}
                onChange={(e) => setNewQuantity(e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full"
              />
            </div>
          </div>

          {isDifferent && (
            <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 p-3 rounded-md flex items-start">
              <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-500 mr-2 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-amber-800 dark:text-amber-400 font-medium">
                  {isPositiveCorrection ? "Bestandserhöhung" : "Bestandsverringerung"} um {difference} Stück
                </p>
                <p className="text-amber-700 dark:text-amber-500 text-sm mt-1">
                  {isPositiveCorrection
                    ? `Der Bestand wird von ${item.quantity} auf ${newQuantity} erhöht.`
                    : `Der Bestand wird von ${item.quantity} auf ${newQuantity} verringert.`}
                </p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:gap-2 items-start">
            <Label htmlFor="reason" className="sm:text-right">
              Korrekturgrund:
            </Label>
            <div className="sm:col-span-3">
              <Select value={reason} onValueChange={(value) => setReason(value as CorrectionReason)}>
                <SelectTrigger id="reason">
                  <SelectValue placeholder="Grund auswählen" />
                </SelectTrigger>
                <SelectContent>
                  {isPositiveCorrection ? (
                    <>
                      <SelectItem value="additional_found">Zusätzliche Ware gefunden</SelectItem>
                      <SelectItem value="wrong_previous_booking">Falsche frühere Buchung</SelectItem>
                      <SelectItem value="return_from_repair">Rückkehr aus Reparatur</SelectItem>
                      <SelectItem value="other_positive">Sonstiges</SelectItem>
                    </>
                  ) : (
                    <>
                      <SelectItem value="loss">Verlust / Schwund</SelectItem>
                      <SelectItem value="wrong_previous_booking">Falsche frühere Buchung</SelectItem>
                      <SelectItem value="damage_paint_repairable">
                        Beschädigung – Bemalungsfehler (reparabel)
                      </SelectItem>
                      <SelectItem value="damage_paint_irrepairable">
                        Beschädigung – Bemalungsfehler (irreparabel)
                      </SelectItem>
                      <SelectItem value="damage_broken_repairable">
                        Beschädigung – Abgebrochene oder verbogene Teile (reparabel)
                      </SelectItem>
                      <SelectItem value="damage_broken_irrepairable">
                        Beschädigung – Abgebrochene oder verbogene Teile (irreparabel)
                      </SelectItem>
                      <SelectItem value="other_negative">Sonstiges</SelectItem>
                    </>
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:gap-2 items-start">
            <Label htmlFor="note" className="sm:text-right">
              Notiz (optional):
            </Label>
            <div className="sm:col-span-3">
              <Input
                id="note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Zusätzliche Informationen..."
                className="w-full"
              />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Abbrechen
          </Button>
          <Button onClick={handleConfirm} disabled={!isDifferent || typeof newQuantity !== "number"}>
            Bestand korrigieren
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

