"use client"

import type React from "react"

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertTriangle, UserX } from "lucide-react"
import { updateCustomer } from "@/lib/api/customers"
import { useToast } from "@/hooks/use-toast"
import { InactiveReason } from "@/lib/definitions"

// Vordefinierte Inaktivierungsgründe mit Labels
const INACTIVE_REASONS = [
  { value: InactiveReason.NoOrders, label: "Keine Bestellungen" },
  { value: InactiveReason.BadPayment, label: "Zahlungsprobleme" },
  { value: InactiveReason.CustomerRequest, label: "Auf Kundenwunsch" },
  { value: InactiveReason.Competitor, label: "Wechsel zu Konkurrenz" },
  { value: InactiveReason.OutOfBusiness, label: "Geschäftsaufgabe" },
  { value: InactiveReason.Other, label: "Sonstiger Grund" },
]

interface DeactivateCustomerDialogProps {
  customerId: string
  customerName: string
  isActive: boolean
  onSuccess?: () => void
  trigger?: React.ReactNode
}

export function DeactivateCustomerDialog({
  customerId,
  customerName,
  isActive,
  onSuccess,
  trigger,
}: DeactivateCustomerDialogProps) {
  const [open, setOpen] = useState(false)
  const [reasonType, setReasonType] = useState<InactiveReason | "">("")
  const [reasonDetails, setReasonDetails] = useState("")
  const queryClient = useQueryClient()
  const { toast } = useToast()

  // Mutation zum Aktualisieren des Kundenstatus
  const updateCustomerMutation = useMutation({
    mutationFn: (data: { isActive: boolean; inactiveReason?: InactiveReason; inactiveReasonDetails?: string }) =>
      updateCustomer(customerId, data),
    onSuccess: () => {
      // Invalidiere die Abfragen, um die Daten neu zu laden
      queryClient.invalidateQueries({ queryKey: ["customer", customerId] })
      queryClient.invalidateQueries({ queryKey: ["customers"] })

      // Zeige eine Erfolgsmeldung
      toast({
        title: isActive ? "Kunde deaktiviert" : "Kunde aktiviert",
        description: isActive ? "Der Kunde wurde erfolgreich deaktiviert." : "Der Kunde wurde erfolgreich aktiviert.",
      })

      // Schließe den Dialog
      setOpen(false)
      setReasonType("")
      setReasonDetails("")

      // Rufe die onSuccess-Callback-Funktion auf, falls vorhanden
      if (onSuccess) onSuccess()
    },
    onError: (error) => {
      // Zeige eine Fehlermeldung
      toast({
        title: "Fehler",
        description: `Beim ${isActive ? "Deaktivieren" : "Aktivieren"} des Kunden ist ein Fehler aufgetreten: ${error}`,
        variant: "destructive",
      })
    },
  })

  // Kunde aktivieren/deaktivieren
  const handleUpdateStatus = () => {
    if (isActive) {
      // Beim Deaktivieren müssen wir einen Grund angeben
      if (!reasonType) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie einen Grund für die Deaktivierung aus.",
          variant: "destructive",
        })
        return
      }

      // Wenn "Sonstiger Grund" ausgewählt wurde, muss ein Detail angegeben werden
      if (reasonType === InactiveReason.Other && !reasonDetails.trim()) {
        toast({
          title: "Fehler",
          description: "Bitte geben Sie Details zum Grund an.",
          variant: "destructive",
        })
        return
      }

      // Deaktiviere den Kunden mit Grund
      updateCustomerMutation.mutate({
        isActive: false,
        inactiveReason: reasonType,
        inactiveReasonDetails: reasonType === InactiveReason.Other ? reasonDetails : undefined,
      })
    } else {
      // Aktiviere den Kunden (ohne Grund)
      updateCustomerMutation.mutate({
        isActive: true,
        inactiveReason: undefined,
        inactiveReasonDetails: undefined,
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant={isActive ? "destructive" : "default"} className="gap-2">
            <UserX className="h-4 w-4" />
            {isActive ? "Kunde deaktivieren" : "Kunde aktivieren"}
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {isActive && <AlertTriangle className="h-5 w-5 text-destructive" />}
            {isActive ? "Kunde deaktivieren" : "Kunde aktivieren"}
          </DialogTitle>
          <DialogDescription>
            {isActive
              ? `Sie sind dabei, den Kunden "${customerName}" zu deaktivieren. Deaktivierte Kunden werden in Listen ausgegraut und können keine neuen Aufträge erhalten.`
              : `Sie sind dabei, den Kunden "${customerName}" zu aktivieren. Der Kunde wird wieder in allen Listen normal angezeigt und kann neue Aufträge erhalten.`}
          </DialogDescription>
        </DialogHeader>

        {isActive && (
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="reasonType">Grund für Deaktivierung</Label>
              <Select value={reasonType} onValueChange={(value: string) => setReasonType(value as InactiveReason)} required>
                <SelectTrigger id="reasonType">
                  <SelectValue placeholder="Grund auswählen" />
                </SelectTrigger>
                <SelectContent>
                  {INACTIVE_REASONS.map((reason) => (
                    <SelectItem key={reason.value} value={reason.value}>
                      {reason.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {reasonType === InactiveReason.Other && (
              <div className="space-y-2">
                <Label htmlFor="reasonDetails">Details zum Grund</Label>
                <Textarea
                  id="reasonDetails"
                  value={reasonDetails}
                  onChange={(e) => setReasonDetails(e.target.value)}
                  placeholder="Bitte geben Sie Details zum Grund an"
                  required
                />
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Abbrechen
          </Button>
          <Button
            variant={isActive ? "destructive" : "default"}
            onClick={handleUpdateStatus}
            disabled={updateCustomerMutation.isPending}
          >
            {updateCustomerMutation.isPending
              ? isActive
                ? "Wird deaktiviert..."
                : "Wird aktiviert..."
              : isActive
                ? "Deaktivieren"
                : "Aktivieren"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
