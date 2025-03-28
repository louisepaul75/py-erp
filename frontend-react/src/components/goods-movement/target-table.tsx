"use client"

import { useMemo } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { BookingItem } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Package, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react"
import type { SortConfig } from "./goods-movement-tab"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useMobile } from "@/hooks/use-mobile"
import { Card, CardContent } from "@/components/ui/card"

interface TargetTableProps {
  items: BookingItem[]
  sortConfig: SortConfig | null
  onSort: (config: SortConfig) => void
}

// Hilfsfunktion zum Gruppieren der Einträge
function groupItemsByBoxAndArticle(items: BookingItem[]): BookingItem[] {
  const groupedMap = new Map<string, BookingItem>()

  items.forEach((item) => {
    // Erstelle einen eindeutigen Schlüssel aus articleOld und boxNumber
    const key = `${item.articleOld}-${item.boxNumber || "nobox"}`

    if (groupedMap.has(key)) {
      // Wenn der Schlüssel bereits existiert, aktualisiere den vorhandenen Eintrag
      const existingItem = groupedMap.get(key)!

      // Addiere die Mengen
      existingItem.quantity += item.quantity

      // Füge Compartments hinzu, wenn sie noch nicht vorhanden sind
      if (item.compartments) {
        const existingCompartments = existingItem.compartments ? existingItem.compartments.split(", ") : []
        const newCompartments = item.compartments.split(", ")

        // Kombiniere und entferne Duplikate
        const allCompartments = [...new Set([...existingCompartments, ...newCompartments])]
        existingItem.compartments = allCompartments.join(", ")
      }

      // Behalte den neuesten Zeitstempel
      if (new Date(item.timestamp) > new Date(existingItem.timestamp)) {
        existingItem.timestamp = item.timestamp
      }
    } else {
      // Wenn der Schlüssel noch nicht existiert, füge einen neuen Eintrag hinzu
      groupedMap.set(key, { ...item })
    }
  })

  // Konvertiere die Map zurück in ein Array
  return Array.from(groupedMap.values())
}

export function TargetTable({ items, sortConfig, onSort }: TargetTableProps) {
  const isMobile = useMobile(768) // Use a tablet breakpoint

  // Gruppierte Items
  const groupedItems = useMemo(() => {
    return groupItemsByBoxAndArticle(items)
  }, [items])

  // Sorted items
  const sortedItems = useMemo(() => {
    if (!sortConfig) return groupedItems

    return [...groupedItems].sort((a, b) => {
      if (a[sortConfig.key as keyof BookingItem] < b[sortConfig.key as keyof BookingItem]) {
        return sortConfig.direction === "asc" ? -1 : 1
      }
      if (a[sortConfig.key as keyof BookingItem] > b[sortConfig.key as keyof BookingItem]) {
        return sortConfig.direction === "asc" ? 1 : -1
      }
      return 0
    })
  }, [groupedItems, sortConfig])

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
    return (
      <div className="space-y-3 max-h-[calc(100vh-350px)] overflow-auto pb-2">
        {sortedItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-muted-foreground py-12">
            <CheckCircle2 className="h-8 w-8 mb-2 opacity-40" />
            <p>No items booked.</p>
            <p className="text-sm">Booked items will appear here.</p>
          </div>
        ) : (
          sortedItems.map((item) => (
            <Card key={item.id} className="overflow-hidden">
              <CardContent className="p-3">
                <div className="flex justify-between items-center mb-2">
                  <div className="font-medium truncate mr-2">{item.articleOld}</div>
                  <Badge variant="secondary">{item.quantity}</Badge>
                </div>

                <div className="text-sm text-muted-foreground mb-2 truncate">{item.description}</div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Target:</span>
                    <Badge variant="outline" className="ml-1">
                      {item.targetSlot}
                    </Badge>
                  </div>

                  {item.boxNumber && (
                    <div className="flex items-center">
                      <span className="text-muted-foreground mr-1">Box:</span>
                      <div className="flex items-center">
                        <Package className="h-3 w-3 mr-1 text-muted-foreground flex-shrink-0" />
                        <span className="truncate">{item.boxNumber}</span>
                      </div>
                    </div>
                  )}

                  {item.compartments && (
                    <div className="col-span-2 mt-1">
                      <span className="text-muted-foreground block mb-1">Compartments:</span>
                      <div className="flex flex-wrap gap-1">
                        {item.compartments.split(", ").map((comp, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {comp}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    )
  }

  // Desktop table view
  return (
    <div className="overflow-auto max-h-[calc(100vh-350px)]">
      <Table className="w-full">
        <TableHeader className="sticky top-0 bg-background z-10">
          <TableRow>
            <TableHead className="w-[15%]">
              <Button
                variant="ghost"
                onClick={() => handleSort("articleOld")}
                className="p-0 h-auto font-semibold hover:bg-transparent text-sm"
              >
                Item No.
                {getSortIcon("articleOld")}
              </Button>
            </TableHead>
            <TableHead className="w-[25%]">
              <Button
                variant="ghost"
                onClick={() => handleSort("description")}
                className="p-0 h-auto font-semibold hover:bg-transparent text-sm"
              >
                Description
                {getSortIcon("description")}
              </Button>
            </TableHead>
            <TableHead className="w-[10%] text-right">
              <Button
                variant="ghost"
                onClick={() => handleSort("quantity")}
                className="p-0 h-auto font-semibold hover:bg-transparent ml-auto text-sm"
              >
                Qty
                {getSortIcon("quantity")}
              </Button>
            </TableHead>
            <TableHead className="w-[15%]">
              <span className="text-sm font-semibold">Box</span>
            </TableHead>
            <TableHead className="w-[15%]">
              <Button
                variant="ghost"
                onClick={() => handleSort("targetSlot")}
                className="p-0 h-auto font-semibold hover:bg-transparent text-sm"
              >
                Target Bin
                {getSortIcon("targetSlot")}
              </Button>
            </TableHead>
            <TableHead className="w-[20%]">
              <span className="text-sm font-semibold">Compartments</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedItems.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="h-24 text-center">
                <div className="flex flex-col items-center justify-center text-muted-foreground">
                  <CheckCircle2 className="h-8 w-8 mb-2 opacity-40" />
                  <p>No items booked.</p>
                  <p className="text-sm">Booked items will appear here.</p>
                </div>
              </TableCell>
            </TableRow>
          ) : (
            sortedItems.map((item) => (
              <TableRow key={item.id} className="hover:bg-muted/50 transition-colors">
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
                  <Badge variant="secondary" className="ml-auto">
                    {item.quantity}
                  </Badge>
                </TableCell>
                <TableCell className="truncate">
                  {item.boxNumber ? (
                    <div className="flex items-center">
                      <Package className="h-3 w-3 mr-1 text-muted-foreground flex-shrink-0" />
                      <span className="text-sm truncate">{item.boxNumber}</span>
                    </div>
                  ) : (
                    <span className="text-muted-foreground">-</span>
                  )}
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{item.targetSlot}</Badge>
                </TableCell>
                <TableCell>
                  {item.compartments ? (
                    <div className="flex flex-wrap gap-1">
                      {item.compartments.split(", ").map((comp, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {comp}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <span className="text-muted-foreground">-</span>
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}

