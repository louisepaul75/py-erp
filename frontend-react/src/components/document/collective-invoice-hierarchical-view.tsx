"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/document/use-toast"
import { useDocuments, useCreateDocument } from "@/hooks/document/use-documents"
import { DeliveryNoteSelector } from "@/components/document/delivery-note-selector"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Search, Filter, Calendar, User, FileText } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

/**
 * Props for the CollectiveInvoiceHierarchicalView component
 */
interface CollectiveInvoiceHierarchicalViewProps {
  onClose: () => void
  sourceDocumentId?: string // Optional: If provided, this document will be pre-selected
}

/**
 * CollectiveInvoiceHierarchicalView component that displays a hierarchical view for creating a collective invoice
 * from multiple delivery notes
 */
export function CollectiveInvoiceHierarchicalView({
  onClose,
  sourceDocumentId,
}: CollectiveInvoiceHierarchicalViewProps) {
  const { toast } = useToast()
  const { data: documents } = useDocuments()
  const createDocument = useCreateDocument()

  // State for selected documents and items
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>(sourceDocumentId ? [sourceDocumentId] : [])
  const [selectedItems, setSelectedItems] = useState<Record<string, boolean>>({})
  const [invoiceNumber, setInvoiceNumber] = useState("")
  const [invoiceDate, setInvoiceDate] = useState(new Date().toISOString().split("T")[0])
  const [customerId, setCustomerId] = useState("")

  // Filter documents to only show delivery notes
  const selectedDeliveryNotes =
    documents?.filter((doc) => doc.type === "DELIVERY" && selectedDocumentIds.includes(doc.id)) || []

  // Get all items from all delivery notes
  const allItems =
    documents
      ?.filter((doc) => doc.type === "DELIVERY")
      .flatMap((doc) => doc.items.map((item) => ({ ...item, documentId: doc.id, documentNumber: doc.number }))) || []

  // Get selected items
  const selectedItemsList = allItems.filter((item) => selectedItems[item.id])

  // Calculate total amount for selected items
  const totalAmount = selectedItemsList.reduce((total, item) => total + item.price * item.quantity, 0)

  // Set customer ID from the first selected document
  useEffect(() => {
    if (selectedDocumentIds.length > 0 && !customerId) {
      const firstDoc = documents?.find((doc) => doc.id === selectedDocumentIds[0])
      if (firstDoc) {
        setCustomerId(firstDoc.customer.id)
      }
    }
  }, [selectedDocumentIds, documents, customerId])

  // Initialize selected items when documents change
  useEffect(() => {
    if (documents) {
      const deliveryNotes = documents.filter((doc) => doc.type === "DELIVERY")
      const newSelectedItems: Record<string, boolean> = { ...selectedItems }

      // Initialize new items with false (unselected)
      deliveryNotes.forEach((doc) => {
        doc.items.forEach((item) => {
          if (newSelectedItems[item.id] === undefined) {
            newSelectedItems[item.id] = false
          }
        })
      })

      // If source document is provided, select all its items
      if (sourceDocumentId) {
        const sourceDoc = deliveryNotes.find((doc) => doc.id === sourceDocumentId)
        if (sourceDoc) {
          sourceDoc.items.forEach((item) => {
            newSelectedItems[item.id] = true
          })
        }
      }

      setSelectedItems(newSelectedItems)
    }
  }, [documents, sourceDocumentId])

  // Create invoice
  const createInvoice = async () => {
    try {
      if (selectedItemsList.length === 0) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie mindestens eine Position aus.",
          variant: "destructive",
        })
        return
      }

      if (!invoiceNumber) {
        toast({
          title: "Fehler",
          description: "Bitte geben Sie eine Rechnungsnummer ein.",
          variant: "destructive",
        })
        return
      }

      if (!customerId) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie einen Kunden aus.",
          variant: "destructive",
        })
        return
      }

      // Create invoice with selected items
      createDocument.mutate(
        {
          type: "INVOICE",
          number: invoiceNumber,
          customerId: customerId,
          date: invoiceDate,
          status: "OPEN",
          notes: `Rechnung aus ${selectedDocumentIds.length} Lieferscheinen erstellt mit ${selectedItemsList.length} Positionen`,
          items: selectedItemsList.map(({ documentId, documentNumber, ...item }) => item),
          amount: totalAmount,
        },
        {
          onSuccess: () => {
            toast({
              title: "Rechnung erstellt",
              description: `Rechnung ${invoiceNumber} wurde erfolgreich erstellt.`,
            })
            onClose()
          },
        },
      )
    } catch (error) {
      toast({
        title: "Fehler",
        description: `Fehler beim Erstellen der Rechnung: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`,
        variant: "destructive",
      })
    }
  }

  // Mock customer data
  const customers = [
    { id: "1", name: "Acme Inc." },
    { id: "2", name: "Globex Corporation" },
    { id: "3", name: "Initech" },
    { id: "4", name: "Umbrella Corporation" },
    { id: "5", name: "Stark Industries" },
    { id: "6", name: "Wayne Enterprises" },
    { id: "7", name: "Cyberdyne Systems" },
    { id: "8", name: "Oscorp Industries" },
    { id: "9", name: "Massive Dynamic" },
    { id: "10", name: "Soylent Corp" },
  ]

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Rechnung erstellen (Standard)</h2>
              <div className="flex items-center gap-4 mt-1">
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  {selectedDocumentIds.length} Lieferscheine ausgewählt
                </Badge>
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  {selectedItemsList.length} Positionen
                </Badge>
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  Kunde:{" "}
                  {customerId
                    ? customers.find((c) => c.id === customerId)?.name || "Nicht ausgewählt"
                    : "Nicht ausgewählt"}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-500">Gesamtbetrag</div>
              <div className="text-3xl font-bold text-primary">{totalAmount.toFixed(2)} €</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - Document list */}
        <div className="w-1/2 border-r bg-white overflow-auto">
          <div className="p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Lieferscheine</h3>
              <div className="space-x-2">
                <Button variant="outline" size="sm">
                  Alle auswählen
                </Button>
                <Button variant="outline" size="sm">
                  Alle abwählen
                </Button>
              </div>
            </div>

            <div className="flex gap-2 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Suche nach Nummer, Kunde, Produkt..." className="pl-9" />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>

            <div className="text-sm text-gray-500 mb-2">30 Lieferscheine gefunden (Seite 1 von 3)</div>

            <DeliveryNoteSelector
              selectedDocumentIds={selectedDocumentIds}
              onDocumentSelectionChange={setSelectedDocumentIds}
              selectedItems={selectedItems}
              onItemSelectionChange={setSelectedItems}
              sourceDocumentId={sourceDocumentId}
            />
          </div>
        </div>

        {/* Right panel - Invoice details */}
        <div className="w-1/2 bg-white overflow-auto">
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-6">Rechnungsdetails</h3>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-primary" />
                    Rechnungsnummer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input
                    id="invoiceNumber"
                    value={invoiceNumber}
                    onChange={(e) => setInvoiceNumber(e.target.value)}
                    placeholder="z.B. INV-2023-001"
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-primary" />
                    Rechnungsdatum
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input
                    id="invoiceDate"
                    type="date"
                    value={invoiceDate}
                    onChange={(e) => setInvoiceDate(e.target.value)}
                  />
                </CardContent>
              </Card>

              <Card className="col-span-2">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <User className="h-4 w-4 mr-2 text-primary" />
                    Kunde
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <select
                    id="customer"
                    value={customerId}
                    onChange={(e) => setCustomerId(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="">Kunden auswählen</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.name}
                      </option>
                    ))}
                  </select>
                </CardContent>
              </Card>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-base">Ausgewählte Positionen</h4>
                <Badge variant="secondary">{selectedItemsList.length} Positionen</Badge>
              </div>
              <Separator className="mb-4" />

              {selectedItemsList.length > 0 ? (
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
                        {selectedItemsList.map((item) => (
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
                    <span className="font-semibold">Gesamtbetrag:</span>
                    <span className="font-bold text-lg">{totalAmount.toFixed(2)} €</span>
                  </div>
                </div>
              ) : (
                <div className="border rounded-md p-8 text-center text-muted-foreground bg-gray-50">
                  Keine Positionen ausgewählt. Bitte wählen Sie Positionen aus den Lieferscheinen aus.
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
            onClick={createInvoice}
            disabled={
              selectedItemsList.length === 0 ||
              !invoiceNumber ||
              !invoiceDate ||
              !customerId ||
              createDocument.isPending
            }
            className="px-8"
          >
            {createDocument.isPending ? "Wird erstellt..." : "Rechnung erstellen"}
          </Button>
        </div>
      </div>
    </div>
  )
}
