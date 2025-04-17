"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { Document } from "@/types/document/document"

/**
 * Props for the OrderSplitSourceItems component
 */
interface OrderSplitSourceItemsProps {
  sourceDocument: Document
  selectedItems: Record<string, boolean>
  toggleItemSelection: (itemId: string) => void
  toggleAllItems: (value: boolean) => void
  remainingAmount: number
}

/**
 * OrderSplitSourceItems component that displays the source order items for splitting
 */
export function OrderSplitSourceItems({
  sourceDocument,
  selectedItems,
  toggleItemSelection,
  toggleAllItems,
  remainingAmount,
}: OrderSplitSourceItemsProps) {
  return (
    <>
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
            <CardTitle className="text-base font-medium">Quellauftrag Details</CardTitle>
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
          <h4 className="font-semibold text-base">Positionen zum Verschieben auswählen</h4>
          <Badge variant="secondary">
            {Object.values(selectedItems).filter(Boolean).length} von {sourceDocument.items.length} ausgewählt
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
                  <TableHead className="text-right">Menge</TableHead>
                  <TableHead className="text-right">Preis</TableHead>
                  <TableHead className="text-right">Gesamt</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sourceDocument.items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="p-2">
                      <Checkbox
                        checked={selectedItems[item.id] || false}
                        onCheckedChange={() => toggleItemSelection(item.id)}
                      />
                    </TableCell>
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
            <span className="font-semibold">Verbleibender Betrag:</span>
            <span className="font-bold text-lg">{remainingAmount.toFixed(2)} €</span>
          </div>
        </div>
      </div>
    </>
  )
}
