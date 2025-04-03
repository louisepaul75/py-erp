"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Trash2 } from "lucide-react"
import type { WarehouseLocation } from "@/types/warehouse-types"
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table"

interface WarehouseLocationTableProps {
  filteredLocations: WarehouseLocation[]
  selectedLocations: string[]
  handleSelectLocation: (id: string, checked: boolean) => void
  handleRowClick: (location: WarehouseLocation) => void
  handleDeleteClick: (location: WarehouseLocation) => void
  highlightedLocationId?: string | null
}

export default function WarehouseLocationTable({
  filteredLocations,
  selectedLocations,
  handleSelectLocation,
  handleRowClick,
  handleDeleteClick,
  highlightedLocationId,
}: WarehouseLocationTableProps) {
  // Definiere die Spalten für die sortierbare Tabelle
  const columns = [
    {
      id: "checkbox",
      header: (
        <Checkbox
          checked={selectedLocations.length === filteredLocations.length && filteredLocations.length > 0}
          onCheckedChange={(checked) => {
            if (checked) {
              handleSelectLocation("all", true)
            } else {
              handleSelectLocation("none", false)
            }
          }}
          aria-label="Alle auswählen"
          className="translate-y-[2px]"
        />
      ),
      cell: (row: WarehouseLocation) => (
        <Checkbox
          checked={selectedLocations.includes(row.id)}
          onCheckedChange={(checked) => handleSelectLocation(row.id, !!checked)}
          aria-label={`Lagerort ${row.laNumber} auswählen`}
          onClick={(e) => e.stopPropagation()}
          className="translate-y-[2px]"
        />
      ),
      className: "w-[40px]",
    },
    {
      id: "laNumber",
      header: "LA-Nummer",
      cell: (row: WarehouseLocation) => row.laNumber,
      sortable: true,
    },
    {
      id: "location",
      header: "Ort/Gebäude",
      cell: (row: WarehouseLocation) => row.location,
      sortable: true,
    },
    {
      id: "status",
      header: "Status",
      cell: (row: WarehouseLocation) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            row.status === "free" ? "bg-status-success/10 text-status-success-foreground" : "bg-status-warning/10 text-status-warning-foreground"
          }`}
        >
          {row.status === "free" ? "Frei" : "Belegt"}
        </span>
      ),
      sortable: true,
    },
    {
      id: "forSale",
      header: "Abverkauf",
      cell: (row: WarehouseLocation) => (row.forSale ? "✅" : "❌"),
      sortable: true,
    },
    {
      id: "specialStorage",
      header: "Sonderlager",
      cell: (row: WarehouseLocation) => (row.specialStorage ? "✅" : "❌"),
      sortable: true,
    },
    {
      id: "shelf",
      header: "Regal",
      cell: (row: WarehouseLocation) => row.shelf,
      sortable: true,
    },
    {
      id: "compartment",
      header: "Fach",
      cell: (row: WarehouseLocation) => row.compartment,
      sortable: true,
    },
    {
      id: "floor",
      header: "Boden",
      cell: (row: WarehouseLocation) => row.floor,
      sortable: true,
    },
    {
      id: "containerCount",
      header: "Anzahl Schütten",
      cell: (row: WarehouseLocation) => row.containerCount,
      sortable: true,
    },
    {
      id: "actions",
      header: "Aktionen",
      cell: (row: WarehouseLocation) => (
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={(e) => {
            e.stopPropagation()
            handleDeleteClick(row)
          }}
          disabled={row.containerCount > 0}
          title={
            row.containerCount > 0 ? "Lagerort enthält Schütten und kann nicht gelöscht werden" : "Lagerort löschen"
          }
        >
          <Trash2 className="h-4 w-4 text-destructive" />
          <span className="sr-only">Löschen</span>
        </Button>
      ),
      className: "text-right",
    },
  ]

  return (
    <div className="border rounded-md">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead
                key={column.id}
                className={column.className}
              >
                {typeof column.header === 'function' ? column.header() : column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredLocations.length > 0 ? (
            filteredLocations.map((location) => (
              <TableRow
                key={location.id}
                data-state={selectedLocations.includes(location.id) ? "selected" : undefined}
                className={`cursor-pointer ${
                  highlightedLocationId === location.id ? "bg-accent" : ""
                }`}
                onClick={() => handleRowClick(location)}
              >
                {columns.map((column) => (
                  <TableCell
                    key={`${location.id}-${column.id}`}
                    className={column.className}
                  >
                    {column.cell(location)}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                Keine Lagerorte gefunden
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}

