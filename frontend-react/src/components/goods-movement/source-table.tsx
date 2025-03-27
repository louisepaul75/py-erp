"use client"

import { useMemo } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Checkbox } from "@/components/ui/checkbox"
import type { Item } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { Box, Loader2, ArrowUpDown, ArrowUp, ArrowDown, Minus, ClipboardEdit } from "lucide-react"
import type { SortConfig } from "./goods-movement-tab"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useMobile } from "@/hooks/use-mobile"
import { Card, CardContent } from "@/components/ui/card"

interface SourceTableProps {
  items: Item[]
  isLoading: boolean
  selectedItems: Item[]
  onItemSelect: (item: Item, selected: boolean) => void
  onSelectAll: (selected: boolean) => void
  sortConfig: SortConfig | null
  onSort: (config: SortConfig) => void
  onCorrection?: (item: Item) => void
}

export function SourceTable({
  items,
  isLoading,
  selectedItems,
  onItemSelect,
  onSelectAll,
  sortConfig,
  onSort,
  onCorrection,
}: SourceTableProps) {
  const isMobile = useMobile(768) // Use a tablet breakpoint

  const isSelected = (item: Item) => selectedItems.some((i) => i.id === item.id)

  // Calculate if all selectable items are selected
  const selectableItems = useMemo(() => items.filter((item) => item.quantity > 0), [items])

  const allSelected = selectableItems.length > 0 && selectableItems.every((item) => isSelected(item))

  const someSelected = selectableItems.length > 0 && selectableItems.some((item) => isSelected(item)) && !allSelected

  // Sorted items
  const sortedItems = useMemo(() => {
    if (!sortConfig) return items

    return [...items].sort((a, b) => {
      if (a[sortConfig.key as keyof Item] < b[sortConfig.key as keyof Item]) {
        return sortConfig.direction === "asc" ? -1 : 1
      }
      if (a[sortConfig.key as keyof Item] > b[sortConfig.key as keyof Item]) {
        return sortConfig.direction === "asc" ? 1 : -1
      }
      return 0
    })
  }, [items, sortConfig])

  const handleSort = (key: string) => {
    if (sortConfig?.key === key) {
      onSort({
        key,
        direction: sortConfig.direction === "asc" ? "desc" : "asc",
      })
    } else {
      onSort({ key, direction: "asc" })
    }
  }

  const getSortIcon = (key: string) => {
    if (sortConfig?.key !== key) {
      return <ArrowUpDown className="ml-1 h-4 w-4" />
    }
    return sortConfig.direction === "asc" ? (
      <ArrowUp className="ml-1 h-4 w-4" />
    ) : (
      <ArrowDown className="ml-1 h-4 w-4" />
    )
  }

  // Mobile card view
  if (isMobile) {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Loading items...</span>
        </div>
      )
    }

    if (sortedItems.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center text-muted-foreground py-12">
          <Box className="h-8 w-8 mb-2 opacity-40" />
          <p>No items found.</p>
          <p className="text-sm">Please scan a box or enter an order number.</p>
        </div>
      )
    }

    return (
      <div className="space-y-3 max-h-[calc(100vh-350px)] overflow-auto pb-2">
        <div className="flex items-center px-3 py-2">
          <Checkbox
            checked={allSelected}
            onCheckedChange={onSelectAll}
            disabled={selectableItems.length === 0}
            aria-label="Select all items"
            className="mr-2"
          />
          <span className="text-sm font-medium">{allSelected ? "Deselect all" : "Select all"}</span>
          <span className="ml-auto text-sm text-muted-foreground">{selectedItems.length} selected</span>
        </div>

        {sortedItems.map((item) => (
          <Card
            key={item.id}
            className={`overflow-hidden ${isSelected(item) ? "border-primary" : ""} ${item.quantity <= 0 ? "opacity-60" : ""}`}
          >
            <CardContent className="p-3">
              <div className="flex items-start">
                <Checkbox
                  checked={isSelected(item)}
                  onCheckedChange={(checked) => onItemSelect(item, !!checked)}
                  disabled={item.quantity <= 0}
                  className="mt-1 mr-3"
                />

                <div className="flex-1">
                  <div className="flex justify-between items-center mb-2">
                    <div className="font-medium truncate mr-2">{item.articleOld}</div>
                    <Badge variant={item.quantity > 0 ? "default" : "outline"}>{item.quantity}</Badge>
                  </div>

                  <div className="text-sm text-muted-foreground mb-2 truncate">{item.description}</div>

                  <div className="flex flex-wrap gap-1 mt-2">
                    {item.slotCodes.map((slot) => (
                      <Badge key={slot} variant="outline" className="text-xs">
                        {slot}
                      </Badge>
                    ))}
                  </div>

                  {onCorrection && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onCorrection(item)}
                      className="mt-2 text-xs h-7 px-2"
                    >
                      <ClipboardEdit className="h-3 w-3 mr-1" />
                      Korrektur
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  // Desktop table view
  return (
    <div className="overflow-auto max-h-[calc(100vh-350px)]">
      <Table className="w-full">
        <TableHeader className="sticky top-0 bg-background z-10">
          <TableRow>
            <TableHead className="w-10">
              {someSelected ? (
                <div className="flex h-4 w-4 items-center justify-center rounded-sm border border-primary bg-primary text-primary-foreground">
                  <Minus className="h-3 w-3" />
                </div>
              ) : (
                <Checkbox
                  checked={allSelected}
                  onCheckedChange={onSelectAll}
                  disabled={selectableItems.length === 0}
                  aria-label="Select all items"
                />
              )}
            </TableHead>
            <TableHead className="w-[20%]">
              <Button
                variant="ghost"
                onClick={() => handleSort("articleOld")}
                className="p-0 h-auto font-semibold hover:bg-transparent text-sm"
              >
                Item No.
                {getSortIcon("articleOld")}
              </Button>
            </TableHead>
            <TableHead className="w-[30%]">
              <Button
                variant="ghost"
                onClick={() => handleSort("description")}
                className="p-0 h-auto font-semibold hover:bg-transparent text-sm"
              >
                Description
                {getSortIcon("description")}
              </Button>
            </TableHead>
            <TableHead className="w-[15%] text-right">
              <Button
                variant="ghost"
                onClick={() => handleSort("quantity")}
                className="p-0 h-auto font-semibold hover:bg-transparent ml-auto text-sm"
              >
                Quantity
                {getSortIcon("quantity")}
              </Button>
            </TableHead>
            <TableHead className="w-[20%]">
              <span className="text-sm font-semibold">Box</span>
            </TableHead>
            {onCorrection && (
              <TableHead className="w-[10%]">
                <span className="text-sm font-semibold">Aktion</span>
              </TableHead>
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={onCorrection ? 6 : 5} className="h-24 text-center">
                <div className="flex items-center justify-center">
                  <Loader2 className="h-6 w-6 animate-spin mr-2" />
                  <span>Loading items...</span>
                </div>
              </TableCell>
            </TableRow>
          ) : sortedItems.length === 0 ? (
            <TableRow>
              <TableCell colSpan={onCorrection ? 6 : 5} className="h-24 text-center">
                <div className="flex flex-col items-center justify-center text-muted-foreground">
                  <Box className="h-8 w-8 mb-2 opacity-40" />
                  <p>No items found.</p>
                  <p className="text-sm">Please scan a box or enter an order number.</p>
                </div>
              </TableCell>
            </TableRow>
          ) : (
            sortedItems.map((item) => (
              <TableRow
                key={item.id}
                className={`
                  ${isSelected(item) ? "bg-muted/50" : ""}
                  ${item.quantity <= 0 ? "opacity-60" : ""}
                  hover:bg-muted/50 transition-colors
                `}
              >
                <TableCell>
                  <Checkbox
                    checked={isSelected(item)}
                    onCheckedChange={(checked) => onItemSelect(item, !!checked)}
                    disabled={item.quantity <= 0}
                  />
                </TableCell>
                <TableCell className="font-medium truncate">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="flex items-center space-x-1">
                          <span className="truncate">{item.articleOld}</span>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Old: {item.articleOld}</p>
                        <p>New: {item.articleNew}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </TableCell>
                <TableCell className="truncate">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger className="text-left w-full">
                        <span className="truncate block">{item.description}</span>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{item.description}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </TableCell>
                <TableCell className="text-right">
                  <Badge variant={item.quantity > 0 ? "default" : "outline"} className="ml-auto">
                    {item.quantity}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {item.slotCodes.map((slot) => (
                      <Badge key={slot} variant="outline" className="text-xs">
                        {slot}
                      </Badge>
                    ))}
                  </div>
                </TableCell>
                {onCorrection && (
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={() => onCorrection(item)} className="h-7 px-2">
                      <ClipboardEdit className="h-3 w-3 mr-1" />
                      Korrektur
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}

