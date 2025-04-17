"use client"

import type React from "react"

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { formatDate } from "@/lib/utils"
import { Phone, Plus, Trash2, AlertCircle } from "lucide-react"
import { fetchCustomerCallHistory, addCustomerCall, deleteCustomerCall } from "@/lib/api/customers"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Badge } from "@/components/ui/badge"
import type { CallHistoryEntry, CallDirection } from "@/lib/types"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

/**
 * Komponente zur Anzeige und Verwaltung der Telefonanruf-Historie eines Kunden
 */
export default function CustomerCallHistoryCard({
  customerId,
}: {
  customerId: string
}) {
  const [showCallDialog, setShowCallDialog] = useState(false)
  const [deleteCallId, setDeleteCallId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Fetch call history using TanStack Query
  const { data: callHistory, isLoading } = useQuery({
    queryKey: ["customerCallHistory", customerId],
    queryFn: () => fetchCustomerCallHistory(customerId),
  })

  // Mutation for adding a new call
  const addCallMutation = useMutation({
    mutationFn: (callData: Omit<CallHistoryEntry, "id" | "customerId" | "timestamp" | "user">) =>
      addCustomerCall(customerId, callData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customerCallHistory", customerId] })
      setShowCallDialog(false)
    },
  })

  // Mutation for deleting a call
  const deleteCallMutation = useMutation({
    mutationFn: (callId: string) => deleteCustomerCall(callId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customerCallHistory", customerId] })
      setDeleteCallId(null)
    },
  })

  const handleAddCall = () => {
    setShowCallDialog(true)
  }

  const handleSaveCall = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)

    const callData = {
      direction: formData.get("direction") as CallDirection,
      duration: Number.parseInt(formData.get("duration") as string, 10),
      notes: formData.get("notes") as string,
    }

    // Überprüfen, ob Notizen eingegeben wurden (verpflichtend)
    if (!callData.notes.trim()) {
      alert("Bitte geben Sie Notizen zum Telefonanruf ein.")
      return
    }

    addCallMutation.mutate(callData)
  }

  const handleDeleteCall = (callId: string) => {
    setDeleteCallId(callId)
  }

  const confirmDeleteCall = () => {
    if (deleteCallId) {
      deleteCallMutation.mutate(deleteCallId)
    }
  }

  // Formatieren der Anrufdauer
  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Phone className="h-5 w-5" />
            Telefonanruf-Historie
          </CardTitle>
          <Button variant="outline" size="sm" onClick={handleAddCall}>
            <Plus className="mr-2 h-4 w-4" />
            Anruf hinzufügen
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-4">Anrufhistorie wird geladen...</div>
          ) : !callHistory || callHistory.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              Keine Telefonanrufe für diesen Kunden gefunden.
            </div>
          ) : (
            <div className="space-y-4">
              {callHistory.map((call) => (
                <div key={call.id} className="flex items-start gap-4 rounded-lg border p-4">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={call.user.avatar} />
                    <AvatarFallback>
                      {call.user.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{call.user.name}</p>
                        <Badge variant={call.direction === "incoming" ? "secondary" : "outline"}>
                          {call.direction === "incoming" ? "Eingehend" : "Ausgehend"}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{formatDate(call.timestamp)}</p>
                    </div>
                    <div className="text-sm text-muted-foreground">Dauer: {formatDuration(call.duration)}</div>
                    <p className="text-sm mt-2">{call.notes}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive"
                    onClick={() => handleDeleteCall(call.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog zum Hinzufügen eines Telefonanrufs */}
      <Dialog open={showCallDialog} onOpenChange={setShowCallDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Telefonanruf hinzufügen</DialogTitle>
            <DialogDescription>Geben Sie die Details des Telefonanrufs ein.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSaveCall}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="direction" className="text-right">
                  Richtung
                </Label>
                <Select name="direction" defaultValue="outgoing">
                  <SelectTrigger className="col-span-3">
                    <SelectValue placeholder="Anrufrichtung auswählen" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="incoming">Eingehend</SelectItem>
                    <SelectItem value="outgoing">Ausgehend</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="duration" className="text-right">
                  Dauer (Sek.)
                </Label>
                <Input
                  id="duration"
                  name="duration"
                  type="number"
                  min="1"
                  defaultValue="60"
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="notes" className="text-right">
                  Notizen *
                </Label>
                <Textarea
                  id="notes"
                  name="notes"
                  className="col-span-3"
                  placeholder="Gesprächsnotizen (verpflichtend)"
                  rows={4}
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" disabled={addCallMutation.isPending}>
                {addCallMutation.isPending ? "Wird gespeichert..." : "Speichern"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete confirmation dialog */}
      <AlertDialog open={!!deleteCallId} onOpenChange={(open) => !open && setDeleteCallId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Telefonanruf löschen
            </AlertDialogTitle>
            <AlertDialogDescription>
              Sind Sie sicher, dass Sie diesen Telefonanruf löschen möchten? Diese Aktion kann nicht rückgängig gemacht
              werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDeleteCall}
              disabled={deleteCallMutation.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteCallMutation.isPending ? "Wird gelöscht..." : "Löschen"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
