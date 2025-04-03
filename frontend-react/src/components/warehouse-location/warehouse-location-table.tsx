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
  StatusBadge,
} from "@/components/ui/data/Table"

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
  const columns = [
    {
      id: "checkbox",
      header: () => (
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
        />
      ),
      cell: (row: WarehouseLocation) => (
        <Checkbox
          checked={selectedLocations.includes(row.id)}
          onCheckedChange={(checked) => handleSelectLocation(row.id, !!checked)}
          aria-label={`Lagerort ${row.laNumber} auswählen`}
          onClick={(e) => e.stopPropagation()}
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
      cell: (row: WarehouseLocation) => {
        const status = row.status === "free" ? "active" : "pending";
        return (
          <StatusBadge status={status}>
            {row.status === "free" ? "Frei" : "Belegt"}
          </StatusBadge>
        );
      },
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
        <div className="flex justify-end">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
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
        </div>
      ),
      className: "text-right",
    },
  ]

  return (
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
              className={`cursor-pointer ${highlightedLocationId === location.id ? "bg-accent" : ""}`}
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
  )
}

