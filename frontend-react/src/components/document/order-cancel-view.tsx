"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { useDocuments } from "@/hooks/document/use-documents"
import { useUpdateDocument } from "@/hooks/document/use-documents"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar, FileText, AlertTriangle } from "lucide-react"
import type { DocumentItem } from "@/types/document/document"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { cancellationReasons } from "@/lib/mock-data/mock-document-history-data"

/**
 * Props for the OrderCancelView component
 */
interface OrderCancelViewProps {
  onClose: () => void
  sourceDocumentId: string // Required: The order to cancel
}

/**
 * Interface for item selection
 */
interface CancelableItem extends DocumentItem {
  selected: boolean
  isCanceled: boolean
}

/**
 * OrderCancelView component that displays a view for canceling an order or specific items
 */
export function OrderCancelView({ onClose, sourceDocumentId }: OrderCancelViewProps) {
  const { toast } = useToast()
  const { data: documents } = useDocuments()
  const updateDocument = useUpdateDocument()

  // Get the source document
  const sourceDocument = documents?.find((doc) => doc.id === sourceDocumentId)

  // State for selected items
  const [items, setItems] = useState<CancelableItem[]>([])

  // State for cancel mode (full or partial)
  const [cancelMode, setCancelMode] = useState<"full" | "partial">("full")

  // State for cancel reason
  const [cancelReasonId, setCancelReasonId] = useState("")

  // State for cancel date
  const [cancelDate, setCancelDate] = useState(new Date().toISOString().split("T")[0])

  // Initialize items when source document changes
  useEffect(() => {
    if (sourceDocument) {
      const initialItems: CancelableItem[] = sourceDocument.items.map((item) => ({
        ...item,
        selected: false,
        isCanceled: item.status === "CANCELED", // Check if item is already canceled
      }))
      setItems(initialItems)
    }
  }, [sourceDocument])

  // Get selected items
  const selectedItems = items.filter((item) => item.selected && !item.isCanceled)

  // Calculate total amount for selected items
  const selectedAmount = selectedItems.reduce((total, item) => total + item.price * item.quantity, 0)

  // Toggle item selection
  const toggleItemSelection = (itemId: string) => {
    setItems(items.map((item) => (item.id === itemId ? { ...item, selected: !item.selected } : item)))
  }

  // Toggle all items
  const toggleAllItems = (value: boolean) => {
    setItems(items.map((item) => (item.isCanceled ? item : { ...item, selected: value })))
  }

  // Cancel order or selected items
  const cancelOrder = async () => {
    try {
      if (!sourceDocument) {
        toast({
          title: "Fehler",
          description: "Quelldokument nicht gefunden.",
          variant: "destructive",
        })
        return
      }

      if (cancelMode === "partial" && selectedItems.length === 0) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie mindestens eine Position aus.",
          variant: "destructive",
        })
        return
      }

      if (!cancelReasonId) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie einen Stornierungsgrund aus.",
          variant: "destructive",
        })
        return
      }

      const selectedReason = cancellationReasons.find((r) => r.id === cancelReasonId)
      const reasonText = selectedReason ? selectedReason.description : "Unbekannter Grund"

      if (cancelMode === "full") {
        // Cancel the entire order
        updateDocument.mutate(
          {
            id: sourceDocument.id,
            status: "CANCELED",
            notes: sourceDocument.notes
              ? `${sourceDocument.notes}\n\nStorniert am ${cancelDate}: ${reasonText}`
              : `Storniert am ${cancelDate}: ${reasonText}`,
          },
          {
            onSuccess: () => {
              toast({
                title: "Auftrag storniert",
                description: `Auftrag ${sourceDocument.number} wurde erfolgreich storniert.`,
              })
              onClose()
            },
          },
        )
      } else {
        // Cancel only selected items
        // In a real application, you would update the status of individual items
        // For this example, we'll just add a note about which items were canceled

        const updatedItems = items.map((item) => {
          if (item.selected && !item.isCanceled) {
            return {
              ...item,
              status: "CANCELED", // Add status to items
            }
          }
          return item
        })

        const canceledItemsText = selectedItems
          .map((item) => `${item.productId} - ${item.description} (${item.quantity} x ${item.price.toFixed(2)} €)`)
          .join("\n")

        updateDocument.mutate(
          {
            id: sourceDocument.id,
            items: updatedItems,
            notes: sourceDocument.notes
              ? `${sourceDocument.notes}\n\nTeilstornierung am ${cancelDate}: ${reasonText}\nStornierte Positionen:\n${canceledItemsText}`
              : `Teilstornierung am ${cancelDate}: ${reasonText}\nStornierte Positionen:\n${canceledItemsText}`,
          },
          {
            onSuccess: () => {
              toast({
                title: "Positionen storniert",
                description: `${selectedItems.length} Positionen in Auftrag ${sourceDocument.number} wurden erfolgreich storniert.`,
              })
              onClose()
            },
          },
        )
      }
    } catch (error) {
      toast({
        title: "Fehler",
        description: `Fehler bei der Stornierung: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`,
        variant: "destructive",
      })
    }
  }

  if (!sourceDocument) {
    return (
      <div className="flex flex-col h-full bg-gray-50 items-center justify-center">
        <div className="w-96 p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Fehler</h3>
          <p className="text-muted-foreground">Der ausgewählte Auftrag wurde nicht gefunden.</p>
          <Button className="w-full mt-4" onClick={onClose}>
            Schließen
          </Button>
        </div>
      </div>
    )
  }

  // Check if order is already canceled
  if (sourceDocument.status === "CANCELED") {
    return (
      <div className="flex flex-col h-full bg-gray-50 items-center justify-center">
        <div className="w-96 p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Auftrag bereits storniert</h3>
          <p className="text-muted-foreground">
            Der Auftrag {sourceDocument.number} wurde bereits storniert und kann nicht erneut storniert werden.
          </p>
          <Button className="w-full mt-4" onClick={onClose}>
            Schließen
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Auftrag stornieren</h2>
              <div className="flex items-center gap-4 mt-1">
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  Auftrag: {sourceDocument.number}
                </Badge>
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  Kunde: {sourceDocument.customer.name}
                </Badge>
                {cancelMode === "partial" && (
                  <Badge variant="outline" className="px-2 py-1 text-sm">
                    {selectedItems.length} von {items.filter((i) => !i.isCanceled).length} Positionen ausgewählt
                  </Badge>
                )}
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-500">
                {cancelMode === "full" ? "Gesamtbetrag" : "Stornierungsbetrag"}
              </div>
              <div className="text-3xl font-bold text-destructive">
                {cancelMode === "full" ? sourceDocument.amount.toFixed(2) : selectedAmount.toFixed(2)} €
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - Cancel options */}
        <div className="w-1/2 border-r bg-white overflow-auto">
          <div className="p-6">
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4">Stornierungsoptionen</h3>

              <Card className="mb-6">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium">Stornierungsart</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center space-x-2">
                      <input
                        type="radio"
                        id="full-cancel"
                        checked={cancelMode === "full"}
                        onChange={() => setCancelMode("full")}
                        className="h-4 w-4 text-primary"
                      />
                      <label htmlFor="full-cancel" className="text-sm font-medium">
                        Kompletten Auftrag stornieren
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="radio"
                        id="partial-cancel"
                        checked={cancelMode === "partial"}
                        onChange={() => setCancelMode("partial")}
                        className="h-4 w-4 text-primary"
                      />
                      <label htmlFor="partial-cancel" className="text-sm font-medium">
                        Einzelne Positionen stornieren
                      </label>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="mb-6">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-primary" />
                    Stornierungsdatum
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input type="date" value={cancelDate} onChange={(e) => setCancelDate(e.target.value)} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-primary" />
                    Stornierungsgrund
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Select value={cancelReasonId} onValueChange={setCancelReasonId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Stornierungsgrund auswählen" />
                    </SelectTrigger>
                    <SelectContent>
                      {cancellationReasons.map((reason) => (
                        <SelectItem key={reason.id} value={reason.id}>
                          {reason.description}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>
            </div>

            {cancelMode === "partial" && (
              <div className="mb-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-base">Positionen zum Stornieren auswählen</h4>
                  <div className="space-x-2">
                    <Button variant="outline" size="sm" onClick={() => toggleAllItems(true)}>
                      Alle auswählen
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => toggleAllItems(false)}>
                      Alle abwählen
                    </Button>
                  </div>
                </div>
                <Separator className="mb-4" />

                <div className="border rounded-md overflow-hidden">
                  <div className="max-h-[calc(95vh-450px)] overflow-y-auto">
                    <Table>
                      <TableHeader className="bg-muted">
                        <TableRow>
                          <TableHead className="w-[50px]"></TableHead>
                          <TableHead>Artikel-Nr.</TableHead>
                          <TableHead>Beschreibung</TableHead>
                          <TableHead className="text-right">Menge</TableHead>
                          <TableHead className="text-right">Preis</TableHead>
                          <TableHead className="text-right">Gesamt</TableHead>
                          <TableHead>Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {items.map((item) => (
                          <TableRow key={item.id} className={item.isCanceled ? "bg-muted/50" : ""}>
                            <TableCell className="p-2">
                              <Checkbox
                                checked={item.selected}
                                onCheckedChange={() => toggleItemSelection(item.id)}
                                disabled={item.isCanceled}
                              />
                            </TableCell>
                            <TableCell className="font-medium">{item.productId}</TableCell>
                            <TableCell>{item.description}</TableCell>
                            <TableCell className="text-right">{item.quantity}</TableCell>
                            <TableCell className="text-right">{item.price.toFixed(2)} €</TableCell>
                            <TableCell className="text-right">{(item.quantity * item.price).toFixed(2)} €</TableCell>
                            <TableCell>
                              {item.isCanceled && (
                                <Badge variant="outline" className="bg-red-100 text-red-800">
                                  Storniert
                                </Badge>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right panel - Order details */}
        <div className="w-1/2 bg-white overflow-auto">
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-6">Auftragsdetails</h3>

            <Card className="mb-6">
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-medium">Auftragsinformationen</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Auftragsnummer:</span> {sourceDocument.number}
                </div>
                <div>
                  <span className="font-medium">Datum:</span> {sourceDocument.date}
                </div>
                <div>
                  <span className="font-medium">Kunde:</span> {sourceDocument.customer.name}
                </div>
                <div>
                  <span className="font-medium">Status:</span> {sourceDocument.status}
                </div>
                <div className="col-span-2">
                  <span className="font-medium">Gesamtbetrag:</span> {sourceDocument.amount.toFixed(2)} €
                </div>
                {sourceDocument.notes && (
                  <div className="col-span-2">
                    <span className="font-medium">Notizen:</span> {sourceDocument.notes}
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="bg-amber-50 border border-amber-200 rounded-md p-4 mb-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-amber-800">Wichtiger Hinweis zur Stornierung</h4>
                  <p className="text-sm text-amber-700 mt-1">
                    Die Stornierung kann nicht rückgängig gemacht werden. Bitte stellen Sie sicher, dass Sie die
                    richtigen Positionen ausgewählt haben.
                  </p>
                  {cancelMode === "full" && (
                    <p className="text-sm text-amber-700 mt-2">
                      Sie sind dabei, den gesamten Auftrag zu stornieren. Alle zugehörigen Positionen werden als
                      storniert markiert.
                    </p>
                  )}
                </div>
              </div>
            </div>

            {cancelMode === "partial" && selectedItems.length > 0 && (
              <div className="mb-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-semibold text-base">Zu stornierende Positionen</h4>
                  <Badge variant="secondary">{selectedItems.length} Positionen</Badge>
                </div>
                <Separator className="mb-4" />

                <div className="border rounded-md overflow-hidden">
                  <div className="max-h-[calc(95vh-450px)] overflow-y-auto">
                    <Table>
                      <TableHeader className="bg-muted">
                        <TableRow>
                          <TableHead>Artikel-Nr.</TableHead>
                          <TableHead>Beschreibung</TableHead>
                          <TableHead className="text-right">Menge</TableHead>
                          <TableHead className="text-right">Preis</TableHead>
                          <TableHead className="text-right">Gesamt</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {selectedItems.map((item) => (
                          <TableRow key={item.id}>
                            <TableCell className="font-medium">{item.productId}</TableCell>
                            <TableCell>{item.description}</TableCell>
                            <TableCell className="text-right">{item.quantity}</TableCell>
                            <TableCell className="text-right">{item.price.toFixed(2)} €</TableCell>
                            <TableCell className="text-right">{(item.quantity * item.price).toFixed(2)} €</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  <div className="bg-muted p-3 flex justify-between items-center border-t">
                    <span className="font-semibold">Stornierungsbetrag:</span>
                    <span className="font-bold text-lg">{selectedAmount.toFixed(2)} €</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t shadow-sm p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Button variant="outline" size="lg" onClick={onClose}>
            Abbrechen
          </Button>
          <Button
            variant="destructive"
            size="lg"
            onClick={cancelOrder}
            disabled={
              (cancelMode === "partial" && selectedItems.length === 0) || !cancelReasonId || updateDocument.isPending
            }
            className="px-8"
          >
            {updateDocument.isPending
              ? "Wird storniert..."
              : cancelMode === "full"
                ? "Auftrag stornieren"
                : "Positionen stornieren"}
          </Button>
        </div>
      </div>
    </div>
  )
}
