"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Trash2 } from "lucide-react"
import type { WarehouseLocation } from "@/types/warehouse-types"

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
      header: "",
      cell: (row: WarehouseLocation) => (
        <Checkbox
          checked={selectedLocations.includes(row.id)}
          onCheckedChange={(checked) => handleSelectLocation(row.id, !!checked)}
          aria-label={`Lagerort ${row.laNumber} auswählen`}
          onClick={(e) => e.stopPropagation()}
        />
      ),
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
            row.status === "free" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
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
          onClick={(e) => {
            e.stopPropagation()
            handleDeleteClick(row)
          }}
          disabled={row.containerCount > 0}
          title={
            row.containerCount > 0 ? "Lagerort enthält Schütten und kann nicht gelöscht werden" : "Lagerort löschen"
          }
        >
          <Trash2 className="h-4 w-4 text-red-500" />
        </Button>
      ),
    },
  ]

  return (
    <div className="border rounded-md overflow-hidden" style={{ maxHeight: "600px" }}>
      <div className="overflow-y-auto" style={{ maxHeight: "600px" }}>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.id}
                  className="px-4 py-3 text-left text-sm font-medium text-gray-500 sticky top-0 bg-gray-100"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 ">
            {filteredLocations.length > 0 ? (
              filteredLocations.map((location) => (
                <tr
                  key={location.id}
                  className={`hover:bg-gray-50 cursor-pointer ${
                    highlightedLocationId === location.id ? "bg-blue-100" : ""
                  }`}
                  onClick={() => handleRowClick(location)}
                >
                  <td className="px-4 py-3">
                    <Checkbox
                      checked={selectedLocations.includes(location.id)}
                      onCheckedChange={(checked) => handleSelectLocation(location.id, !!checked)}
                      aria-label={`Lagerort ${location.laNumber} auswählen`}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </td>
                  <td className="px-4 py-3">{location.laNumber}</td>
                  <td className="px-4 py-3">{location.location}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        location.status === "free" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {location.status === "free" ? "Frei" : "Belegt"}
                    </span>
                  </td>
                  <td className="px-4 py-3">{location.forSale ? "✅" : "❌"}</td>
                  <td className="px-4 py-3">{location.specialStorage ? "✅" : "❌"}</td>
                  <td className="px-4 py-3">{location.shelf}</td>
                  <td className="px-4 py-3">{location.compartment}</td>
                  <td className="px-4 py-3">{location.floor}</td>
                  <td className="px-4 py-3">{location.containerCount}</td>
                  <td className="px-4 py-3">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteClick(location)
                      }}
                      disabled={location.containerCount > 0}
                      title={
                        location.containerCount > 0
                          ? "Lagerort enthält Schütten und kann nicht gelöscht werden"
                          : "Lagerort löschen"
                      }
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-4 py-6 text-center text-gray-500">
                  Keine Lagerorte gefunden
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

