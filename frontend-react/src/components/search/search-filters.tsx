"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { DocumentType } from "@/types/document/document"
import { Search, X } from "lucide-react"
import { useSearchParams, useRouter, usePathname } from "next/navigation"
import { DateRangePicker } from "@/components/search/date-range-picker"
import { useMediaQuery } from "@/hooks/document/use-media-query"

/**
 * SearchFilters component that displays filters for searching documents
 */
export function SearchFilters() {
  // Router and search params
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  // Get current filter values from URL only once during initialization
  const currentSearch = searchParams.get("search") || ""
  const currentType = searchParams.get("type") || ""
  const currentStatus = searchParams.get("status") || ""
  const currentCustomer = searchParams.get("customer") || ""
  const currentDateFrom = searchParams.get("dateFrom") || ""
  const currentDateTo = searchParams.get("dateTo") || ""

  // Local state for filter values
  const [search, setSearch] = useState(currentSearch)
  const [type, setType] = useState(currentType)
  const [status, setStatus] = useState(currentStatus)
  const [customer, setCustomer] = useState(currentCustomer)
  const [dateRange, setDateRange] = useState<{
    from?: Date
    to?: Date
  }>({
    from: currentDateFrom ? new Date(currentDateFrom) : undefined,
    to: currentDateTo ? new Date(currentDateTo) : undefined,
  })

  // Check if the device is a tablet or mobile
  const isTablet = useMediaQuery("(max-width: 1024px)")

  // Apply filters
  const applyFilters = () => {
    const params = new URLSearchParams()

    // Set or remove search parameter
    if (search) {
      params.set("search", search)
    }

    // Set or remove type parameter
    if (type) {
      params.set("type", type)
    }

    // Set or remove status parameter
    if (status) {
      params.set("status", status)
    }

    // Set or remove customer parameter
    if (customer) {
      params.set("customer", customer)
    }

    // Set or remove date range parameters
    if (dateRange.from) {
      params.set("dateFrom", dateRange.from.toISOString().split("T")[0])
    }

    if (dateRange.to) {
      params.set("dateTo", dateRange.to.toISOString().split("T")[0])
    }

    // Update URL with new parameters
    router.push(`${pathname}?${params.toString()}`)
  }

  // Reset filters
  const resetFilters = () => {
    setSearch("")
    setType("")
    setStatus("")
    setCustomer("")
    setDateRange({ from: undefined, to: undefined })

    // Remove all filter parameters from URL
    router.push(pathname)
  }

  // Get document type options
  const documentTypes: { value: DocumentType; label: string }[] = [
    { value: "ORDER", label: "Order" },
    { value: "DELIVERY", label: "Delivery Note" },
    { value: "INVOICE", label: "Invoice" },
    { value: "CREDIT", label: "Credit Note" },
  ]

  // Get status options
  const statusOptions = [
    { value: "OPEN", label: "Open" },
    { value: "COMPLETED", label: "Completed" },
    { value: "CANCELED", label: "Canceled" },
    { value: "PAID", label: "Paid" },
  ]

  // Mock customer data
  const customers = [
    { id: "1", name: "Acme Inc." },
    { id: "2", name: "Globex Corporation" },
    { id: "3", name: "Initech" },
    { id: "4", name: "Umbrella Corporation" },
    { id: "5", name: "Stark Industries" },
    { id: "6", name: "Wayne Enterprises" },
    { id: "7", name: "Cyberdyne Systems" },
    { id: "8", name: "Oscorp Industries" },
    { id: "9", name: "Massive Dynamic" },
    { id: "10", name: "Soylent Corp" },
  ]

  return (
    <div className="border rounded-md p-4 space-y-4">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search documents..."
              className="pl-8"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <Select value={type} onValueChange={setType}>
            <SelectTrigger>
              <SelectValue placeholder="Document Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All Types</SelectItem>
              {documentTypes.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All Statuses</SelectItem>
              {statusOptions.map((status) => (
                <SelectItem key={status.value} value={status.value}>
                  {status.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={customer} onValueChange={setCustomer}>
            <SelectTrigger>
              <SelectValue placeholder="Customer" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All Customers</SelectItem>
              {customers.map((customer) => (
                <SelectItem key={customer.id} value={customer.id}>
                  {customer.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <DateRangePicker value={dateRange} onChange={setDateRange} />
        </div>
      </div>

      <div className="flex justify-between">
        <Button variant="outline" size="sm" onClick={resetFilters}>
          <X className="h-4 w-4 mr-2" />
          Reset Filters
        </Button>
        <Button size="sm" onClick={applyFilters}>
          <Search className="h-4 w-4 mr-2" />
          Apply Filters
        </Button>
      </div>
    </div>
  )
}
