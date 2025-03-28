"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertCircle, CheckCircle, AlertTriangle } from "lucide-react"

export type CorrectionType =
  | "excess" // Mehr Artikel gefunden als im System
  | "shortage" // Weniger Artikel gefunden als im System

export type CorrectionAction =
  | "adjust" // Bestand anpassen (Inventurdifferenz)
  | "partial" // Teilentnahme (nur bei shortage)

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

interface CorrectionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  type: CorrectionType
  systemQuantity: number
  enteredQuantity: number
  onConfirm: (action: CorrectionAction, reason?: CorrectionReason, note?: string) => void
  tolerancePercentage: number
}

export function CorrectionDialog({
  open,
  onOpenChange,
  type,
  systemQuantity,
  enteredQuantity,
  onConfirm,
  tolerancePercentage,
}: CorrectionDialogProps) {
  // Bei Shortage standardmäßig "partial" auswählen, bei Excess "adjust"
  const [action, setAction] = useState<CorrectionAction>(type === "excess" ? "adjust" : "partial")
  const [reason, setReason] = useState<CorrectionReason>(type === "excess" ? "additional_found" : "loss")
  const [note, setNote] = useState("")

  // Bei jedem Öffnen des Dialogs die Standardwerte zurücksetzen
  useEffect(() => {
    if (open) {
      setAction(type === "excess" ? "adjust" : "partial")
      setReason(type === "excess" ? "additional_found" : "loss")
      setNote("")
    }
  }, [open, type])

  const difference = type === "excess" ? enteredQuantity - systemQuantity : systemQuantity - enteredQuantity
  const differencePercentage = (difference / systemQuantity) * 100

  // Bestimmen, ob die Differenz innerhalb der Toleranz liegt
  const isWithinTolerance = differencePercentage <= tolerancePercentage

  // Bei großen Differenzen (außerhalb der Toleranz) bei Mangel automatisch Teilentnahme vorschlagen
  const showAdjustOption = type === "excess" || isWithinTolerance

  const handleConfirm = () => {
    onConfirm(action, action === "adjust" ? reason : undefined, note.trim() || undefined)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            {type === "excess" ? (
              <>
                <AlertCircle className="h-5 w-5 text-orange-500 mr-2" />
                Bestandsüberschuss festgestellt
              </>
            ) : (
              <>
                <AlertTriangle className="h-5 w-5 text-amber-500 mr-2" />
                Bestandsdifferenz festgestellt
              </>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="py-4">
          {type === "excess" ? (
            <div className="space-y-4">
              <p>
                Du entnimmst <strong>{enteredQuantity}</strong>, das ist <strong>{difference}</strong> mehr als das
                Systembestand ({systemQuantity}).
              </p>
              <p>
                Hast du wirklich {difference === 1 ? "einen zusätzlichen Artikel" : `${difference} zusätzliche Artikel`}{" "}
                gefunden?
              </p>

              <RadioGroup value={action} onValueChange={(value) => setAction(value as CorrectionAction)}>
                <div className="flex items-center space-x-2 bg-background p-2 rounded-md border hover:bg-muted/50 transition-colors">
                  <RadioGroupItem value="adjust" id="adjust" />
                  <Label htmlFor="adjust" className="flex items-center cursor-pointer">
                    <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                    Ja, Bestand korrigieren
                  </Label>
                </div>
              </RadioGroup>

              {action === "adjust" && (
                <div className="space-y-3 pt-2">
                  <Label htmlFor="reason">Korrekturgrund</Label>
                  <Select value={reason} onValueChange={(value) => setReason(value as CorrectionReason)}>
                    <SelectTrigger id="reason">
                      <SelectValue placeholder="Grund auswählen" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="additional_found">Zusätzliche Ware gefunden</SelectItem>
                      <SelectItem value="wrong_previous_booking">Falsche frühere Buchung</SelectItem>
                      <SelectItem value="return_from_repair">Rückkehr aus Reparatur</SelectItem>
                      <SelectItem value="other_positive">Sonstiges</SelectItem>
                    </SelectContent>
                  </Select>

                  <Label htmlFor="note">Notiz (optional)</Label>
                  <Input
                    id="note"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    placeholder="Zusätzliche Informationen..."
                  />
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <p>
                Es sind laut System <strong>{systemQuantity}</strong> da. Du entnimmst{" "}
                <strong>{enteredQuantity}</strong>.
              </p>
              <p>Bitte wähle:</p>

              <RadioGroup value={action} onValueChange={(value) => setAction(value as CorrectionAction)}>
                {showAdjustOption && (
                  <div className="flex items-center space-x-2 bg-background p-2 rounded-md border hover:bg-muted/50 transition-colors">
                    <RadioGroupItem value="adjust" id="adjust" />
                    <Label htmlFor="adjust" className="flex items-center cursor-pointer">
                      <AlertTriangle className="h-4 w-4 mr-2 text-amber-500" />
                      Es {difference === 1 ? "fehlt" : "fehlen"} tatsächlich {difference}{" "}
                      {difference === 1 ? "Stück" : "Stücke"} (Verlust/Schwund)
                    </Label>
                  </div>
                )}

                <div className="flex items-center space-x-2 bg-background p-2 rounded-md border hover:bg-muted/50 transition-colors">
                  <RadioGroupItem value="partial" id="partial" />
                  <Label htmlFor="partial" className="flex items-center cursor-pointer">
                    <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                    Ich möchte nur {enteredQuantity} entnehmen, {difference} {difference === 1 ? "bleibt" : "bleiben"}{" "}
                    liegen
                  </Label>
                </div>
              </RadioGroup>

              {action === "adjust" && (
                <div className="space-y-3 pt-2">
                  <Label htmlFor="reason">Korrekturgrund</Label>
                  <Select value={reason} onValueChange={(value) => setReason(value as CorrectionReason)}>
                    <SelectTrigger id="reason">
                      <SelectValue placeholder="Grund auswählen" />
                    </SelectTrigger>
                    <SelectContent>
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
                    </SelectContent>
                  </Select>

                  <Label htmlFor="note">Notiz (optional)</Label>
                  <Input
                    id="note"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    placeholder="Zusätzliche Informationen..."
                  />
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Abbrechen
          </Button>
          <Button onClick={handleConfirm}>Bestätigen</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

