"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/document/use-toast"
import { useDocuments, useCreateDocument } from "@/hooks/document/use-documents"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar, FileText, User, ArrowRightLeft, Search, X } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

/**
 * Props for the OrderMergeView component
 */
interface OrderMergeViewProps {
  onClose: () => void
  sourceDocumentId?: string // Optional: If provided, this order will be pre-selected
}

/**
 * OrderMergeView component that displays a view for merging multiple orders
 * It allows selecting orders to merge into a new order
 */
export function OrderMergeView({ onClose, sourceDocumentId }: OrderMergeViewProps) {
  const { toast } = useToast()
  const { data: documents } = useDocuments()
  const createDocument = useCreateDocument()

  // State for selected orders
  const [selectedOrderIds, setSelectedOrderIds] = useState<string[]>(sourceDocumentId ? [sourceDocumentId] : [])

  // State for new order details
  const [newOrderNumber, setNewOrderNumber] = useState("")
  const [newOrderDate, setNewOrderDate] = useState(new Date().toISOString().split("T")[0])
  const [newOrderStatus, setNewOrderStatus] = useState("OPEN")
  const [newOrderNotes, setNewOrderNotes] = useState("")
  const [customerId, setCustomerId] = useState("")

  // State for search and filters
  const [searchTerm, setSearchTerm] = useState("")
  const [customerFilter, setCustomerFilter] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string | null>(null)

  // Filter documents to only show orders
  const allOrders = documents?.filter((doc) => doc.type === "ORDER") || []

  // Get unique customers for filter dropdown
  const uniqueCustomers = Array.from(new Map(allOrders.map((doc) => [doc.customer.id, doc.customer])).values())

  // Get unique statuses for filter dropdown
  const uniqueStatuses = Array.from(new Set(allOrders.map((doc) => doc.status)))

  // Apply filters and search
  const filteredOrders = allOrders.filter((doc) => {
    // Apply search term
    const matchesSearch =
      searchTerm === "" ||
      doc.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.notes?.toLowerCase().includes(searchTerm.toLowerCase())

    // Apply customer filter
    const matchesCustomer = customerFilter === null || doc.customer.id === customerFilter

    // Apply status filter
    const matchesStatus = statusFilter === null || doc.status === statusFilter

    // Wenn bereits ein Auftrag ausgewählt ist, zeige nur Aufträge vom selben Kunden an
    const matchesSelectedCustomer =
      selectedOrderIds.length === 0 ||
      (selectedOrderIds.length > 0 &&
        allOrders.find((order) => order.id === selectedOrderIds[0])?.customer.id === doc.customer.id)

    return matchesSearch && matchesCustomer && matchesStatus && matchesSelectedCustomer
  })

  // Get selected orders
  const selectedOrders = filteredOrders.filter((doc) => selectedOrderIds.includes(doc.id))

  // Get all items from all selected orders
  const allItems = selectedOrders.flatMap((doc) =>
    doc.items.map((item) => ({ ...item, documentId: doc.id, documentNumber: doc.number })),
  )

  // Calculate total amount for all items
  const totalAmount = allItems.reduce((total, item) => total + item.price * item.quantity, 0)

  // Set customer ID from the first selected order
  useEffect(() => {
    if (selectedOrderIds.length > 0 && !customerId) {
      const firstDoc = documents?.find((doc) => doc.id === selectedOrderIds[0])
      if (firstDoc) {
        setCustomerId(firstDoc.customer.id)
      }
    }
  }, [selectedOrderIds, documents, customerId])

  // Ändern Sie die toggleOrderSelection-Funktion, um die Logik klarer zu machen
  // und eine Fehlermeldung anzuzeigen, wenn ein Benutzer versucht, einen Auftrag
  // eines anderen Kunden auszuwählen

  // Toggle order selection
  const toggleOrderSelection = (orderId: string) => {
    const isSelected = selectedOrderIds.includes(orderId)

    // Wenn der Auftrag bereits ausgewählt ist, kann er abgewählt werden
    if (isSelected) {
      const newSelectedOrderIds = selectedOrderIds.filter((id) => id !== orderId)
      setSelectedOrderIds(newSelectedOrderIds)

      // Wenn keine Aufträge mehr ausgewählt sind, setze customerId zurück
      if (newSelectedOrderIds.length === 0) {
        setCustomerId("")
      }
      return
    }

    // Get the order
    const order = allOrders.find((doc) => doc.id === orderId)
    if (!order) return

    // Wenn dies der erste ausgewählte Auftrag ist, setze den Kunden
    if (selectedOrderIds.length === 0) {
      setCustomerId(order.customer.id)
    }

    // Update selected orders
    setSelectedOrderIds([...selectedOrderIds, orderId])
  }

  // Reset all filters
  const resetFilters = () => {
    setSearchTerm("")
    setCustomerFilter(null)
    setStatusFilter(null)
  }

  // Merge orders
  const mergeOrders = async () => {
    try {
      if (selectedOrders.length < 2) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie mindestens zwei Aufträge aus.",
          variant: "destructive",
        })
        return
      }

      if (!newOrderNumber) {
        toast({
          title: "Fehler",
          description: "Bitte geben Sie eine Auftragsnummer ein.",
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

      // Create new order with all items from selected orders
      createDocument.mutate(
        {
          type: "ORDER",
          number: newOrderNumber,
          customerId: customerId,
          date: newOrderDate,
          status: newOrderStatus,
          notes:
            newOrderNotes ||
            `Auftrag erstellt durch Zusammenführung von ${selectedOrders.map((o) => o.number).join(", ")}`,
          items: allItems.map(({ documentId, documentNumber, ...item }) => item),
          amount: totalAmount,
        },
        {
          onSuccess: () => {
            toast({
              title: "Aufträge zusammengeführt",
              description: `Neuer Auftrag ${newOrderNumber} wurde erfolgreich erstellt.`,
            })
            onClose()
          },
        },
      )
    } catch (error) {
      toast({
        title: "Fehler",
        description: `Fehler beim Zusammenführen der Aufträge: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`,
        variant: "destructive",
      })
    }
  }

  // Get status options
  const statusOptions = [
    { value: "OPEN", label: "Offen" },
    { value: "CONFIRMED", label: "Bestätigt" },
    { value: "COMPLETED", label: "Abgeschlossen" },
    { value: "CANCELED", label: "Storniert" },
  ]

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Aufträge zusammenführen</h2>
              <div className="flex items-center gap-4 mt-1">
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  {selectedOrders.length} Aufträge ausgewählt
                </Badge>
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  {allItems.length} Positionen
                </Badge>
                <Badge variant="outline" className="px-2 py-1 text-sm">
                  Kunde:{" "}
                  {customerId
                    ? uniqueCustomers.find((c) => c.id === customerId)?.name || "Nicht ausgewählt"
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
        {/* Left panel - Order list */}
        <div className="w-1/2 border-r bg-white overflow-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Aufträge</h3>
            </div>

            <div className="flex gap-2 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Suche nach Nummer, Kunde..."
                  className="pl-9"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select
                value={customerFilter || "all"}
                onValueChange={(value) => setCustomerFilter(value === "all" ? null : value)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Kunde" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Kunden</SelectItem>
                  {uniqueCustomers.map((customer) => (
                    <SelectItem key={customer.id} value={customer.id}>
                      {customer.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select
                value={statusFilter || "all"}
                onValueChange={(value) => setStatusFilter(value === "all" ? null : value)}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Status</SelectItem>
                  {uniqueStatuses.map((status) => (
                    <SelectItem key={status} value={status}>
                      {status}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Filter Summary */}
            {(customerFilter || statusFilter) && (
              <div className="flex flex-wrap gap-2 text-sm mb-4">
                {customerFilter && (
                  <Badge variant="outline" className="flex items-center gap-1 py-1 px-2">
                    <User className="h-3 w-3 mr-1" />
                    {uniqueCustomers.find((c) => c.id === customerFilter)?.name}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-4 w-4 p-0 ml-1"
                      onClick={() => setCustomerFilter(null)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </Badge>
                )}

                {statusFilter && (
                  <Badge variant="outline" className="flex items-center gap-1 py-1 px-2">
                    <ArrowRightLeft className="h-3 w-3 mr-1" />
                    {statusFilter}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-4 w-4 p-0 ml-1"
                      onClick={() => setStatusFilter(null)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </Badge>
                )}

                <Button variant="ghost" size="sm" className="h-7 px-2 text-xs" onClick={resetFilters}>
                  Filter zurücksetzen
                </Button>
              </div>
            )}

            <div className="text-sm text-gray-500 mb-2">{filteredOrders.length} Aufträge gefunden</div>
            {selectedOrderIds.length > 0 && (
              <div className="text-sm text-primary mb-4 flex items-center">
                <User className="h-4 w-4 mr-2" />
                Es werden nur Aufträge von {uniqueCustomers.find((c) => c.id === customerId)?.name || "diesem Kunden"}{" "}
                angezeigt
              </div>
            )}
            {customerId && (
              <div className="text-sm text-gray-500 mb-2">
                Es werden nur Aufträge für den Kunden {uniqueCustomers.find((c) => c.id === customerId)?.name}{" "}
                angezeigt.
              </div>
            )}

            <div className="space-y-3">
              {filteredOrders.length > 0 ? (
                filteredOrders.map((order) => {
                  const isSelected = selectedOrderIds.includes(order.id)

                  return (
                    <Card key={order.id} className={`mb-3 overflow-hidden ${isSelected ? "bg-primary/5" : ""}`}>
                      <div
                        className={`p-4 flex justify-between items-center cursor-pointer ${
                          isSelected ? "bg-primary/5" : "bg-white"
                        }`}
                        onClick={() => toggleOrderSelection(order.id)}
                      >
                        <div className="flex items-center gap-3">
                          <Checkbox
                            checked={isSelected}
                            onCheckedChange={() => toggleOrderSelection(order.id)}
                            className="h-5 w-5"
                          />
                          <div>
                            <div className="font-medium">{order.number}</div>
                            <div className="text-sm text-muted-foreground">{order.customer.name}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge variant="outline">{order.status}</Badge>
                          <div className="text-right">
                            <div className="text-sm">{order.date}</div>
                            <div className="font-medium">{order.amount.toFixed(2)} €</div>
                          </div>
                        </div>
                      </div>
                      {isSelected && (
                        <CardContent className="p-3 pt-4 bg-gray-50 border-t">
                          <div className="text-sm mb-2">
                            <span className="font-medium">Positionen:</span> {order.items.length}
                          </div>
                          <div className="border rounded-md overflow-hidden bg-white">
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
                                {order.items.map((item) => (
                                  <TableRow key={item.id}>
                                    <TableCell className="font-medium">{item.productId}</TableCell>
                                    <TableCell>{item.description}</TableCell>
                                    <TableCell className="text-right">{item.quantity}</TableCell>
                                    <TableCell className="text-right">{item.price.toFixed(2)} €</TableCell>
                                    <TableCell className="text-right">
                                      {(item.quantity * item.price).toFixed(2)} €
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </div>
                        </CardContent>
                      )}
                    </Card>
                  )
                })
              ) : (
                <div className="text-center py-8 text-muted-foreground border rounded-md bg-gray-50">
                  {selectedOrderIds.length > 0
                    ? "Keine weiteren Aufträge von diesem Kunden gefunden"
                    : "Keine Aufträge gefunden"}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right panel - New order details */}
        <div className="w-1/2 bg-white overflow-auto">
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-6">Neuer zusammengeführter Auftrag</h3>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-primary" />
                    Auftragsnummer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input
                    value={newOrderNumber}
                    onChange={(e) => setNewOrderNumber(e.target.value)}
                    placeholder="z.B. ORD-2023-001"
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base font-medium flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-primary" />
                    Auftragsdatum
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Input type="date" value={newOrderDate} onChange={(e) => setNewOrderDate(e.target.value)} />
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
                  <Input
                    value={customerId ? uniqueCustomers.find((c) => c.id === customerId)?.name || "" : ""}
                    disabled
                  />
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
                  <Select value={newOrderStatus} onValueChange={setNewOrderStatus}>
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
                    value={newOrderNotes}
                    onChange={(e) => setNewOrderNotes(e.target.value)}
                    placeholder={`Auftrag erstellt durch Zusammenführung von ${selectedOrders.map((o) => o.number).join(", ")}`}
                  />
                </CardContent>
              </Card>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-base">Zusammengeführte Positionen</h4>
                <Badge variant="secondary">{allItems.length} Positionen</Badge>
              </div>
              <Separator className="mb-4" />

              {allItems.length > 0 ? (
                <div className="border rounded-md overflow-hidden">
                  <div className="max-h-[calc(95vh-450px)] overflow-y-auto">
                    <Table>
                      <TableHeader className="bg-muted">
                        <TableRow>
                          <TableHead>Auftrag</TableHead>
                          <TableHead>Artikel-Nr.</TableHead>
                          <TableHead>Beschreibung</TableHead>
                          <TableHead className="text-right">Menge</TableHead>
                          <TableHead className="text-right">Preis</TableHead>
                          <TableHead className="text-right">Gesamt</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {allItems.map((item) => (
                          <TableRow key={item.id}>
                            <TableCell className="text-xs text-muted-foreground">{item.documentNumber}</TableCell>
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
                    <span className="font-semibold">Gesamtbetrag neuer Auftrag:</span>
                    <span className="font-bold text-lg">{totalAmount.toFixed(2)} €</span>
                  </div>
                </div>
              ) : (
                <div className="border rounded-md p-8 text-center text-muted-foreground bg-gray-50">
                  Keine Aufträge ausgewählt. Bitte wählen Sie mindestens zwei Aufträge aus.
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
            onClick={mergeOrders}
            disabled={selectedOrders.length < 2 || !newOrderNumber || !newOrderDate || createDocument.isPending}
            className="px-8"
          >
            {createDocument.isPending ? "Wird erstellt..." : "Aufträge zusammenführen"}
          </Button>
        </div>
      </div>
    </div>
  )
}
