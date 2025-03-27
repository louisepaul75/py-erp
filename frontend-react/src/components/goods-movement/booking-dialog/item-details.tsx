"use client"

import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import type { Item } from "@/lib/types"

interface ItemDetailsProps {
  item: Item
}

export function ItemDetails({ item }: ItemDetailsProps) {
  return (
    <div className="bg-muted/50 p-3 rounded-md">
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-center">
        <Label className="sm:text-right text-sm text-muted-foreground">Item:</Label>
        <div className="sm:col-span-3 font-medium">
          {item.articleNew} <span className="text-muted-foreground">({item.articleOld})</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-center mt-1">
        <Label className="sm:text-right text-sm text-muted-foreground">Description:</Label>
        <div className="sm:col-span-3">{item.description}</div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-center mt-1">
        <Label className="sm:text-right text-sm text-muted-foreground">Available:</Label>
        <div className="sm:col-span-3">
          <Badge variant="outline">{item.quantity} pieces</Badge>
        </div>
      </div>
    </div>
  )
}

