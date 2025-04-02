"use client"

import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select1"

interface ContainerManagementFiltersProps {
  searchTerm: string
  setSearchTerm: (value: string) => void
  typeFilter: string
  setTypeFilter: (value: string) => void
  purposeFilter: string
  setPurposeFilter: (value: string) => void
}

const CONTAINER_TYPES = [
  { value: "all", label: "Alle Typen" },
  { value: "OD", label: "OD" },
  { value: "KC", label: "KC" },
  { value: "PT", label: "PT" },
  { value: "JK", label: "JK" },
  { value: "AR", label: "AR" },
  { value: "HF", label: "HF" },
]

const PURPOSES = [
  { value: "all", label: "Alle Zwecke" },
  { value: "Lager", label: "Lager" },
  { value: "Transport", label: "Transport" },
  { value: "Picken", label: "Picken" },
  { value: "Werkstatt", label: "Werkstatt" },
]

export default function ContainerManagementFilters({
  searchTerm,
  setSearchTerm,
  typeFilter,
  setTypeFilter,
  purposeFilter,
  setPurposeFilter,
}: ContainerManagementFiltersProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="space-y-4">
        <div className="flex-1">
          <Label htmlFor="combinedSearch" className="text-sm">
            Suche (Schütten-Nr., Artikel-Nr., Bezeichnung, Lagerort):
          </Label>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
            <Input
              id="combinedSearch"
              type="text"
              placeholder="SC123456, 123456, 9315XXX-BE, Bezeichnung oder LA1234"
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-2">
          <div>
            <Label htmlFor="typeFilter" className="text-sm">
              Typ:
            </Label>
            <Select
              value={typeFilter}
              onValueChange={setTypeFilter}
              placeholder="Typ auswählen"
              options={CONTAINER_TYPES}
            />
          </div>
          <div>
            <Label htmlFor="purposeFilter" className="text-sm">
              Zweck:
            </Label>
            <Select
              value={purposeFilter}
              onValueChange={setPurposeFilter}
              placeholder="Zweck auswählen"
              options={PURPOSES}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

