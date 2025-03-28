"use client"

import { useState, useMemo } from "react"
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  type ColumnDef,
  type VisibilityState,
  useReactTable,
} from "@tanstack/react-table"
import { DndProvider, useDrag, useDrop } from "react-dnd"
import { HTML5Backend } from "react-dnd-html5-backend"
import { TouchBackend } from "react-dnd-touch-backend"
import { ArrowUpDown, MoreHorizontal, CheckSquare, AlertCircle, X } from "lucide-react"
import { format } from "date-fns"
import { de } from "date-fns/locale"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuPortal,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Checkbox } from "@/components/ui/checkbox"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import type { Order, PickingMethod, PickingStatus } from "@/types/types"
import { cn } from "@/lib/utils"
import { useIsMobile } from "@/hooks/use-mobile"
import { OrderDetailView } from "@/components/order-detail-view"
import { ScanPopup } from "@/components/scan-popup"
import { PickingProcess } from "@/components/picking-process"
import { MultiPickingProcess } from "@/components/multi-picking-process"

// Reorder columns functionality
const DraggableColumnHeader = ({ header, table }) => {
  const [, drag] = useDrag({
    type: "COLUMN",
    item: { id: header.id },
  })

  const [, drop] = useDrop({
    accept: "COLUMN",
    drop: (item: { id: string }) => {
      const currentColumnOrder = table.getState().columnOrder
      const fromIndex = currentColumnOrder.indexOf(item.id)
      const toIndex = currentColumnOrder.indexOf(header.id)

      if (fromIndex !== toIndex) {
        const newColumnOrder = [...currentColumnOrder]
        newColumnOrder.splice(fromIndex, 1)
        newColumnOrder.splice(toIndex, 0, item.id)
        table.setColumnOrder(newColumnOrder)
      }
    },
  })

  return (
    <div ref={(node) => drag(drop(node))} className="flex items-center cursor-move">
      {flexRender(header.column.columnDef.header, header.getContext())}
    </div>
  )
}

// Status badge component with color matching
const StatusBadge = ({ status }: { status: PickingStatus }) => {
  const statusConfig = {
    notStarted: { label: "Nicht begonnen", color: "text-gray-600 bg-gray-100" },
    inProgress: { label: "In Bearbeitung", color: "text-yellow-600 bg-yellow-100" },
    completed: { label: "Abgeschlossen", color: "text-green-600 bg-green-100" },
    problem: { label: "Problem", color: "text-red-600 bg-red-100" },
  }

  const config = statusConfig[status]

  return <Badge className={cn("font-medium", config.color)}>{config.label}</Badge>
}

interface PicklistTableProps {
  orders: Order[]
  isLoading: boolean
  totalOrders: number
}

export function PicklistTable({ orders, isLoading, totalOrders }: PicklistTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [columnOrder, setColumnOrder] = useState<string[]>([
    "deliveryDate",
    "orderNumber",
    "customerNumber",
    "customerName",
    "pickingProgress",
    "pickingStatus",
    "orderDate",
    "pickingSequence",
  ])
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [showScanPopup, setShowScanPopup] = useState(false)
  const [showPickingProcess, setShowPickingProcess] = useState(false)
  const [currentOrderId, setCurrentOrderId] = useState<string | null>(null)
  const [pickingMethod, setPickingMethod] = useState<PickingMethod>("manual")
  const [scannedBin, setScannedBin] = useState<string | null>(null)
  const [showPickingMethodSelector, setShowPickingMethodSelector] = useState(false)

  // Mehrfach-Picking-States
  const [isMultiPickingMode, setIsMultiPickingMode] = useState(false)
  const [selectedOrderIds, setSelectedOrderIds] = useState<string[]>([])
  const [isMultiPickingStarted, setIsMultiPickingStarted] = useState(false)
  const [selectedDeliveryDate, setSelectedDeliveryDate] = useState<string | null>("past")

  // Ermittle die Kundennummer des ersten ausgewählten Auftrags
  const selectedCustomerNumber = useMemo(() => {
    if (selectedOrderIds.length === 0) return null
    const firstSelectedOrder = orders.find((order) => order.id === selectedOrderIds[0])
    return firstSelectedOrder ? firstSelectedOrder.customerNumber : null
  }, [selectedOrderIds, orders])

  const handleRowClick = (order: Order) => {
    if (isMultiPickingMode) {
      // Im Mehrfach-Picking-Modus wird die Checkbox umgeschaltet
      toggleOrderSelection(order.id)
    } else {
      // Im normalen Modus wird die Detailansicht geöffnet
      setSelectedOrder(order)
    }
  }

  const handleCloseDetail = () => {
    setSelectedOrder(null)
  }

  const handleStartPicking = (orderId: string, method: PickingMethod) => {
    setCurrentOrderId(orderId)
    setPickingMethod(method)
    setShowScanPopup(true)
  }

  const handleScanSubmit = (binCode: string) => {
    console.log(
      `Scanning bin code: ${binCode} for ${isMultiPickingMode ? "multi-picking" : `order ${currentOrderId}`} using ${pickingMethod} method`,
    )
    setScannedBin(binCode)
    setShowScanPopup(false)

    if (isMultiPickingMode) {
      setIsMultiPickingStarted(true)
    }

    setShowPickingProcess(true)
  }

  const handleSkipScan = () => {
    console.log(`Starting ${isMultiPickingMode ? "multi-picking" : `picking for order ${currentOrderId}`} without bin`)
    setScannedBin(null)
    setShowScanPopup(false)

    if (isMultiPickingMode) {
      setIsMultiPickingStarted(true)
    }

    setShowPickingProcess(true)
  }

  const handleTare = () => {
    console.log("Waage wird tariert...")
    // Hier würde die tatsächliche Tarierungs-Logik implementiert werden
  }

  const handlePickingComplete = () => {
    console.log(`Picking completed for order ${currentOrderId}`)
    setShowPickingProcess(false)
    // Hier würde die Logik für den Abschluss des Pickings implementiert werden
  }

  const handlePickingInterrupt = () => {
    console.log(`Picking interrupted for order ${currentOrderId}`)
    setShowPickingProcess(false)
    // Hier würde die Logik für die Unterbrechung des Pickings implementiert werden
  }

  // Mehrfach-Picking-Funktionen
  const toggleMultiPickingMode = () => {
    setIsMultiPickingMode(!isMultiPickingMode)
    if (isMultiPickingMode) {
      // Wenn der Modus deaktiviert wird, alle Auswahlen zurücksetzen
      setSelectedOrderIds([])
    }
  }

  const toggleOrderSelection = (orderId: string) => {
    const order = orders.find((o) => o.id === orderId)
    if (!order) return

    setSelectedOrderIds((prev) => {
      // Wenn bereits Aufträge ausgewählt sind, prüfe die Kundennummer
      if (prev.length > 0 && !prev.includes(orderId)) {
        const firstSelectedOrder = orders.find((o) => o.id === prev[0])
        if (firstSelectedOrder && firstSelectedOrder.customerNumber !== order.customerNumber) {
          // Wenn die Kundennummer nicht übereinstimmt, nicht hinzufügen
          return prev
        }
      }

      // Wenn der Auftrag bereits ausgewählt ist, entferne ihn
      if (prev.includes(orderId)) {
        return prev.filter((id) => id !== orderId)
      }
      // Sonst füge ihn hinzu
      else {
        return [...prev, orderId]
      }
    })
  }

  const startMultiPicking = () => {
    if (selectedOrderIds.length > 0) {
      // Zeige zuerst die Auswahl für die Picking-Methode an
      setShowPickingMethodSelector(true)
    }
  }

  const handlePickingMethodSelect = (method: PickingMethod) => {
    setPickingMethod(method)
    setShowPickingMethodSelector(false)
    // Dann das Scan-Popup anzeigen
    setShowScanPopup(true)
  }

  // Prüfe, ob ein Auftrag auswählbar ist (gleiche Kundennummer)
  const isOrderSelectable = (order: Order) => {
    if (selectedOrderIds.length === 0) return true
    return selectedCustomerNumber === order.customerNumber
  }

  // Extrahiere alle einzigartigen Liefertermine aus den ausgewählten Aufträgen
  const selectedOrders = useMemo(() => {
    return orders.filter((order) => selectedOrderIds.includes(order.id))
  }, [orders, selectedOrderIds])

  const uniqueDeliveryDates = useMemo(() => {
    const dates = selectedOrders.map((order) => {
      const date = new Date(order.deliveryDate)
      return format(date, "yyyy-MM-dd")
    })
    return Array.from(new Set(dates))
  }, [selectedOrders])

  // Filtere die ausgewählten Aufträge nach dem ausgewählten Lieferdatum
  const filteredSelectedOrders = useMemo(() => {
    if (!selectedDeliveryDate || selectedDeliveryDate === "all") {
      return selectedOrders
    }

    const today = new Date()
    today.setHours(0, 0, 0, 0)

    if (selectedDeliveryDate === "past") {
      return selectedOrders.filter((order) => {
        const deliveryDate = new Date(order.deliveryDate)
        deliveryDate.setHours(0, 0, 0, 0)
        return deliveryDate < today
      })
    }

    return selectedOrders.filter((order) => {
      const formattedDate = format(new Date(order.deliveryDate), "yyyy-MM-dd")
      return formattedDate === selectedDeliveryDate
    })
  }, [selectedOrders, selectedDeliveryDate])

  const columns: ColumnDef<Order>[] = useMemo(
    () => [
      // Checkbox-Spalte für Mehrfach-Picking
      ...(isMultiPickingMode
        ? [
            {
              id: "select",
              header: ({ table }) => (
                <Checkbox
                  checked={
                    table.getRowModel().rows.length > 0 &&
                    table
                      .getRowModel()
                      .rows.every(
                        (row) => selectedOrderIds.includes(row.original.id) || !isOrderSelectable(row.original),
                      )
                  }
                  onCheckedChange={(value) => {
                    if (value) {
                      // Nur auswählbare Aufträge hinzufügen
                      const selectableOrderIds = table
                        .getRowModel()
                        .rows.filter((row) => isOrderSelectable(row.original))
                        .map((row) => row.original.id)
                      setSelectedOrderIds((prev) => [...new Set([...prev, ...selectableOrderIds])])
                    } else {
                      setSelectedOrderIds([])
                    }
                  }}
                  aria-label="Select all"
                />
              ),
              cell: ({ row }) => {
                const isSelectable = isOrderSelectable(row.original)

                return (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="flex items-center">
                          <Checkbox
                            checked={selectedOrderIds.includes(row.original.id)}
                            onCheckedChange={(value) => {
                              if (isSelectable) {
                                if (value) {
                                  toggleOrderSelection(row.original.id)
                                } else {
                                  toggleOrderSelection(row.original.id)
                                }
                              }
                            }}
                            onClick={(e) => e.stopPropagation()}
                            disabled={!isSelectable && !selectedOrderIds.includes(row.original.id)}
                            aria-label="Select row"
                            className={!isSelectable && !selectedOrderIds.includes(row.original.id) ? "opacity-50" : ""}
                          />
                          {!isSelectable && !selectedOrderIds.includes(row.original.id) && (
                            <AlertCircle className="h-4 w-4 text-amber-500 ml-1" />
                          )}
                        </div>
                      </TooltipTrigger>
                      {!isSelectable && !selectedOrderIds.includes(row.original.id) && (
                        <TooltipContent>
                          <p>Nur Aufträge mit der Kundennummer {selectedCustomerNumber} können ausgewählt werden</p>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  </TooltipProvider>
                )
              },
              enableSorting: false,
              enableHiding: false,
            },
          ]
        : []),
      {
        accessorKey: "deliveryDate",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Lieferdatum
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          const value = row.getValue("deliveryDate");
          // Check if value is a valid date before formatting
          if (!value || !(value instanceof Date) || isNaN(value.getTime())) {
            return "-";
          }
          return format(value as Date, "dd.MM.yyyy", { locale: de });
        },
      },
      {
        accessorKey: "orderNumber",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Auftragsnummer
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
      },
      {
        accessorKey: "customerNumber",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Kundennummer
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
      },
      {
        accessorKey: "customerName",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Kundenname
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
      },
      {
        accessorKey: "pickingProgress",
        header: "Fortschritt",
        cell: ({ row }) => {
          const { itemsPicked, totalItems, pickingStatus } = row.original
          const percentage = Math.round((itemsPicked / totalItems) * 100)

          // Determine color based on status
          const colorMap = {
            notStarted: "text-gray-600",
            inProgress: "text-yellow-600",
            completed: "text-green-600",
            problem: "text-red-600",
          }

          const textColor = colorMap[pickingStatus]
          const bgColor = {
            notStarted: "bg-gray-100",
            inProgress: "bg-yellow-100",
            completed: "bg-green-100",
            problem: "bg-red-100",
          }[pickingStatus]

          return (
            <div className="w-full max-w-[150px]">
              <div className="flex justify-between mb-1 text-xs">
                <span className={textColor}>
                  {itemsPicked} / {totalItems} Items
                </span>
                <span className={textColor}>{percentage}%</span>
              </div>
              <div className="flex items-center gap-2">
                <Progress value={percentage} className={cn("h-2 flex-1", bgColor)} />
                <div
                  className={cn(
                    "w-2 h-2 rounded-full",
                    pickingStatus === "completed" && "bg-green-500",
                    pickingStatus === "inProgress" && "bg-yellow-500",
                    pickingStatus === "notStarted" && "bg-gray-500",
                    pickingStatus === "problem" && "bg-red-500",
                  )}
                />
              </div>
            </div>
          )
        },
      },
      {
        accessorKey: "pickingStatus",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Status
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          return <StatusBadge status={row.getValue("pickingStatus") as PickingStatus} />
        },
      },
      {
        accessorKey: "orderDate",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Auftragsdatum
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          const value = row.getValue("orderDate");
          // Check if value is a valid date before formatting
          if (!value || !(value instanceof Date) || isNaN(value.getTime())) {
            return "-";
          }
          return format(value as Date, "dd.MM.yyyy", { locale: de });
        },
      },
      {
        accessorKey: "pickingSequence",
        header: ({ column }) => (
          <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Reihenfolge
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          return <span className="font-medium">{row.getValue("pickingSequence")}</span>
        },
      },
      {
        id: "actions",
        cell: ({ row }) => {
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Menü öffnen</span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRowClick(row.original)
                  }}
                >
                  Details anzeigen
                </DropdownMenuItem>
                <DropdownMenuSub>
                  <DropdownMenuSubTrigger>Picking starten</DropdownMenuSubTrigger>
                  <DropdownMenuPortal>
                    <DropdownMenuSubContent>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStartPicking(row.original.id, "manual")
                        }}
                      >
                        Manuelles Picking
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStartPicking(row.original.id, "scale")
                        }}
                      >
                        Picking mit Waage
                      </DropdownMenuItem>
                    </DropdownMenuSubContent>
                  </DropdownMenuPortal>
                </DropdownMenuSub>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
    ],
    [isMultiPickingMode, selectedOrderIds, selectedCustomerNumber],
  )

  const table = useReactTable({
    data: orders,
    columns,
    state: {
      sorting,
      columnVisibility,
      columnOrder,
    },
    onSortingChange: setSorting,
    onColumnVisibilityChange: setColumnVisibility,
    onColumnOrderChange: setColumnOrder,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  // Use the appropriate backend based on device
  const DndBackend = useIsMobile() ? TouchBackend : HTML5Backend

  if (isLoading) {
    return <div>Daten werden geladen...</div>
  }

  // Finde den aktuellen Auftrag
  const currentOrder = currentOrderId ? orders.find((o) => o.id === currentOrderId) : null

  // Finde die gescannte Schütte
  const scannedBinLocation =
    currentOrder && scannedBin ? currentOrder.binLocations.find((bin) => bin.binCode === scannedBin) : null

  return (
    <>
      <div className="mb-4 flex justify-between items-center">
        <Button
          variant={isMultiPickingMode ? "default" : "outline"}
          onClick={toggleMultiPickingMode}
          className="flex items-center gap-2"
        >
          <CheckSquare className="h-4 w-4" />
          {isMultiPickingMode ? "Mehrfach-Picking beenden" : "Mehrfach-Picking"}
        </Button>

        {isMultiPickingMode && (
          <Button onClick={startMultiPicking} disabled={selectedOrderIds.length === 0} className="ml-2">
            Ausgewählte Aufträge picken ({selectedOrderIds.length})
          </Button>
        )}
      </div>

      {isMultiPickingMode && selectedCustomerNumber && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-blue-700">
            <strong>Hinweis:</strong> Es können nur Aufträge mit der Kundennummer{" "}
            <strong>{selectedCustomerNumber}</strong> ausgewählt werden.
          </p>
        </div>
      )}

      <DndProvider backend={DndBackend}>
        <div className="rounded-md border bg-white overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <TableHead key={header.id} className="whitespace-nowrap">
                        {header.isPlaceholder ? null : <DraggableColumnHeader header={header} table={table} />}
                      </TableHead>
                    ))}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows?.length ? (
                  table.getRowModel().rows.map((row) => {
                    const isSelectable = isOrderSelectable(row.original)
                    return (
                      <TableRow
                        key={row.id}
                        data-state={row.getIsSelected() && "selected"}
                        className={cn(
                          "cursor-pointer hover:bg-muted/50",
                          isMultiPickingMode && !isSelectable && !selectedOrderIds.includes(row.original.id)
                            ? "opacity-50"
                            : "",
                        )}
                        onClick={() => handleRowClick(row.original)}
                      >
                        {row.getVisibleCells().map((cell) => (
                          <TableCell key={cell.id}>
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </TableCell>
                        ))}
                      </TableRow>
                    )
                  })
                ) : (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="h-24 text-center">
                      Keine Ergebnisse gefunden.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </DndProvider>

      {/* Picking-Methode Auswahl für Mehrfach-Picking */}
      {showPickingMethodSelector && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
          <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Picking-Methode auswählen</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowPickingMethodSelector(false)}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Schließen</span>
              </Button>
            </div>

            <div className="space-y-6">
              <p className="text-center">Bitte wählen Sie die Picking-Methode für die ausgewählten Aufträge:</p>

              <RadioGroup
                value={pickingMethod}
                onValueChange={(value) => setPickingMethod(value as PickingMethod)}
                className="flex flex-col space-y-4"
              >
                <div className="flex items-center space-x-2 border rounded-md p-4">
                  <RadioGroupItem value="manual" id="manual-multi" />
                  <Label htmlFor="manual-multi" className="flex-1 cursor-pointer">
                    Manuelles Picking
                  </Label>
                </div>
                <div className="flex items-center space-x-2 border rounded-md p-4">
                  <RadioGroupItem value="scale" id="scale-multi" />
                  <Label htmlFor="scale-multi" className="flex-1 cursor-pointer">
                    Picking mit Waage
                  </Label>
                </div>
              </RadioGroup>

              <Button onClick={() => handlePickingMethodSelect(pickingMethod)} className="w-full">
                Weiter
              </Button>
            </div>
          </div>
        </div>
      )}

      {selectedOrder && (
        <OrderDetailView
          order={selectedOrder}
          onClose={handleCloseDetail}
          onStartPicking={(orderId, method) => handleStartPicking(orderId, method)}
        />
      )}

      {showScanPopup &&
        (isMultiPickingMode ? (
          <ScanPopup
            title="Schütte für Mehrfach-Picking scannen"
            onClose={() => setShowScanPopup(false)}
            onSubmit={handleScanSubmit}
            onSkip={handleSkipScan}
            skipButtonText="Keine Schütte"
            placeholder="Schüttencode scannen..."
            orderNumber={`${selectedOrderIds.length} Aufträge ausgewählt`}
            customerInfo={selectedCustomerNumber ? `Kundennummer: ${selectedCustomerNumber}` : ""}
            pickingMethod={pickingMethod}
            onTare={handleTare}
          />
        ) : (
          currentOrder && (
            <ScanPopup
              title="Schütte scannen"
              onClose={() => setShowScanPopup(false)}
              onSubmit={handleScanSubmit}
              onSkip={handleSkipScan}
              skipButtonText="Keine Schütte"
              placeholder="Schüttencode scannen..."
              orderNumber={currentOrder.orderNumber}
              customerInfo={`${currentOrder.customerNumber} ${currentOrder.customerName}`}
              pickingMethod={pickingMethod}
              onTare={handleTare}
            />
          )
        ))}

      {showPickingProcess &&
        (isMultiPickingStarted ? (
          <MultiPickingProcess
            onClose={() => {
              setShowPickingProcess(false)
              setIsMultiPickingStarted(false)
            }}
            onComplete={() => {
              setShowPickingProcess(false)
              setIsMultiPickingStarted(false)
              setIsMultiPickingMode(false)
              setSelectedOrderIds([])
            }}
            onInterrupt={() => {
              setShowPickingProcess(false)
              setIsMultiPickingStarted(false)
            }}
            orders={selectedOrders}
            uniqueDeliveryDates={uniqueDeliveryDates}
            onDeliveryDateChange={setSelectedDeliveryDate}
            selectedDeliveryDate={selectedDeliveryDate}
            filteredOrders={filteredSelectedOrders}
            pickingMethod={pickingMethod}
          />
        ) : (
          currentOrder && (
            <PickingProcess
              onClose={() => setShowPickingProcess(false)}
              onComplete={handlePickingComplete}
              onInterrupt={handlePickingInterrupt}
              orderNumber={currentOrder.orderNumber}
              customerInfo={`${currentOrder.customerNumber} ${currentOrder.customerName}`}
              items={currentOrder.items}
              binLocations={currentOrder.binLocations}
              initialBinLocation={scannedBinLocation}
              pickingMethod={pickingMethod}
            />
          )
        ))}
    </>
  )
}

