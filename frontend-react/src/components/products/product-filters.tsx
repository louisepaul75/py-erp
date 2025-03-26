"use client"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Select } from "@/components/ui/select"
import { Filter } from "lucide-react"

interface ProductFiltersProps {
  searchTerm: string
  setSearchTerm: (value: string) => void
  statusFilter: string
  setStatusFilter: (value: string) => void
  categoryFilter: string
  setCategoryFilter: (value: string) => void
  isNewFilter: boolean
  setIsNewFilter: (value: boolean) => void
  isActiveFilter: boolean
  setIsActiveFilter: (value: boolean) => void
}

export function ProductFilters({
  searchTerm,
  setSearchTerm,
  statusFilter,
  setStatusFilter,
  categoryFilter,
  setCategoryFilter,
  isNewFilter,
  setIsNewFilter,
  isActiveFilter,
  setIsActiveFilter,
}: ProductFiltersProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center gap-1">
          <Filter className="h-4 w-4" />
          <span>Filter</span>
        </Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Filter</SheetTitle>
        </SheetHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label>Status</Label>
            <Select
              value={statusFilter}
              onValueChange={setStatusFilter}
              options={[
                { value: "", label: "Alle" },
                { value: "active", label: "Aktiv" },
                { value: "inactive", label: "Inaktiv" },
              ]}
            />
          </div>
          <div className="space-y-2">
            <Label>Kategorie</Label>
            <Select
              value={categoryFilter}
              onValueChange={setCategoryFilter}
              options={[
                { value: "", label: "Alle" },
                { value: "electronics", label: "Elektronik" },
                { value: "clothing", label: "Kleidung" },
                { value: "books", label: "Bücher" },
              ]}
            />
          </div>
          <div className="space-y-2">
            <Label>Neuheit</Label>
            <Select
              value={isNewFilter ? "new" : "all"}
              onValueChange={(value) => setIsNewFilter(value === "new")}
              options={[
                { value: "all", label: "Alle" },
                { value: "new", label: "Nur neue" },
              ]}
            />
          </div>
          <div className="space-y-2">
            <Label>Aktivität</Label>
            <Select
              value={isActiveFilter ? "active" : "all"}
              onValueChange={(value) => setIsActiveFilter(value === "active")}
              options={[
                { value: "all", label: "Alle" },
                { value: "active", label: "Nur aktive" },
              ]}
            />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
} 