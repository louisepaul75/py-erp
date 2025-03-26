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
  isNewFilter: string
  setIsNewFilter: (value: string) => void
  isActiveFilter: string
  setIsActiveFilter: (value: string) => void
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
              value={isNewFilter}
              onValueChange={setIsNewFilter}
              options={[
                { value: "all", label: "Alle" },
                { value: "new", label: "Nur neue" },
                { value: "not_new", label: "Keine neuen" }
              ]}
            />
          </div>
          <div className="space-y-2">
            <Label>Aktivität</Label>
            <Select
              value={isActiveFilter}
              onValueChange={setIsActiveFilter}
              options={[
                { value: "all", label: "Alle" },
                { value: "active", label: "Nur aktive" },
                { value: "inactive", label: "Nur inaktive" }
              ]}
            />
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
} 