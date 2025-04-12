"use client"

import React, { useState, useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { PicklistFilters } from "@/components/picklist-filters"
import { PicklistSearch } from "@/components/picklist-search"
import { PageSizeSelector } from "@/components/page-size-selector"
import { fetchOrders } from "@/lib/api"
import type { FilterType, PickingStatus, Order, PickingMethod } from "@/types/types"

// Add imports needed for the table
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  type ColumnDef,
  type VisibilityState,
  useReactTable,
  type Column,
  type Table as ReactTable,
  type Header,
  type Row,
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
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { useIsMobile } from "@/hooks/use-mobile"
import { OrderDetailView } from "@/components/order-detail-view"
import { ScanPopup } from "@/components/scan-popup"
import { PickingProcess } from "@/components/picking-process"
import { MultiPickingProcess } from "@/components/multi-picking-process"

// Reorder columns functionality
const DraggableColumnHeader = ({ header, table }: { header: Header<Order, unknown>; table: ReactTable<Order> }) => {
  const { id } = header.column // Destructure id here
  const { getState, setColumnOrder } = table // Destructure methods

  const [, drag] = useDrag({
    type: "COLUMN",
    item: { id },
  })

  const [, drop] = useDrop({
    accept: "COLUMN",
    drop: (item: { id: string }) => {
      const currentColumnOrder = getState().columnOrder
      const fromIndex = currentColumnOrder.indexOf(item.id)
      const toIndex = currentColumnOrder.indexOf(id) // Use destructured id

      if (fromIndex !== toIndex) {
        const newColumnOrder = [...currentColumnOrder]
        newColumnOrder.splice(fromIndex, 1)
        newColumnOrder.splice(toIndex, 0, item.id)
        setColumnOrder(newColumnOrder)
      }
    },
  })

  // Use React.RefCallback for ref handling
  const ref = React.useRef<HTMLDivElement>(null)
  drag(drop(ref))

  return (
    <div ref={ref} className="flex items-center cursor-move">
      {flexRender(header.column.columnDef.header, header.getContext())}
    </div>
  )
}

// Status badge component with semantic colors
const StatusBadge = ({ status }: { status: PickingStatus }) => {
  const statusConfig = {
    notStarted: { label: "Nicht begonnen", color: "bg-muted text-muted-foreground" },
    inProgress: { label: "In Bearbeitung", color: "bg-warning/10 text-warning-foreground" }, // Assuming warning colors exist
    completed: { label: "Abgeschlossen", color: "bg-success/10 text-success-foreground" }, // Assuming success colors exist
    problem: { label: "Problem", color: "bg-destructive/10 text-destructive-foreground" },
  }

  const config = statusConfig[status]

  // Apply base Badge variant styling and override with specific colors
  return <Badge variant="secondary" className={cn("font-medium", config.color)}>{config.label}</Badge>
}

export default function PicklistDashboard() {
  const [filterType, setFilterType] = useState<FilterType>("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<PickingStatus | "all">("all")
  const [pageSize, setPageSize] = useState(100)

  // Add state from PicklistTable
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
  const [selectedDeliveryDate, setSelectedDeliveryDate] = useState<string | "all">("all")

  const {
    data: allOrders = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["orders"],
    queryFn: fetchOrders,
  })

  // Filter all orders based on criteria
  const filteredOrders = useMemo(() => {
    return allOrders.filter((order) => {
      // Filter by type (orders, delivery notes, or both)
      if (filterType === "orders" && !order.isOrder) return false
      if (filterType === "deliveryNotes" && !order.isDeliveryNote) return false

      // Filter by status
      if (statusFilter !== "all" && order.pickingStatus !== statusFilter) return false

      // Search functionality
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        return (
          order.orderNumber.toLowerCase().includes(query) ||
          order.customerNumber.toLowerCase().includes(query) ||
          order.customerName.toLowerCase().includes(query)
        )
      }

      return true
    })
  }, [allOrders, filterType, statusFilter, searchQuery])

  // Apply pagination to filtered orders
  const displayedOrders = useMemo(() => {
    if (pageSize === 0) return filteredOrders // Show all
    return filteredOrders.slice(0, pageSize)
  }, [filteredOrders, pageSize])

  // Ermittle die Kundennummer des ersten ausgewählten Auftrags
  const selectedCustomerNumber = useMemo(() => {
    if (selectedOrderIds.length === 0) return null
    const firstSelectedOrder = allOrders.find((order) => order.id === selectedOrderIds[0]) // Use allOrders here
    return firstSelectedOrder ? firstSelectedOrder.customerNumber : null
  }, [selectedOrderIds, allOrders])

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
    const order = allOrders.find((o) => o.id === orderId) // Use allOrders
    if (!order) return

    setSelectedOrderIds((prev) => {
      // Wenn bereits Aufträge ausgewählt sind, prüfe die Kundennummer
      if (prev.length > 0 && !prev.includes(orderId)) {
        const firstSelectedOrder = allOrders.find((o) => o.id === prev[0]) // Use allOrders
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
    return allOrders.filter((order) => selectedOrderIds.includes(order.id))
  }, [allOrders, selectedOrderIds])

  const uniqueDeliveryDates = useMemo(() => {
    const dates = selectedOrders.map((order) => {
      const date = new Date(order.deliveryDate)
      // Ensure consistent date formatting if needed by MultiPickingProcess
      return format(date, "yyyy-MM-dd", { locale: de })
    })
    // Add 'all' option if the component requires it
    return ["all", ...Array.from(new Set(dates))]
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

  // --- Start Column Definition (Copied/Adapted from PicklistTable) ---
  const columns: ColumnDef<Order>[] = useMemo(
    () => [
      // Checkbox-Spalte für Mehrfach-Picking
      ...(isMultiPickingMode
        ? [
            {
              id: "select",
              header: ({ table }: { table: ReactTable<Order> }) => (
                <Checkbox
                  checked={
                    table.getRowModel().rows.length > 0 &&
                    table
                      .getRowModel()
                      .rows.every(
                        (row: Row<Order>) => selectedOrderIds.includes(row.original.id) || !isOrderSelectable(row.original),
                      )
                  }
                  onCheckedChange={(value) => {
                    if (value) {
                      const selectableOrderIds = table
                        .getRowModel()
                        .rows.filter((row: Row<Order>) => isOrderSelectable(row.original))
                        .map((row: Row<Order>) => row.original.id)
                      // Use Array.from to fix downlevelIteration error
                      setSelectedOrderIds((prev) => Array.from(new Set([...prev, ...selectableOrderIds])))
                    } else {
                      setSelectedOrderIds([])
                    }
                  }}
                  aria-label="Select all"
                />
              ),
              cell: ({ row }: { row: Row<Order> }) => {
                const isSelectable = isOrderSelectable(row.original)

                return (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="flex items-center justify-center">
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
                            <AlertCircle className="h-4 w-4 text-warning ml-1" />
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
            Datum
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        ),
        cell: ({ row }) => {
          const value = row.getValue("deliveryDate")
          if (!value || !(value instanceof Date) || isNaN(value.getTime())) {
            return "-"
          }
          return format(value as Date, "dd.MM.yyyy", { locale: de })
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

          // Determine semantic colors based on status
          const colorConfig = {
            notStarted: { text: "text-muted-foreground", bg: "bg-muted", indicator: "bg-muted-foreground" },
            inProgress: { text: "text-warning-foreground", bg: "bg-warning/10", indicator: "bg-warning" }, // Assuming warning colors exist
            completed: { text: "text-success-foreground", bg: "bg-success/10", indicator: "bg-success" }, // Assuming success colors exist
            problem: { text: "text-destructive-foreground", bg: "bg-destructive/10", indicator: "bg-destructive" },
          }

          const { text: textColor, bg: bgColor, indicator: indicatorColor } = colorConfig[pickingStatus]

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
                <div className={cn("w-2 h-2 rounded-full", indicatorColor)} />
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
          const value = row.getValue("orderDate")
          // Check if value is a valid date before formatting
          if (!value || !(value instanceof Date) || isNaN(value.getTime())) {
            return "-"
          }
          return format(value as Date, "dd.MM.yyyy", { locale: de })
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
  // --- End Column Definition ---

  // --- Start Table Instance (Copied/Adapted from PicklistTable) ---
  const table = useReactTable({
    data: displayedOrders, // Use displayedOrders which includes pagination
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
  // --- End Table Instance ---

  // Use the appropriate backend based on device
  const DndBackend = useIsMobile() ? TouchBackend : HTML5Backend

  if (error && error.name !== 'AbortError') {
    // Use destructive colors for error message
    return <div className="p-4 border border-destructive/20 bg-destructive/10 text-destructive rounded-md">Fehler beim Laden der Daten: {error.message}</div>
  }

  if (isLoading) {
    // Consistent loading indicator (optional, can use Suspense boundary)
    return (
        <div className="flex justify-center items-center p-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <span className="ml-3">Lade Pickliste...</span>
        </div>
      )
  }

  return (
    // Use Card component for overall structure
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            {/* Title and Description */}
            <div>
                <CardTitle className="text-2xl font-bold text-primary">Lager Pickliste</CardTitle>
                <CardDescription>Verwalten und bearbeiten Sie Picking-Aufträge.</CardDescription>
            </div>
            {/* Action Buttons (Example - Adapt if needed) */}
            <div className="flex gap-2 items-start">
              {/* Add relevant top-level actions here if needed, similar to Warehouse page */}
            </div>
        </div>
         {/* Filters and Search */}
        <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <PicklistFilters
            filterType={filterType}
            setFilterType={setFilterType}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            />
            <PicklistSearch searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Info and Pagination Controls */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-muted-foreground">
            {filteredOrders.length} Aufträge gefunden
            {filteredOrders.length > displayedOrders.length && ` (${displayedOrders.length} angezeigt)`}
          </div>
          <PageSizeSelector pageSize={pageSize} setPageSize={setPageSize} totalItems={filteredOrders.length} />
        </div>

        {/* Multi-Picking Controls */}
        <div className="flex justify-between items-center">
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
          // Use muted/info colors for hint box
          <div className="mb-4 p-3 bg-muted border border-border rounded-md">
            <p className="text-muted-foreground">
              <strong>Hinweis:</strong> Es können nur Aufträge mit der Kundennummer{" "}
              <strong>{selectedCustomerNumber}</strong> ausgewählt werden.
            </p>
          </div>
        )}

        {/* Table Rendering */}
        <DndProvider backend={DndBackend}>
          {/* Remove explicit bg-white, rely on Card styling */}
          <div className="rounded-md border overflow-hidden">
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
                          {row.getVisibleCells().map((cell) => {
                              // Special handling for checkbox cell content
                              if (cell.column.id === 'select') {
                                const isSelectable = isOrderSelectable(row.original)
                                return (
                                <TableCell key={cell.id}>
                                  <TooltipProvider>
                                    <Tooltip>
                                      <TooltipTrigger asChild>
                                        <div className="flex items-center justify-center"> {/* Center checkbox */}
                                          <Checkbox
                                            checked={selectedOrderIds.includes(row.original.id)}
                                            onCheckedChange={(value) => {
                                              if (isSelectable) {
                                                toggleOrderSelection(row.original.id)
                                              }
                                            }}
                                            onClick={(e) => e.stopPropagation()}
                                            disabled={!isSelectable && !selectedOrderIds.includes(row.original.id)}
                                            aria-label="Select row"
                                            className={!isSelectable && !selectedOrderIds.includes(row.original.id) ? "opacity-50" : ""}
                                          />
                                          {!isSelectable && !selectedOrderIds.includes(row.original.id) && (
                                            // Use warning color for the alert icon
                                            <AlertCircle className="h-4 w-4 text-warning ml-1" />
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
                                  </TableCell>
                                )
                              }
                             // Special handling for progress cell
                             if (cell.column.id === 'pickingProgress') {
                                const { itemsPicked, totalItems, pickingStatus } = row.original
                                const percentage = totalItems > 0 ? Math.round((itemsPicked / totalItems) * 100) : 0;

                                // Determine semantic colors based on status
                                const colorConfig = {
                                    notStarted: { text: "text-muted-foreground", bg: "bg-muted", indicator: "bg-muted-foreground" },
                                    inProgress: { text: "text-warning-foreground", bg: "bg-warning/10", indicator: "bg-warning" }, // Assuming warning colors exist
                                    completed: { text: "text-success-foreground", bg: "bg-success/10", indicator: "bg-success" }, // Assuming success colors exist
                                    problem: { text: "text-destructive-foreground", bg: "bg-destructive/10", indicator: "bg-destructive" },
                                };

                                const { text: textColor, bg: bgColor, indicator: indicatorColor } = colorConfig[pickingStatus];

                                return (
                                  <TableCell key={cell.id}>
                                    <div className="w-full max-w-[150px]">
                                      <div className="flex justify-between mb-1 text-xs">
                                        <span className={textColor}>
                                          {itemsPicked} / {totalItems} Items
                                        </span>
                                        <span className={textColor}>{percentage}%</span>
                                      </div>
                                      <div className="flex items-center gap-2">
                                         {/* Apply semantic background to Progress - remove indicatorClassName */}
                                        <Progress value={percentage} className={cn("h-2 flex-1", bgColor)} />
                                        {/* Use semantic color for the indicator dot */}
                                        <div className={cn("w-2 h-2 rounded-full", indicatorColor)} />
                                      </div>
                                    </div>
                                  </TableCell>
                                );
                            }
                            // Default rendering for other cells
                            return (
                                <TableCell key={cell.id}>
                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                </TableCell>
                            );
                        })}
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

        {/* --- Popups and Modals (Ensure consistency within these components if needed) --- */}
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
            currentOrderId && (
              <ScanPopup
                title="Schütte scannen"
                onClose={() => setShowScanPopup(false)}
                onSubmit={handleScanSubmit}
                onSkip={handleSkipScan}
                skipButtonText="Keine Schütte"
                placeholder="Schüttencode scannen..."
                orderNumber={currentOrderId}
                customerInfo={`${selectedCustomerNumber} ${selectedOrder?.customerName}`}
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
                // Reset delivery date filter after completion
                setSelectedDeliveryDate("all")
              }}
              onInterrupt={() => {
                setShowPickingProcess(false)
                setIsMultiPickingStarted(false)
              }}
              orders={selectedOrders} // Pass all selected orders
              filteredOrders={filteredSelectedOrders} // Pass orders filtered by date
              pickingMethod={pickingMethod}
              // Pass missing props
              uniqueDeliveryDates={uniqueDeliveryDates}
              selectedDeliveryDate={selectedDeliveryDate}
              onDeliveryDateChange={setSelectedDeliveryDate}
            />
          ) : (
            // Ensure selectedOrder is not null before rendering
            currentOrderId && selectedOrder && (
              <PickingProcess
                onClose={handlePickingInterrupt}
                onComplete={handlePickingComplete}
                // Revert to passing the full selectedOrder object
                order={selectedOrder}
                pickingMethod={pickingMethod}
              />
            )
          ))}
      </CardContent>
    </Card>
  )
}

