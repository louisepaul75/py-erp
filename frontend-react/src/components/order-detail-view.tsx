"use client"

import { useState, useMemo } from "react"
import { format } from "date-fns"
import { de } from "date-fns/locale"
import { X, Search, CheckCircle2, Clock } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { Order, PickingMethod } from "@/types/types"
import { PageSizeSelector } from "@/components/page-size-selector"
import { cn } from "@/lib/utils"

interface OrderDetailViewProps {
  order: Order
  onClose: () => void
  onStartPicking: (orderId: string, method: PickingMethod) => void
}

export function OrderDetailView({ order, onClose, onStartPicking }: OrderDetailViewProps) {
  const [pickingMethod, setPickingMethod] = useState<PickingMethod>("manual")
  const [articleSearch, setArticleSearch] = useState("")
  const [articlePageSize, setArticlePageSize] = useState(100)

  const statusConfig = {
    notStarted: { label: "Nicht begonnen", color: "text-gray-600 bg-gray-100" },
    inProgress: { label: "In Bearbeitung", color: "text-yellow-600 bg-yellow-100" },
    completed: { label: "Abgeschlossen", color: "text-green-600 bg-green-100" },
    problem: { label: "Problem", color: "text-red-600 bg-red-100" },
  }

  // Filter articles based on search
  const filteredArticles = useMemo(() => {
    if (!articleSearch) return order.items

    const search = articleSearch.toLowerCase()
    return order.items.filter(
      (item) =>
        item.oldArticleNumber.toLowerCase().includes(search) ||
        item.newArticleNumber.toLowerCase().includes(search) ||
        item.description.toLowerCase().includes(search),
    )
  }, [order.items, articleSearch])

  // Apply pagination to filtered articles
  const displayedArticles = useMemo(() => {
    if (articlePageSize === 0) return filteredArticles // Show all
    return filteredArticles.slice(0, articlePageSize)
  }, [filteredArticles, articlePageSize])

  const handleStartPicking = () => {
    onStartPicking(order.id, pickingMethod)
  }

  const totalProgress = Math.round((order.itemsPicked / order.totalItems) * 100)

  // Function to get bin information for an item
  const getItemBins = (itemBinIds: string[]) => {
    if (!itemBinIds.length) return []

    return itemBinIds
      .map((binId) => {
        return order.binLocations.find((bin) => bin.id === binId)
      })
      .filter(Boolean)
  }

  // Get status color
  const statusColor = statusConfig[order.pickingStatus].color

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm">
      <div className="fixed inset-0 z-50 flex items-start justify-center sm:items-center">
        <div className="flex flex-col w-full max-w-4xl max-h-[90vh] bg-background border rounded-lg shadow-lg">
          <div className="flex items-center justify-between p-4 border-b">
            <h2 className="text-xl font-semibold">
              {order.isOrder ? "Auftrag" : "Lieferschein"}: {order.orderNumber}
            </h2>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
              <span className="sr-only">Schließen</span>
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Bin Locations - Moved to the very top */}
            <Card className="border-2 border-primary">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Schütten</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border overflow-hidden">
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Schüttencode</TableHead>
                          <TableHead>Location</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {order.binLocations.length > 0 ? (
                          order.binLocations.map((bin, index) => (
                            <TableRow key={index}>
                              <TableCell>{bin.binCode}</TableCell>
                              <TableCell>{bin.location}</TableCell>
                            </TableRow>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={2} className="text-center py-4">
                              Keine Schütten zugewiesen
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Order Header Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Auftragsinformationen</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="grid grid-cols-2 gap-1">
                    <div className="font-medium">Auftragsnummer:</div>
                    <div>{order.orderNumber}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    <div className="font-medium">Auftragsdatum:</div>
                    <div>{format(order.orderDate, "dd.MM.yyyy", { locale: de })}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    <div className="font-medium">Lieferdatum:</div>
                    <div>{format(order.deliveryDate, "dd.MM.yyyy", { locale: de })}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    <div className="font-medium">Status:</div>
                    <div>
                      <Badge className={cn("font-medium", statusColor)}>
                        {statusConfig[order.pickingStatus].label}
                      </Badge>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    <div className="font-medium">Fortschritt:</div>
                    <div className="w-full">
                      <div className="flex justify-between mb-1 text-xs">
                        <span className={statusColor.split(" ")[0]}>
                          {order.itemsPicked} / {order.totalItems} Items
                        </span>
                        <span className={statusColor.split(" ")[0]}>{totalProgress}%</span>
                      </div>
                      <Progress value={totalProgress} className={cn("h-2", statusColor.split(" ")[1])} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Kundeninformationen</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="grid grid-cols-2 gap-1">
                    <div className="font-medium">Kundennummer:</div>
                    <div>{order.customerNumber}</div>
                  </div>
                  <div className="grid grid-cols-2 gap-1">
                    <div className="font-medium">Kundenname:</div>
                    <div>{order.customerName}</div>
                  </div>
                  {order.customerAddress && (
                    <div className="grid grid-cols-2 gap-1">
                      <div className="font-medium">Adresse:</div>
                      <div>{order.customerAddress}</div>
                    </div>
                  )}
                  {order.contactPerson && (
                    <div className="grid grid-cols-2 gap-1">
                      <div className="font-medium">Kontaktperson:</div>
                      <div>{order.contactPerson}</div>
                    </div>
                  )}
                  {order.phoneNumber && (
                    <div className="grid grid-cols-2 gap-1">
                      <div className="font-medium">Telefon:</div>
                      <div>{order.phoneNumber}</div>
                    </div>
                  )}
                  {order.email && (
                    <div className="grid grid-cols-2 gap-1">
                      <div className="font-medium">E-Mail:</div>
                      <div>{order.email}</div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Picking Method and Start Button - MOVED UP */}
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-between bg-gray-50 p-4 rounded-lg border">
              <RadioGroup
                value={pickingMethod}
                onValueChange={(value) => setPickingMethod(value as PickingMethod)}
                className="flex flex-row space-x-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="manual" id="manual" />
                  <Label htmlFor="manual">Manuelles Picking</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="scale" id="scale" />
                  <Label htmlFor="scale">Picking mit Waage</Label>
                </div>
              </RadioGroup>

              <Button
                onClick={handleStartPicking}
                disabled={order.pickingStatus === "completed"}
                className="w-full sm:w-auto"
              >
                Picking starten
              </Button>
            </div>

            {/* Items Table */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Artikel</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-4">
                  <div className="flex flex-col sm:flex-row gap-4 justify-between">
                    <div className="relative w-full sm:w-[300px]">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        type="search"
                        placeholder="Artikel suchen..."
                        className="pl-8"
                        value={articleSearch}
                        onChange={(e) => setArticleSearch(e.target.value)}
                      />
                    </div>
                    <div className="flex items-center justify-between sm:justify-end gap-4">
                      <div className="text-sm text-muted-foreground">
                        {filteredArticles.length} Artikel gefunden
                        {filteredArticles.length > displayedArticles.length &&
                          ` (${displayedArticles.length} angezeigt)`}
                      </div>
                      <PageSizeSelector
                        pageSize={articlePageSize}
                        setPageSize={setArticlePageSize}
                        totalItems={filteredArticles.length}
                      />
                    </div>
                  </div>

                  <div className="rounded-md border overflow-hidden">
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Status</TableHead>
                            <TableHead>Alte Artikelnr.</TableHead>
                            <TableHead>Neue Artikelnr.</TableHead>
                            <TableHead>Bezeichnung</TableHead>
                            <TableHead>Fortschritt</TableHead>
                            <TableHead>Schütten</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {displayedArticles.length > 0 ? (
                            displayedArticles.map((item) => {
                              const itemBins = getItemBins(item.binLocations)
                              const isFullyPicked = item.quantityPicked === item.quantityTotal
                              const isPartiallyPicked = item.quantityPicked > 0 && !isFullyPicked
                              const isNotPicked = item.quantityPicked === 0

                              // Determine color based on picking status
                              const itemColor = isFullyPicked
                                ? "text-green-600"
                                : isPartiallyPicked
                                  ? "text-yellow-600"
                                  : "text-gray-600"

                              const itemBgColor = isFullyPicked
                                ? "bg-green-100"
                                : isPartiallyPicked
                                  ? "bg-yellow-100"
                                  : "bg-gray-100"

                              return (
                                <TableRow key={item.id}>
                                  <TableCell>
                                    <div
                                      className={cn(
                                        "flex items-center justify-center w-6 h-6 rounded-full",
                                        itemBgColor,
                                      )}
                                    >
                                      {isFullyPicked && <CheckCircle2 className="h-4 w-4 text-green-600" />}
                                      {isPartiallyPicked && <CheckCircle2 className="h-4 w-4 text-yellow-600" />}
                                      {isNotPicked && <Clock className="h-4 w-4 text-gray-600" />}
                                    </div>
                                  </TableCell>
                                  <TableCell>{item.oldArticleNumber}</TableCell>
                                  <TableCell>{item.newArticleNumber}</TableCell>
                                  <TableCell>{item.description}</TableCell>
                                  <TableCell>
                                    <div className="flex flex-col gap-1 min-w-[120px]">
                                      <span className={itemColor}>
                                        {item.quantityPicked} / {item.quantityTotal}
                                      </span>
                                      <Progress
                                        value={(item.quantityPicked / item.quantityTotal) * 100}
                                        className={cn("h-2 w-full", itemBgColor)}
                                      />
                                    </div>
                                  </TableCell>
                                  <TableCell>
                                    <div className="flex flex-col gap-2">
                                      {itemBins.length > 0 ? (
                                        itemBins.map(
                                          (bin, index) =>
                                            bin && (
                                              <div key={index} className="flex flex-col">
                                                <Badge variant="outline" className="mb-1">
                                                  {bin.binCode}
                                                </Badge>
                                                <span className="text-xs text-muted-foreground">
                                                  Location: {bin.location}
                                                </span>
                                              </div>
                                            ),
                                        )
                                      ) : (
                                        <span className="text-muted-foreground text-sm">Keine Schütte</span>
                                      )}
                                    </div>
                                  </TableCell>
                                </TableRow>
                              )
                            })
                          ) : (
                            <TableRow>
                              <TableCell colSpan={6} className="text-center py-4">
                                Keine Artikel gefunden
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

