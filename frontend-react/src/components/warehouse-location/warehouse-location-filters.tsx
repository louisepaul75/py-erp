"use client"

import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"

interface WarehouseLocationFiltersProps {
  searchTerm: string
  setSearchTerm: (value: string) => void
  locationFilter: string
  setLocationFilter: (value: string) => void
  shelfFilter: string
  setShelfFilter: (value: string) => void
  compartmentFilter: string
  setCompartmentFilter: (value: string) => void
  floorFilter: string
  setFloorFilter: (value: string) => void
  saleFilter: string
  setSaleFilter: (value: string) => void
  specialFilter: string
  setSpecialFilter: (value: string) => void
  statusFilter: string
  setStatusFilter: (value: string) => void
}

const LOCATIONS = [
  { value: "all", label: "Alle Orte" },
  { value: "Hauptlager 1", label: "Hauptlager 1" },
  { value: "Hauptlager 2", label: "Hauptlager 2" },
  { value: "Externes Lager", label: "Externes Lager" },
  { value: "Nebenlager", label: "Nebenlager" },
  { value: "Stammlager-Diessen", label: "Stammlager-Diessen" },
]

const STATUS_OPTIONS = [
  { value: "all", label: "Alle Status" },
  { value: "free", label: "Frei" },
  { value: "in-use", label: "Belegt" },
]

export default function WarehouseLocationFilters({
  searchTerm,
  setSearchTerm,
  locationFilter,
  setLocationFilter,
  shelfFilter,
  setShelfFilter,
  compartmentFilter,
  setCompartmentFilter,
  floorFilter,
  setFloorFilter,
  saleFilter,
  setSaleFilter,
  specialFilter,
  setSpecialFilter,
  statusFilter,
  setStatusFilter,
}: WarehouseLocationFiltersProps) {
  return (
    <>
      {/* Search and Filter Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            type="text"
            placeholder="LA-Nummer oder Schüttennummer suchen..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <Select
            value={locationFilter}
            onValueChange={setLocationFilter}
            placeholder="Ort/Gebäude"
            options={LOCATIONS}
          />

          <Select value={statusFilter} onValueChange={setStatusFilter} placeholder="Status" options={STATUS_OPTIONS} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="grid grid-cols-3 gap-2">
          <Input
            type="number"
            placeholder="Regal"
            value={shelfFilter}
            onChange={(e) => setShelfFilter(e.target.value)}
          />
          <Input
            type="number"
            placeholder="Fach"
            value={compartmentFilter}
            onChange={(e) => setCompartmentFilter(e.target.value)}
          />
          <Input
            type="number"
            placeholder="Boden"
            value={floorFilter}
            onChange={(e) => setFloorFilter(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <Select
            value={saleFilter}
            onValueChange={setSaleFilter}
            placeholder="Abverkauf"
            options={[
              { value: "all", label: "Abverkauf: Alle" },
              { value: "yes", label: "Abverkauf: Ja" },
              { value: "no", label: "Abverkauf: Nein" },
            ]}
          />

          <Select
            value={specialFilter}
            onValueChange={setSpecialFilter}
            placeholder="Sonderlager"
            options={[
              { value: "all", label: "Sonderlager: Alle" },
              { value: "yes", label: "Sonderlager: Ja" },
              { value: "no", label: "Sonderlager: Nein" },
            ]}
          />
        </div>
      </div>
    </>
  )
}

