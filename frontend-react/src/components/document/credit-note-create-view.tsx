"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { useDocuments, useCreateDocument } from "@/hooks/document/use-documents"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar, FileText, User, ArrowRightLeft, MinusCircle } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { DocumentItem } from "@/types/document/document"

/**
 * Props for the CreditNoteCreateView component
 */
interface CreditNoteCreateViewProps {
  onClose: () => void
  sourceDocumentId: string // Required: The invoice to create a credit note from
}

/**
 * Interface for item selection with quantity
 */
interface SelectedItem extends DocumentItem {
  selected: boolean
  creditQuantity: number
}

/**
 * CreditNoteCreateView component that displays a view for creating a credit note from an invoice
 * It allows selecting specific items to include in the credit note
 */
export function CreditNoteCreateView({ onClose, sourceDocumentId }: CreditNoteCreateViewProps) {
  const { toast } = useToast()
  const { data: documents } = useDocuments()
  const createDocument = useCreateDocument()

  // Get the source document
  const sourceDocument = documents?.find((doc) => doc.id === sourceDocumentId)

  // State for selected items with quantities
  const [items, setItems] = useState<SelectedItem[]>([])

  // State for new credit note details
  const [creditNoteNumber, setCreditNoteNumber] = useState("")
  const [creditNoteDate, setCreditNoteDate] = useState(new Date().toISOString().split("T")[0])
  const [creditNoteStatus, setCreditNoteStatus] = useState("OPEN")
  const [creditNoteNotes, setCreditNoteNotes] = useState("")
  const [creditReason, setCreditReason] = useState("RETURN")

  // Initialize items when source document changes
  useEffect(() => {
    if (sourceDocument) {
      const initialItems: SelectedItem[] = sourceDocument.items.map((item: DocumentItem) => ({
        ...item,
        selected: false,
        creditQuantity: item.quantity, // Default to full quantity
      }))
      setItems(initialItems)
    }
  }, [sourceDocument])

  // Get selected items
  const selectedItems = items.filter((item) => item.selected)

  // Calculate total amount for selected items
  const selectedAmount = selectedItems.reduce((total, item) => total + item.price * item.creditQuantity, 0)

  // Toggle item selection
  const toggleItemSelection = (itemId: string) => {
    setItems(items.map((item) => (item.id === itemId ? { ...item, selected: !item.selected } : item)))
  }

  // Update item credit quantity
  const updateItemQuantity = (itemId: string, quantity: number) => {
    setItems(
      items.map((item) => {
        if (item.id === itemId) {
          // Ensure quantity is not greater than original and not less than 1
          const validQuantity = Math.min(Math.max(1, quantity), item.quantity)
          return { ...item, creditQuantity: validQuantity }
        }
        return item
      }),
    )
  }

  // Toggle all items
  const toggleAllItems = (value: boolean) => {
    setItems(items.map((item) => ({ ...item, selected: value })))
  }

  // Create credit note
  const createCreditNote = async () => {
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

      if (!creditNoteNumber) {
        toast({
          title: "Fehler",
          description: "Bitte geben Sie eine Gutschriftsnummer ein.",
          variant: "destructive",
        })
        return
      }

      // Create credit note with selected items
      const creditItems = selectedItems.map(({ selected, creditQuantity, ...item }) => ({
        ...item,
        quantity: creditQuantity, // Use the credit quantity
      }))

      createDocument.mutate(
        {
          type: "CREDIT",
          number: creditNoteNumber,
          customer: {
            id: sourceDocument.customer.id,
            name: sourceDocument.customer.name
          },
          date: creditNoteDate,
          status: creditNoteStatus,
          notes:
            creditNoteNotes ||
            `Gutschrift erstellt für Rechnung ${sourceDocument.number} - Grund: ${getCreditReasonLabel(creditReason)}`,
          items: creditItems,
          amount: selectedAmount,
        },
        {
          onSuccess: () => {
            toast({
              title: "Gutschrift erstellt",
              description: `Gutschrift ${creditNoteNumber} wurde erfolgreich erstellt.`,
            })
            onClose()
          },
        },
      )
    } catch (error) {
      toast({
        title: "Fehler",
        description: `Fehler beim Erstellen der Gutschrift: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`,
        variant: "destructive",
      })
    }
  }

  // Get status options
  const statusOptions = [
    { value: "OPEN", label: "Offen" },
    { value: "PROCESSED", label: "Verarbeitet" },
    { value: "CANCELED", label: "Storniert" },
  ]

  // Get credit reason options
  const creditReasonOptions = [
    { value: "RETURN", label: "Retoure" },
    { value: "COMPLAINT", label: "Reklamation" },
    { value: "PRICE_ADJUSTMENT", label: "Preisanpassung" },
    { value: "CANCELLATION", label: "Stornierung" },
    { value: "OTHER", label: "Sonstiges" },
  ]

  // Get credit reason label
  const getCreditReasonLabel = (value: string): string => {
    return creditReasonOptions.find((option) => option.value === value)?.label || value
  }

  if (!sourceDocument) {
    return (
      <div className="flex flex-col h-full bg-gray-50 items-center justify-center">
        <div className="w-96 p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Fehler</h3>
          <p className="text-muted-foreground">Die ausgewählte Rechnung wurde nicht gefunden.</p>
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
              <h2 className="text-2xl font-bold">Gutschrift erstellen</h2>
              <div className="flex items-center gap-4 mt-1">
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  Rechnung: {sourceDocument.number}
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
              <div className="text-sm font-medium text-gray-500">Gutschriftsbetrag</div>
              <div className="text-3xl font-bold text-primary">{selectedAmount.toFixed(2)} €</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - Source invoice items */}
        <div className="w-1/2 border-r bg-white overflow-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Positionen der Quellrechnung</h3>
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
                  <CardTitle className="text-base font-medium">Rechnungsdetails</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Rechnungsnummer:</span> {sourceDocument.number}
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
                <h4 className="font-semibold text-base">Positionen für Gutschrift auswählen</h4>
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
                        <TableHead className="text-right">Gutschrift Menge</TableHead>
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
                              value={item.creditQuantity}
                              onChange={(e) => updateItemQuantity(item.id, Number.parseInt(e.target.value) || 1)}
                              className="w-20 h-8 text-right"
                              disabled={!item.selected}
                            />
                          </TableCell>
                          <TableCell className="text-right">{item.price.toFixed(2)} €</TableCell>
                          <TableCell className="text-right">
                            {item.selected ? (item.creditQuantity * item.price).toFixed(2) : "0.00"} €
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

        {/* Right panel - Credit note details */}
        <div className="w-1/2 bg-white overflow-auto">
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-6">Gutschriftsdetails</h3>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-primary" />
                    Gutschriftsnummer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input
                    value={creditNoteNumber}
                    onChange={(e) => setCreditNoteNumber(e.target.value)}
                    placeholder="z.B. CRD-2023-001"
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-primary" />
                    Gutschriftsdatum
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input type="date" value={creditNoteDate} onChange={(e) => setCreditNoteDate(e.target.value)} />
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
                  <Select value={creditNoteStatus} onValueChange={setCreditNoteStatus}>
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
                    <MinusCircle className="h-4 w-4 mr-2 text-primary" />
                    Grund der Gutschrift
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Select value={creditReason} onValueChange={setCreditReason}>
                    <SelectTrigger>
                      <SelectValue placeholder="Grund auswählen" />
                    </SelectTrigger>
                    <SelectContent>
                      {creditReasonOptions.map((option) => (
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
                    value={creditNoteNotes}
                    onChange={(e) => setCreditNoteNotes(e.target.value)}
                    placeholder={`Gutschrift für Rechnung ${sourceDocument.number}`}
                  />
                </CardContent>
              </Card>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-base">Ausgewählte Positionen für Gutschrift</h4>
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
                            <TableCell className="text-right">{item.creditQuantity}</TableCell>
                            <TableCell className="text-right">{item.price.toFixed(2)} €</TableCell>
                            <TableCell className="text-right">
                              {(item.creditQuantity * item.price).toFixed(2)} €
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  <div className="bg-muted p-3 flex justify-between items-center border-t">
                    <span className="font-semibold">Gesamtbetrag Gutschrift:</span>
                    <span className="font-bold text-lg">{selectedAmount.toFixed(2)} €</span>
                  </div>
                </div>
              ) : (
                <div className="border rounded-md p-8 text-center text-muted-foreground bg-gray-50">
                  Keine Positionen ausgewählt. Bitte wählen Sie Positionen aus der Quellrechnung aus.
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
            onClick={createCreditNote}
            disabled={selectedItems.length === 0 || !creditNoteNumber || !creditNoteDate || createDocument.isPending}
            className="px-8"
          >
            {createDocument.isPending ? "Wird erstellt..." : "Gutschrift erstellen"}
          </Button>
        </div>
      </div>
    </div>
  )
}
