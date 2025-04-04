"use client"

import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

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
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="LA-Nummer oder Schüttennummer suchen..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-2 ">
          <Select
            value={locationFilter}
            onValueChange={setLocationFilter}
          >
            <SelectTrigger>
              <SelectValue placeholder="Ort/Gebäude" />
            </SelectTrigger>
            <SelectContent>
              {LOCATIONS.map((loc) => (
                <SelectItem key={loc.value} value={loc.value}>
                  {loc.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
             value={statusFilter}
             onValueChange={setStatusFilter}
          >
            <SelectTrigger>
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
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
          >
            <SelectTrigger>
              <SelectValue placeholder="Abverkauf" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Abverkauf: Alle</SelectItem>
              <SelectItem value="yes">Abverkauf: Ja</SelectItem>
              <SelectItem value="no">Abverkauf: Nein</SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={specialFilter}
            onValueChange={setSpecialFilter}
          >
            <SelectTrigger>
              <SelectValue placeholder="Sonderlager" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Sonderlager: Alle</SelectItem>
              <SelectItem value="yes">Sonderlager: Ja</SelectItem>
              <SelectItem value="no">Sonderlager: Nein</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </>
  )
}

