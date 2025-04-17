"use client"

import { useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DateRangePicker } from "@/components/ui/date-range-picker"
import { Download, ArrowLeft, Calendar, User, Package, ArrowRightLeft, ClipboardEdit, Filter } from "lucide-react"
import { Providers } from "@/components/providers"
import Link from "next/link"
import { useMobile } from "@/hooks/use-mobile"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import { useHistory } from "@/components/goods-movement/history-context"
import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select"

// Definiere die möglichen Aktionstypen
type ActionType = "all" | "movement" | "correction" | "excess" | "shortage"

function HistoryPageContent() {
  const isMobile = useMobile(768)
  const [searchTerm, setSearchTerm] = useState("")
  const [dateRange, setDateRange] = useState<{ from: Date | undefined; to: Date | undefined }>({
    from: undefined,
    to: undefined,
  })
  const [actionTypeFilter, setActionTypeFilter] = useState<ActionType>("all")

  const { historyEntries } = useHistory()

  // Filter by search term
  const searchFiltered = historyEntries.filter(
    (entry) =>
      entry.articleOld.includes(searchTerm) ||
      entry.articleNew.includes(searchTerm) ||
      entry.sourceSlot.includes(searchTerm) ||
      entry.targetSlot.includes(searchTerm) ||
      (entry.boxNumber && entry.boxNumber.includes(searchTerm)) ||
      (entry.orderNumber && entry.orderNumber.includes(searchTerm)),
  )

  // Filter by action type
  const actionFiltered = searchFiltered.filter((entry) => {
    if (actionTypeFilter === "all") return true
    if (actionTypeFilter === "movement" && !entry.correction) return true
    if (actionTypeFilter === "correction" && entry.correction?.type === "inventory_correction") return true
    if (actionTypeFilter === "excess" && entry.correction?.type === "excess") return true
    if (actionTypeFilter === "shortage" && entry.correction?.type === "shortage") return true
    return false
  })

  // Filter by date range
  const dateFilteredHistory = actionFiltered.filter((entry) => {
    const entryDate = new Date(entry.timestamp)
    if (dateRange.from && entryDate < dateRange.from) return false
    if (dateRange.to) {
      const toDateEnd = new Date(dateRange.to)
      toDateEnd.setHours(23, 59, 59, 999)
      if (entryDate > toDateEnd) return false
    }
    return true
  })

  // Sort by timestamp (newest first)
  const sortedHistory = [...dateFilteredHistory].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
  )

  const exportData = () => {
    // Implementation for exporting data
    alert("Export functionality would be implemented here")
  }

  // Mobile card view for history entries
  const renderMobileView = () => {
    if (sortedHistory.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center text-muted-foreground py-12">
          <Calendar className="h-8 w-8 mb-2 opacity-40" />
          <p>No history entries found</p>
        </div>
      )
    }

    return (
      <div className="space-y-3 pb-2 h-full overflow-auto">
        {sortedHistory.map((entry) => (
          <Card key={entry.id} className="overflow-hidden">
            <CardContent className="p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-1 text-muted-foreground" />
                  <span className="text-sm">{format(new Date(entry.timestamp), "MMM d, HH:mm")}</span>
                </div>
                <div className="flex items-center">
                  <User className="h-4 w-4 mr-1 text-muted-foreground" />
                  <span className="text-sm">{entry.user}</span>
                </div>
              </div>

              <div className="flex justify-between items-center mb-2">
                <div className="font-medium truncate mr-2">{entry.articleNew}</div>
                <Badge>{entry.quantity}</Badge>
              </div>

              <div className="flex items-center mb-2">
                <ArrowRightLeft className="h-4 w-4 mr-1 text-muted-foreground" />
                <span className="text-sm">
                  {entry.sourceSlot} → {entry.targetSlot}
                </span>
              </div>

              {(entry.boxNumber || entry.orderNumber) && (
                <div className="flex items-center text-sm text-muted-foreground mb-2">
                  <Package className="h-4 w-4 mr-1" />
                  <span>
                    {entry.boxNumber ? `Box: ${entry.boxNumber}` : ""}
                    {entry.orderNumber ? `Order: ${entry.orderNumber}` : ""}
                  </span>
                </div>
              )}

              {entry.correction && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {entry.correction.type === "inventory_correction" && (
                      <div className="flex items-center">
                        <ClipboardEdit className="h-3 w-3 mr-1" />
                        {entry.correction.oldQuantity} → {entry.correction.newQuantity}
                      </div>
                    )}
                    {entry.correction.reason}
                    {entry.correction.note ? `: ${entry.correction.note}` : ""}
                  </span>
                  <Badge
                    variant={
                      entry.correction.type === "excess"
                        ? "success"
                        : entry.correction.type === "shortage"
                          ? "destructive"
                          : "secondary"
                    }
                  >
                    {entry.correction.type === "inventory_correction"
                      ? "Korrektur"
                      : entry.correction.type === "excess"
                        ? "Überschuss"
                        : "Mangel"}
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  // Desktop table view for history entries
  const renderDesktopView = () => {
    return (
      <div className="rounded-md border overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Old Article</TableHead>
                <TableHead>New Article</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Source → Target</TableHead>
                <TableHead>Box/Order</TableHead>
                <TableHead>Type</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedHistory.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-4">
                    No history entries found
                  </TableCell>
                </TableRow>
              ) : (
                sortedHistory.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{new Date(entry.timestamp).toLocaleString()}</TableCell>
                    <TableCell>{entry.user}</TableCell>
                    <TableCell>{entry.articleOld}</TableCell>
                    <TableCell>{entry.articleNew}</TableCell>
                    <TableCell>
                      {entry.quantity}
                      {entry.correction?.type === "inventory_correction" && (
                        <span className="text-xs text-muted-foreground ml-1">
                          ({entry.correction.oldQuantity} → {entry.correction.newQuantity})
                        </span>
                      )}
                    </TableCell>
                    <TableCell>{`${entry.sourceSlot} → ${entry.targetSlot}`}</TableCell>
                    <TableCell>
                      {entry.boxNumber ? `Box: ${entry.boxNumber}` : ""}
                      {entry.orderNumber ? `Order: ${entry.orderNumber}` : ""}
                    </TableCell>
                    <TableCell>
                      {entry.correction ? (
                        <div className="flex flex-col gap-1">
                          <Badge
                            variant={
                              entry.correction.type === "excess"
                                ? "success"
                                : entry.correction.type === "shortage"
                                  ? "destructive"
                                  : "secondary"
                            }
                          >
                            {entry.correction.type === "inventory_correction"
                              ? "Korrektur"
                              : entry.correction.type === "excess"
                                ? "Überschuss"
                                : "Mangel"}
                          </Badge>
                          <span className="text-xs text-muted-foreground">{entry.correction.reason}</span>
                        </div>
                      ) : (
                        <Badge variant="outline">Bewegung</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl pb-20">
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between pb-2">
          <div className="flex items-center">
            <Link href="/" className="mr-4">
              <Button variant="outline" size="icon" className="h-8 w-8">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <CardTitle className="text-2xl">Movement History</CardTitle>
          </div>
          <Button onClick={exportData} className="whitespace-nowrap mt-2 sm:mt-0">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-grow">
              <Input
                placeholder="Search by article, slot, box or order number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <div className="flex gap-2">
              <Select value={actionTypeFilter} onValueChange={(value) => setActionTypeFilter(value as ActionType)}>
                <SelectTrigger className="w-[180px]">
                  <div className="flex items-center">
                    <Filter className="h-4 w-4 mr-2" />
                    <span>Filter by Type</span>
                  </div>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Actions</SelectItem>
                  <SelectItem value="movement">Movements</SelectItem>
                  <SelectItem value="correction">Corrections</SelectItem>
                  <SelectItem value="excess">Excess</SelectItem>
                  <SelectItem value="shortage">Shortage</SelectItem>
                </SelectContent>
              </Select>
              <DateRangePicker value={dateRange} onChange={setDateRange} />
            </div>
          </div>

          {isMobile ? renderMobileView() : renderDesktopView()}
        </CardContent>
      </Card>
    </div>
  )
}

export default function HistoryPage() {
  return (
    <Providers>
      <HistoryPageContent />
    </Providers>
  )
}

