"use client"

import { Badge } from "@/components/ui/badge"
import type { Document } from "@/types/document/document"

/**
 * Props for the OrderSplitHeader component
 */
interface OrderSplitHeaderProps {
  sourceDocument: Document
  selectedItemsCount: number
  selectedAmount: number
}

/**
 * OrderSplitHeader component that displays the header for the order split view
 */
export function OrderSplitHeader({ sourceDocument, selectedItemsCount, selectedAmount }: OrderSplitHeaderProps) {
  return (
    <div className="bg-white border-b shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">Auftrag splitten</h2>
            <div className="flex items-center gap-4 mt-1">
              <Badge variant="outline" className="px-2 py-1 text-sm">
                Auftrag: {sourceDocument.number}
              </Badge>
              <Badge variant="outline" className="px-2 py-1 text-sm">
                Kunde: {sourceDocument.customer.name}
              </Badge>
              <Badge variant="outline" className="px-2 py-1 text-sm">
                {selectedItemsCount} von {sourceDocument.items.length} Positionen ausgewählt
              </Badge>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-500">Neuer Auftragswert</div>
            <div className="text-3xl font-bold text-primary">{selectedAmount.toFixed(2)} €</div>
          </div>
        </div>
      </div>
    </div>
  )
}
