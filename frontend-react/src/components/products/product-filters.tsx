"use client"

import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"

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

export default function ProductFilters({
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
    <>
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <Input
          className="pl-10 w-full"
          placeholder="Produkt suchen (Artikelnummer, Name)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <Select
          value={statusFilter}
          onValueChange={setStatusFilter}
          placeholder="Status"
          options={[
            { value: "all", label: "Alle Status" },
            { value: "active", label: "Aktiv" },
            { value: "inactive", label: "Inaktiv" },
            { value: "discontinued", label: "Eingestellt" },
          ]}
        />

        <Select
          value={categoryFilter}
          onValueChange={setCategoryFilter}
          placeholder="Kategorie"
          options={[
            { value: "all", label: "Alle Kategorien" },
            { value: "zinnfigur", label: "Zinnfiguren" },
            { value: "eisenbahn", label: "Eisenbahnen" },
            { value: "accessories", label: "Zubehör" },
          ]}
        />

        <Select
          value={isNewFilter}
          onValueChange={setIsNewFilter}
          placeholder="Neuheit"
          options={[
            { value: "all", label: "Alle Produkte" },
            { value: "new", label: "Neuheiten" },
            { value: "old", label: "Keine Neuheiten" },
          ]}
        />

        <Select
          value={isActiveFilter}
          onValueChange={setIsActiveFilter}
          placeholder="Status"
          options={[
            { value: "all", label: "Alle Produkte" },
            { value: "active", label: "Aktive Produkte" },
            { value: "inactive", label: "Inaktive Produkte" },
          ]}
        />
      </div>
    </>
  )
} 