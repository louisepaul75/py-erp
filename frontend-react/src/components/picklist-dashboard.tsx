"use client"

import { useState, useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { PicklistTable } from "@/components/picklist-table"
import { PicklistFilters } from "@/components/picklist-filters"
import { PicklistSearch } from "@/components/picklist-search"
import { PageSizeSelector } from "@/components/page-size-selector"
import { fetchOrders } from "@/lib/api"
import type { FilterType, PickingStatus } from "@/types/types"

export default function PicklistDashboard() {
  const [filterType, setFilterType] = useState<FilterType>("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<PickingStatus | "all">("all")
  const [pageSize, setPageSize] = useState(100)

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

  if (error) {
    return <div className="text-red-500">Fehler beim Laden der Daten: {error.message}</div>
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <PicklistFilters
          filterType={filterType}
          setFilterType={setFilterType}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
        />
        <PicklistSearch searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-sm text-muted-foreground">
          {filteredOrders.length} Aufträge gefunden
          {filteredOrders.length > displayedOrders.length && ` (${displayedOrders.length} angezeigt)`}
        </div>
        <PageSizeSelector pageSize={pageSize} setPageSize={setPageSize} totalItems={filteredOrders.length} />
      </div>

      <PicklistTable orders={displayedOrders} isLoading={isLoading} totalOrders={filteredOrders.length} />
    </div>
  )
}

