"use client"

import { useState, useEffect, useRef, useMemo } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { SourceTable } from "./source-table"
import { TargetTable } from "./target-table"
import { ScannerInput } from "./scanner-input"
import { BookingDialog } from "./booking-dialog"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/use-toast"
import { useWebSocket } from "@/hooks/use-websocket"
import { useHistory } from "./history-context"
import { fetchItemsByBox, fetchItemsByOrder, bookItems } from "@/lib/api"
import type { Item, BookingItem, HistoryEntry } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, Loader2, ScanBarcode, Package, Settings } from "lucide-react"
import { SettingsDialog, type InventorySettings } from "./settings-dialog"
import { InventoryCorrectionDialog, type CorrectionReason } from "./inventory-correction-dialog"
import { useTimer } from "@/components/timer/timer-context"

// Mock data for source table
const initialMockSourceItems: Item[] = [
  {
    id: "1",
    articleOld: "A1001",
    articleNew: "N2001",
    description: "Wireless Headphones",
    quantity: 10,
    slotCodes: ["S101", "S102"],
    boxNumber: "B001",
  },
  {
    id: "2",
    articleOld: "A1002",
    articleNew: "N2002",
    description: "USB-C Cable",
    quantity: 25,
    slotCodes: ["S103"],
    boxNumber: "B001",
  },
  {
    id: "3",
    articleOld: "A1003",
    articleNew: "N2003",
    description: "Wireless Mouse",
    quantity: 15,
    slotCodes: ["S104", "S105"],
    boxNumber: "B002",
  },
  {
    id: "4",
    articleOld: "A1004",
    articleNew: "N2004",
    description: "Power Bank",
    quantity: 8,
    slotCodes: ["S106"],
    orderNumber: "O001",
  },
  {
    id: "5",
    articleOld: "A1005",
    articleNew: "N2005",
    description: "Bluetooth Speaker",
    quantity: 12,
    slotCodes: ["S107"],
    orderNumber: "O001",
  },
]

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

interface GoodsMovementTabProps {
  tabId: string
  onStatusUpdate?: (allAssigned: boolean) => void
}

export type SortConfig = {
  key: string
  direction: "asc" | "desc"
}

export function GoodsMovementTab({ tabId, onStatusUpdate }: GoodsMovementTabProps) {
  // Bestehende States beibehalten
  const { addBookedItems } = useTimer()
  const [selectedItems, setSelectedItems] = useState<Item[]>([])
  const [bookingDialogOpen, setBookingDialogOpen] = useState(false)
  const [boxNumber, setBoxNumber] = useState("")
  const [orderNumber, setOrderNumber] = useState("")
  const [targetItems, setTargetItems] = useState<BookingItem[]>([])
  // Initialisiere die Mockdaten
  const [mockSourceItems, setMockSourceItems] = useState<Item[]>([...initialMockSourceItems])
  const [useMockData, setUseMockData] = useState(true)

  // Sorting
  const [sourceSortConfig, setSourceSortConfig] = useState<SortConfig | null>(null)
  const [targetSortConfig, setTargetSortConfig] = useState<SortConfig | null>(null)

  // Settings
  const [settings, setSettings] = useState<InventorySettings>({
    tolerancePercentage: 10, // Default-Wert: 10%
  })
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false)

  // Inventory Correction Dialog
  const [correctionDialogOpen, setCorrectionDialogOpen] = useState(false)
  const [selectedItemForCorrection, setSelectedItemForCorrection] = useState<Item | null>(null)

  // Ref to track previous assignment status to prevent unnecessary updates
  const prevAllAssignedRef = useRef<boolean>(false)

  const { toast } = useToast()
  const queryClient = useQueryClient()
  const { addHistoryEntry } = useHistory()

  // Gruppierte Target-Items für die Anzeige der Anzahl
  const groupedTargetItems = useMemo(() => {
    return groupItemsByBoxAndArticle(targetItems)
  }, [targetItems])

  // Listen for WebSocket events
  useWebSocket({
    onMessage: (data) => {
      if (data.type === "INVENTORY_UPDATED") {
        queryClient.invalidateQueries({ queryKey: ["sourceItems", tabId] })
        toast({
          title: "Inventory updated",
          description: "The inventory has been updated by an external booking.",
        })
      }
    },
  })

  // Source items query
  const {
    data: sourceItems = useMockData ? mockSourceItems : [],
    isLoading: isLoadingSourceItems,
    refetch: refetchSourceItems,
  } = useQuery({
    queryKey: ["sourceItems", tabId, boxNumber, orderNumber, useMockData, mockSourceItems],
    queryFn: () => {
      if (useMockData) {
        return Promise.resolve(mockSourceItems)
      } else if (boxNumber) {
        return fetchItemsByBox(boxNumber)
      } else if (orderNumber) {
        return fetchItemsByOrder(orderNumber)
      }
      return Promise.resolve([])
    },
    enabled: !!(useMockData || boxNumber || orderNumber),
  })

  // Überprüfen, ob alle Artikel zugewiesen wurden - mit Optimierung, um Endlosschleifen zu vermeiden
  useEffect(() => {
    if (sourceItems && onStatusUpdate) {
      const allAssigned = sourceItems.every((item) => item.quantity === 0)

      // Nur aktualisieren, wenn sich der Status geändert hat
      if (allAssigned !== prevAllAssignedRef.current) {
        prevAllAssignedRef.current = allAssigned
        onStatusUpdate(allAssigned)
      }
    }
  }, [sourceItems, onStatusUpdate])

  // Booking mutation
  const bookItemsMutation = useMutation({
    mutationFn: bookItems,
    onSuccess: (data) => {
      // Update target items
      setTargetItems((prev) => [...prev, ...data])

      // Speichere die gebuchten Artikel im Timer-Kontext
      try {
        addBookedItems(data)
      } catch (error) {
        console.error("Fehler beim Hinzufügen der Buchungen zum Timer:", error)
      }

      if (useMockData) {
        // Update mock source items by reducing quantities
        setMockSourceItems((prevItems) => {
          const updatedItems = [...prevItems]
          data.forEach((bookedItem) => {
            const sourceItemIndex = updatedItems.findIndex((item) => item.articleOld === bookedItem.articleOld)
            if (sourceItemIndex !== -1) {
              updatedItems[sourceItemIndex] = {
                ...updatedItems[sourceItemIndex],
                quantity: Math.max(0, updatedItems[sourceItemIndex].quantity - bookedItem.quantity),
              }
            }
          })
          return updatedItems
        })
      } else {
        // Refresh source items from API
        refetchSourceItems()
      }

      // Speichere jede Buchung in der History
      data.forEach((item) => {
        const historyEntry: Omit<HistoryEntry, "id"> = {
          timestamp: new Date().toISOString(),
          user: "mock-current-user",
          articleOld: item.articleOld,
          articleNew: item.articleNew,
          quantity: item.quantity,
          sourceSlot: "mock-source-slot", // In einer echten Anwendung würde dies aus den Quelldaten kommen
          targetSlot: item.targetSlot,
          boxNumber: item.boxNumber,
          correction: item.correction,
        }

        // Speichere den History-Eintrag
        addHistoryEntry(historyEntry)
      })

      // Show success message
      toast({
        title: "Booking successful",
        description: `${data.length} items were successfully booked.`,
      })
    },
    onError: (error) => {
      toast({
        title: "Booking failed",
        description: error.message,
        variant: "destructive",
      })
    },
  })

  const handleBoxScan = (value: string) => {
    setBoxNumber(value)
    setOrderNumber("")
    setUseMockData(false)
  }

  const handleOrderInput = (value: string) => {
    setOrderNumber(value)
    setBoxNumber("")
    setUseMockData(false)
  }

  const handleItemSelect = (item: Item, selected: boolean) => {
    if (selected) {
      setSelectedItems((prev) => [...prev, item])
    } else {
      setSelectedItems((prev) => prev.filter((i) => i.id !== item.id))
    }
  }

  const handleSelectAllItems = (selected: boolean) => {
    if (selected) {
      // Only select items with quantity > 0
      const selectableItems = sourceItems.filter((item) => item.quantity > 0)
      setSelectedItems(selectableItems)
    } else {
      setSelectedItems([])
    }
  }

  const handleBookItems = (bookingItems: BookingItem[]) => {
    bookItemsMutation.mutate(bookingItems)
    setBookingDialogOpen(false)
    setSelectedItems([])
  }

  const handleSourceSort = (config: SortConfig) => {
    setSourceSortConfig(config)
  }

  const handleTargetSort = (config: SortConfig) => {
    setTargetSortConfig(config)
  }

  const handleSaveSettings = (newSettings: InventorySettings) => {
    setSettings(newSettings)
    toast({
      title: "Einstellungen gespeichert",
      description: `Toleranzwert wurde auf ${newSettings.tolerancePercentage}% gesetzt.`,
    })
  }

  // Neue Funktion für die Bestandskorrektur
  const handleCorrection = (item: Item) => {
    setSelectedItemForCorrection(item)
    setCorrectionDialogOpen(true)
  }

  // Funktion zum Bestätigen der Bestandskorrektur
  const handleCorrectionConfirm = (itemId: string, newQuantity: number, reason: CorrectionReason, note: string) => {
    // In einer echten Anwendung würde hier ein API-Aufruf erfolgen
    if (useMockData) {
      // Finde das Item
      const item = mockSourceItems.find((item) => item.id === itemId)
      if (!item) return

      const oldQuantity = item.quantity
      const difference = newQuantity - oldQuantity
      const isIncrease = difference > 0

      // Update mock source items
      setMockSourceItems((prevItems) => {
        return prevItems.map((item) => {
          if (item.id === itemId) {
            return {
              ...item,
              quantity: newQuantity,
            }
          }
          return item
        })
      })

      // Erstelle einen History-Eintrag für die Korrektur
      const historyEntry: Omit<HistoryEntry, "id"> = {
        timestamp: new Date().toISOString(),
        user: "mock-current-user",
        articleOld: item.articleOld,
        articleNew: item.articleNew,
        quantity: Math.abs(difference),
        sourceSlot: item.slotCodes[0] || "mock-slot",
        targetSlot: isIncrease ? item.slotCodes[0] || "mock-slot" : "mock-inventory-correction",
        boxNumber: item.boxNumber,
        orderNumber: item.orderNumber,
        correction: {
          type: "inventory_correction",
          reason: reason,
          amount: Math.abs(difference),
          note: note || undefined,
          oldQuantity: oldQuantity,
          newQuantity: newQuantity,
        },
      }

      // Speichere den History-Eintrag im Context
      addHistoryEntry(historyEntry)

      // Erstelle ein BookingItem für den Timer-Kontext
      const correctionBookingItem: BookingItem = {
        id: `correction-${item.id}-${Date.now()}`,
        articleOld: item.articleOld,
        articleNew: item.articleNew,
        description: item.description,
        quantity: Math.abs(difference),
        targetSlot: "inventory-correction",
        timestamp: new Date().toISOString(),
        correction: {
          type: "inventory_correction",
          reason: reason,
          amount: Math.abs(difference),
          note: note || undefined,
          oldQuantity: oldQuantity,
          newQuantity: newQuantity,
        },
      }

      // Speichere die Korrektur im Timer-Kontext
      try {
        addBookedItems([correctionBookingItem])
      } catch (error) {
        console.error("Fehler beim Hinzufügen der Korrektur zum Timer:", error)
      }

      // Erfolgsmeldung anzeigen
      toast({
        title: isIncrease ? "Bestand erhöht" : "Bestand verringert",
        description: `Artikel ${item.articleNew}: Bestand wurde von ${oldQuantity} auf ${newQuantity} ${
          isIncrease ? "erhöht" : "verringert"
        }. Grund: ${reason}`,
      })
    } else {
      // In einer echten Anwendung würde hier ein API-Aufruf erfolgen
      // und dann die Daten neu geladen werden
      refetchSourceItems()
    }

    setCorrectionDialogOpen(false)
    setSelectedItemForCorrection(null)
  }

  return (
    <div className="flex flex-col space-y-4">
      {/* Scanner Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 mb-2">
              <ScanBarcode className="h-5 w-5" />
              <h3 className="font-medium">Scan Box</h3>
            </div>
            <ScannerInput
              label=""
              value={boxNumber}
              onChange={handleBoxScan}
              disabled={!!orderNumber}
              className="w-full"
              placeholder="Box scannen..."
              icon={<ScanBarcode className="h-4 w-4 text-muted-foreground" />}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Package className="h-5 w-5" />
                <h3 className="font-medium">Order Number</h3>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setSettingsDialogOpen(true)} className="h-8 w-8 p-0">
                <Settings className="h-4 w-4" />
                <span className="sr-only">Einstellungen</span>
              </Button>
            </div>
            <ScannerInput
              label=""
              value={orderNumber}
              onChange={handleOrderInput}
              disabled={!!boxNumber}
              className="w-full"
              placeholder="Enter order number..."
              icon={<Package className="h-4 w-4 text-muted-foreground" />}
            />
          </CardContent>
        </Card>
      </div>

      {/* Tables Container */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source Table */}
        <Card className="h-full shadow-sm">
          <CardHeader className="pb-3 border-b">
            <CardTitle className="flex items-center text-lg">
              <span className="bg-muted w-7 h-7 rounded-full flex items-center justify-center mr-2 text-sm">S</span>
              Source Items
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <SourceTable
              items={sourceItems}
              isLoading={isLoadingSourceItems}
              selectedItems={selectedItems}
              onItemSelect={handleItemSelect}
              onSelectAll={handleSelectAllItems}
              sortConfig={sourceSortConfig}
              onSort={handleSourceSort}
              onCorrection={handleCorrection}
            />

            <div className="p-4 border-t bg-muted/30 flex justify-between items-center">
              <div className="text-sm text-muted-foreground">
                {selectedItems.length > 0 ? (
                  <span>{selectedItems.length} items selected</span>
                ) : (
                  <span>No items selected</span>
                )}
              </div>
              <Button onClick={() => setBookingDialogOpen(true)} disabled={selectedItems.length === 0}>
                {bookItemsMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <ArrowRight className="mr-2 h-4 w-4" />
                )}
                Move
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Target Table */}
        <Card className="h-full shadow-sm">
          <CardHeader className="pb-3 border-b">
            <CardTitle className="flex items-center text-lg">
              <span className="bg-muted w-7 h-7 rounded-full flex items-center justify-center mr-2 text-sm">T</span>
              Target Items
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <TargetTable items={targetItems} sortConfig={targetSortConfig} onSort={handleTargetSort} />
          </CardContent>
        </Card>
      </div>

      <BookingDialog
        open={bookingDialogOpen}
        onOpenChange={setBookingDialogOpen}
        items={selectedItems}
        onBookItems={handleBookItems}
        tolerancePercentage={settings.tolerancePercentage}
      />

      <SettingsDialog
        open={settingsDialogOpen}
        onOpenChange={setSettingsDialogOpen}
        settings={settings}
        onSaveSettings={handleSaveSettings}
      />

      {/* Inventory Correction Dialog */}
      {selectedItemForCorrection && (
        <InventoryCorrectionDialog
          open={correctionDialogOpen}
          onOpenChange={setCorrectionDialogOpen}
          item={selectedItemForCorrection}
          onConfirm={handleCorrectionConfirm}
        />
      )}
    </div>
  )
}

