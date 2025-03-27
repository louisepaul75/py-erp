"use client"

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { FilterType, PickingStatus } from "@/types/types"

interface PicklistFiltersProps {
  filterType: FilterType
  setFilterType: (type: FilterType) => void
  statusFilter: PickingStatus | "all"
  setStatusFilter: (status: PickingStatus | "all") => void
}

export function PicklistFilters({ filterType, setFilterType, statusFilter, setStatusFilter }: PicklistFiltersProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
      <Tabs
        value={filterType}
        onValueChange={(value) => setFilterType(value as FilterType)}
        className="w-full sm:w-auto"
      >
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="all">Alle</TabsTrigger>
          <TabsTrigger value="orders">Aufträge</TabsTrigger>
          <TabsTrigger value="deliveryNotes">Lieferscheine</TabsTrigger>
        </TabsList>
      </Tabs>

      <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as PickingStatus | "all")}>
        <SelectTrigger className="w-full sm:w-[180px]">
          <SelectValue placeholder="Status Filter" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Alle Status</SelectItem>
          <SelectItem value="notStarted">Nicht begonnen</SelectItem>
          <SelectItem value="inProgress">In Bearbeitung</SelectItem>
          <SelectItem value="completed">Abgeschlossen</SelectItem>
          <SelectItem value="problem">Problem</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}

