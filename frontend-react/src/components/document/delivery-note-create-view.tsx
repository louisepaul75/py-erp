"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { useDocuments } from "@/hooks/document/use-documents"
import { useCreateDocument } from "@/hooks/document/use-documents"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar, FileText, User, ArrowRightLeft } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { DocumentItem } from "@/types/document/document"

/**
 * Props for the DeliveryNoteCreateView component
 */
interface DeliveryNoteCreateViewProps {
  onClose: () => void
  sourceDocumentId: string // Required: The order to create a delivery note from
}

/**
 * Interface for item selection with quantity
 */
interface SelectedItem extends DocumentItem {
  selected: boolean
  deliveryQuantity: number
}

/**
 * DeliveryNoteCreateView component that displays a view for creating a delivery note from an order
 * It allows selecting specific items to include in the delivery note
 */
export function DeliveryNoteCreateView({ onClose, sourceDocumentId }: DeliveryNoteCreateViewProps) {
  const { toast } = useToast()
  const { data: documents } = useDocuments()
  const createDocument = useCreateDocument()

  // Get the source document
  const sourceDocument = documents?.find((doc) => doc.id === sourceDocumentId)

  // State for selected items with quantities
  const [items, setItems] = useState<SelectedItem[]>([])

  // State for new delivery note details
  const [deliveryNoteNumber, setDeliveryNoteNumber] = useState("")
  const [deliveryNoteDate, setDeliveryNoteDate] = useState(new Date().toISOString().split("T")[0])
  const [deliveryNoteStatus, setDeliveryNoteStatus] = useState("OPEN")
  const [deliveryNoteNotes, setDeliveryNoteNotes] = useState("")

  // Initialize items when source document changes
  useEffect(() => {
    if (sourceDocument) {
      const initialItems: SelectedItem[] = sourceDocument.items.map((item: DocumentItem) => ({
        ...item,
        selected: true, // Default to selected
        deliveryQuantity: item.quantity, // Default to full quantity
      }))
      setItems(initialItems)
    }
  }, [sourceDocument])

  // Get selected items
  const selectedItems = items.filter((item) => item.selected)

  // Calculate total amount for selected items
  const selectedAmount = selectedItems.reduce((total, item) => total + item.price * item.deliveryQuantity, 0)

  // Toggle item selection
  const toggleItemSelection = (itemId: string) => {
    setItems(items.map((item) => (item.id === itemId ? { ...item, selected: !item.selected } : item)))
  }

  // Update item delivery quantity
  const updateItemQuantity = (itemId: string, quantity: number) => {
    setItems(
      items.map((item) => {
        if (item.id === itemId) {
          // Ensure quantity is not greater than original and not less than 1
          const validQuantity = Math.min(Math.max(1, quantity), item.quantity)
          return { ...item, deliveryQuantity: validQuantity }
        }
        return item
      }),
    )
  }

  // Toggle all items
  const toggleAllItems = (value: boolean) => {
    setItems(items.map((item) => ({ ...item, selected: value })))
  }

  // Create delivery note
  const createDeliveryNote = async () => {
    try {
      if (!sourceDocument) {
        toast({
          title: "Fehler",
          description: "Quelldokument nicht gefunden.",
          variant: "destructive",
        })
        return
      }

      if (selectedItems.length === 0) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie mindestens eine Position aus.",
          variant: "destructive",
        })
        return
      }

      if (!deliveryNoteNumber) {
        toast({
          title: "Fehler",
          description: "Bitte geben Sie eine Lieferscheinnummer ein.",
          variant: "destructive",
        })
        return
      }

      // Create delivery note with selected items
      const deliveryItems = selectedItems.map(({ selected, deliveryQuantity, ...item }) => ({
        ...item,
        quantity: deliveryQuantity, // Use the delivery quantity
      }))

      createDocument.mutate(
        {
          type: "DELIVERY",
          number: deliveryNoteNumber,
          customer: sourceDocument.customer,
          date: deliveryNoteDate,
          status: deliveryNoteStatus,
          notes: deliveryNoteNotes || `Lieferschein erstellt für Auftrag ${sourceDocument.number}`,
          items: deliveryItems,
          amount: selectedAmount,
        },
        {
          onSuccess: () => {
            toast({
              title: "Lieferschein erstellt",
              description: `Lieferschein ${deliveryNoteNumber} wurde erfolgreich erstellt.`,
            })
            onClose()
          },
        },
      )
    } catch (error) {
      toast({
        title: "Fehler",
        description: `Fehler beim Erstellen des Lieferscheins: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`,
        variant: "destructive",
      })
    }
  }

  // Get status options
  const statusOptions = [
    { value: "OPEN", label: "Offen" },
    { value: "SHIPPED", label: "Versendet" },
    { value: "DELIVERED", label: "Geliefert" },
    { value: "CANCELED", label: "Storniert" },
  ]

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

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Lieferschein erstellen</h2>
              <div className="flex items-center gap-4 mt-1">
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  Auftrag: {sourceDocument.number}
                </Badge>
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  Kunde: {sourceDocument.customer.name}
                </Badge>
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  {selectedItems.length} von {items.length} Positionen ausgewählt
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-500">Lieferwert</div>
              <div className="text-3xl font-bold text-primary">{selectedAmount.toFixed(2)} €</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - Source order items */}
        <div className="w-1/2 border-r bg-white overflow-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Positionen des Quellauftrags</h3>
              <div className="space-x-2">
                <Button variant="outline" size="sm" onClick={() => toggleAllItems(true)}>
                  Alle auswählen
                </Button>
                <Button variant="outline" size="sm" onClick={() => toggleAllItems(false)}>
                  Alle abwählen
                </Button>
              </div>
            </div>

            <div className="mb-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium">Auftragsdetails</CardTitle>
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
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-base">Positionen für Lieferschein auswählen</h4>
                <Badge variant="secondary">
                  {selectedItems.length} von {items.length} ausgewählt
                </Badge>
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
                        <TableHead className="text-right">Orig. Menge</TableHead>
                        <TableHead className="text-right">Liefer-Menge</TableHead>
                        <TableHead className="text-right">Preis</TableHead>
                        <TableHead className="text-right">Gesamt</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {items.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell className="p-2">
                            <Checkbox checked={item.selected} onCheckedChange={() => toggleItemSelection(item.id)} />
                          </TableCell>
                          <TableCell className="font-medium">{item.productId}</TableCell>
                          <TableCell>{item.description}</TableCell>
                          <TableCell className="text-right">{item.quantity}</TableCell>
                          <TableCell className="text-right">
                            <Input
                              type="number"
                              min={1}
                              max={item.quantity}
                              value={item.deliveryQuantity}
                              onChange={(e) => updateItemQuantity(item.id, Number.parseInt(e.target.value) || 1)}
                              className="w-20 h-8 text-right"
                              disabled={!item.selected}
                            />
                          </TableCell>
                          <TableCell className="text-right">{item.price.toFixed(2)} €</TableCell>
                          <TableCell className="text-right">
                            {item.selected ? (item.deliveryQuantity * item.price).toFixed(2) : "0.00"} €
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right panel - Delivery note details */}
        <div className="w-1/2 bg-white overflow-auto">
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-6">Lieferscheindetails</h3>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-primary" />
                    Lieferscheinnummer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input
                    value={deliveryNoteNumber}
                    onChange={(e) => setDeliveryNoteNumber(e.target.value)}
                    placeholder="z.B. DEL-2023-001"
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-primary" />
                    Lieferdatum
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input type="date" value={deliveryNoteDate} onChange={(e) => setDeliveryNoteDate(e.target.value)} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <User className="h-4 w-4 mr-2 text-primary" />
                    Kunde
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input value={sourceDocument.customer.name} disabled />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <ArrowRightLeft className="h-4 w-4 mr-2 text-primary" />
                    Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Select value={deliveryNoteStatus} onValueChange={setDeliveryNoteStatus}>
                    <SelectTrigger>
                      <SelectValue placeholder="Status auswählen" />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              <Card className="col-span-2">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-primary" />
                    Notizen
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input
                    value={deliveryNoteNotes}
                    onChange={(e) => setDeliveryNoteNotes(e.target.value)}
                    placeholder={`Lieferschein für Auftrag ${sourceDocument.number}`}
                  />
                </CardContent>
              </Card>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-base">Ausgewählte Positionen für Lieferschein</h4>
                <Badge variant="secondary">{selectedItems.length} Positionen</Badge>
              </div>
              <Separator className="mb-4" />

              {selectedItems.length > 0 ? (
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
                            <TableCell className="text-right">{item.deliveryQuantity}</TableCell>
                            <TableCell className="text-right">{item.price.toFixed(2)} €</TableCell>
                            <TableCell className="text-right">
                              {(item.deliveryQuantity * item.price).toFixed(2)} €
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  <div className="bg-muted p-3 flex justify-between items-center border-t">
                    <span className="font-semibold">Gesamtbetrag Lieferschein:</span>
                    <span className="font-bold text-lg">{selectedAmount.toFixed(2)} €</span>
                  </div>
                </div>
              ) : (
                <div className="border rounded-md p-8 text-center text-muted-foreground bg-gray-50">
                  Keine Positionen ausgewählt. Bitte wählen Sie Positionen aus dem Quellauftrag aus.
                </div>
              )}
            </div>
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
            size="lg"
            onClick={createDeliveryNote}
            disabled={
              selectedItems.length === 0 || !deliveryNoteNumber || !deliveryNoteDate || createDocument.isPending
            }
            className="px-8"
          >
            {createDocument.isPending ? "Wird erstellt..." : "Lieferschein erstellen"}
          </Button>
        </div>
      </div>
    </div>
  )
}
