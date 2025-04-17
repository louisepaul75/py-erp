"use client"

import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Calendar, FileText, User, ArrowRightLeft } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Document, DocumentItem } from "@/types/document/document"

/**
 * Props for the OrderSplitNewOrder component
 */
interface OrderSplitNewOrderProps {
  sourceDocument: Document
  newOrderNumber: string
  setNewOrderNumber: (value: string) => void
  newOrderDate: string
  setNewOrderDate: (value: string) => void
  newOrderStatus: string
  setNewOrderStatus: (value: string) => void
  newOrderNotes: string
  setNewOrderNotes: (value: string) => void
  statusOptions: { value: string; label: string }[]
  selectedItemsList: DocumentItem[]
  selectedAmount: number
}

/**
 * OrderSplitNewOrder component that displays the new order details for splitting
 */
export function OrderSplitNewOrder({
  sourceDocument,
  newOrderNumber,
  setNewOrderNumber,
  newOrderDate,
  setNewOrderDate,
  newOrderStatus,
  setNewOrderStatus,
  newOrderNotes,
  setNewOrderNotes,
  statusOptions,
  selectedItemsList,
  selectedAmount,
}: OrderSplitNewOrderProps) {
  return (
    <>
      <h3 className="text-xl font-semibold mb-6">Neuer Auftrag</h3>

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
              placeholder={`Auftrag erstellt durch Splitting von ${sourceDocument.number}`}
            />
          </CardContent>
        </Card>
      </div>

      <div className="mb-4">
        <div className="flex justify-between items-center mb-3">
          <h4 className="font-semibold text-base">Ausgewählte Positionen für neuen Auftrag</h4>
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
              <span className="font-semibold">Gesamtbetrag neuer Auftrag:</span>
              <span className="font-bold text-lg">{selectedAmount.toFixed(2)} €</span>
            </div>
          </div>
        ) : (
          <div className="border rounded-md p-8 text-center text-muted-foreground bg-gray-50">
            Keine Positionen ausgewählt. Bitte wählen Sie Positionen aus dem Quellauftrag aus.
          </div>
        )}
      </div>
    </>
  )
}
