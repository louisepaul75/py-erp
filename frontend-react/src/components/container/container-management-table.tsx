"use client"

import type React from "react"

import { useState } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Edit, Trash2, ChevronDown, ChevronRight } from "lucide-react"
import type { ContainerItem } from "@/types/warehouse-types"

interface ContainerManagementTableProps { 
  filteredContainers: ContainerItem[]
  selectedContainers: string[]
  handleSelectContainer: (id: string, checked: boolean) => void
  handleSelectAll: (checked: boolean) => void
  handleEditClick: (container: ContainerItem, e: React.MouseEvent) => void
  handleDeleteClick: (container: ContainerItem, e: React.MouseEvent) => void
  lastPrintDate: Date | null
  onLocationClick?: (shelf: number, compartment: number, floor: number) => void
}

export default function ContainerManagementTable({
  filteredContainers,
  selectedContainers,
  handleSelectContainer,
  handleSelectAll,
  handleEditClick,
  handleDeleteClick,
  lastPrintDate,
  onLocationClick,
}: ContainerManagementTableProps) {
  // State to track which containers are expanded
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({})

  // Toggle expanded state for a container
  const toggleRowExpanded = (containerId: string) => {
    setExpandedRows((prev) => ({
      ...prev,
      [containerId]: !prev[containerId],
    }))
  }

  // Function to navigate to warehouse location
  const navigateToLocation = (locationString: string, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent row click

    // Parse the location string (e.g., "11-3-1")
    const [shelf, compartment, floor] = locationString.split("-").map(Number)

    // Call the callback if provided
    if (onLocationClick) {
      onLocationClick(shelf, compartment, floor)
    } else {
      // Fallback to window.location if callback not provided
      window.location.href = `/?shelf=${shelf}&compartment=${compartment}&floor=${floor}`
    }
  }

  return (
    <div className="border rounded-md overflow-hidden">
      <div className="overflow-auto" style={{ maxHeight: "600px" }}>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              <th className="w-10 px-4 py-3 text-left">
                <Checkbox
                  checked={selectedContainers.length === filteredContainers.length && filteredContainers.length > 0}
                  onCheckedChange={(checked) => handleSelectAll(!!checked)}
                  aria-label="Alle auswählen"
                />
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Schütten</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Type</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Zweck</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Slots</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Einh.</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">angelegt</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">AZ</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">gedruckt</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">GZ</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Aktionen</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredContainers.length > 0 ? (
              filteredContainers.map((container) => {
                // Get the purpose based on container type
                const purpose =
                  container.type === "OD" || container.type === "KC"
                    ? "Transport"
                    : container.type === "PT" || container.type === "JK"
                      ? "Picken"
                      : "Lager"

                // Generate a random location string
                const locationString = `${Math.floor(Math.random() * 20) + 1}-${Math.floor(Math.random() * 10) + 1}-${Math.floor(Math.random() * 5) + 1}`

                // Check if this row is expanded
                const isExpanded = expandedRows[container.id] || false

                return (
                  <>
                    <tr
                      key={container.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => toggleRowExpanded(container.id)}
                    >
                      <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                        <Checkbox
                          checked={selectedContainers.includes(container.id)}
                          onCheckedChange={(checked) => handleSelectContainer(container.id, !!checked)}
                          aria-label={`Schütte ${container.containerCode} auswählen`}
                        />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center">
                          {isExpanded ? (
                            <ChevronDown className="h-4 w-4 mr-2 flex-shrink-0" />
                          ) : (
                            <ChevronRight className="h-4 w-4 mr-2 flex-shrink-0" />
                          )}
                          {container.containerCode}
                        </div>
                      </td>
                      <td className="px-4 py-3">{container.type}</td>
                      <td className="px-4 py-3">{purpose}</td>
                      <td className="px-4 py-3">{container.slots?.length || 0}</td>
                      <td className="px-4 py-3">
                        {container.units?.filter((u) => u.articleNumber || u.description || u.stock).length || 0}/
                        {container.units?.length || 0}
                      </td>
                      <td className="px-4 py-3">{new Date().toLocaleDateString("de-DE")}</td>
                      <td className="px-4 py-3">
                        {new Date().toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })}
                      </td>
                      <td className="px-4 py-3">{lastPrintDate ? lastPrintDate.toLocaleDateString("de-DE") : "-"}</td>
                      <td className="px-4 py-3">
                        {lastPrintDate
                          ? lastPrintDate.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })
                          : "-"}
                      </td>
                      <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => handleEditClick(container, e)}
                            title="Details"
                            className="flex items-center gap-1"
                          >
                            <Edit className="h-4 w-4 text-blue-500" />
                            <span className="text-xs text-blue-500">Details</span>
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => handleDeleteClick(container, e)}
                            title="Löschen"
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </td>
                    </tr>

                    {/* Expanded row with container details */}
                    {isExpanded && (
                      <tr key={`expanded-${container.id}`}>
                        <td colSpan={11} className="p-0 border-t border-gray-100">
                          <div className="p-4 bg-gray-50">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                              {/* Container Visualization - smaller (1/4 width) */}
                              <div className="space-y-2">
                                <h3 className="text-sm font-medium">Schütten-Visualisierung</h3>
                                <div className="border-2 border-gray-300 rounded-lg p-2 bg-white">
                                  <div className="grid grid-cols-2 gap-2">
                                    {container.slots?.map((slot) => {
                                      const unit = container.units?.find(
                                        (u) => Array.isArray(u.slots) && u.slots.includes(slot.id),
                                      )

                                      return (
                                        <div
                                          key={slot.id}
                                          className={`flex flex-col items-center justify-center ${slot.code.color} text-white font-bold rounded-md h-14 p-1`}
                                        >
                                          <div className="text-base">{slot.code.code}</div>
                                          <div className="text-xs">Einheit {unit?.unitNumber || "-"}</div>
                                        </div>
                                      )
                                    })}
                                  </div>
                                </div>
                              </div>

                              {/* Units and Articles Table - larger (3/4 width) */}
                              <div className="space-y-2 md:col-span-3">
                                <h3 className="text-sm font-medium">Einheiten und Artikel</h3>
                                <div className="border rounded-md overflow-hidden bg-white">
                                  <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-100">
                                      <tr>
                                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Einh.</th>
                                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Code</th>
                                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                          Artikel-Nr.
                                        </th>
                                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                          alte Art.-Nr.
                                        </th>
                                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                          Bezeichnung
                                        </th>
                                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                          Bestand
                                        </th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200">
                                      {container.units?.map((unit) => {
                                        // Get all slots for this unit
                                        const unitSlots = container.slots?.filter(
                                          (slot) => Array.isArray(unit.slots) && unit.slots.includes(slot.id),
                                        )

                                        return (
                                          <tr key={unit.id} className="hover:bg-gray-50">
                                            <td className="px-3 py-2 text-sm">{unit.unitNumber}</td>
                                            <td className="px-3 py-2">
                                              <div className="flex flex-wrap gap-1">
                                                {unitSlots?.map((slot) => (
                                                  <span
                                                    key={slot.id}
                                                    className={`inline-flex items-center justify-center w-10 h-6 ${slot.code.color} text-white font-medium rounded`}
                                                  >
                                                    {slot.code.code}
                                                  </span>
                                                ))}
                                              </div>
                                            </td>
                                            <td className="px-3 py-2 text-sm font-medium">
                                              {unit.articleNumber || "-"}
                                            </td>
                                            <td className="px-3 py-2 text-sm">{unit.oldArticleNumber || "-"}</td>
                                            <td className="px-3 py-2 text-sm">{unit.description || "-"}</td>
                                            <td className="px-3 py-2 text-sm">{unit.stock || 0}</td>
                                          </tr>
                                        )
                                      })}
                                      {(!container.units || container.units.length === 0) && (
                                        <tr>
                                          <td colSpan={6} className="px-3 py-2 text-center text-sm text-gray-500">
                                            Keine Einheiten vorhanden
                                          </td>
                                        </tr>
                                      )}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                )
              })
            ) : (
              <tr>
                <td colSpan={11} className="px-4 py-6 text-center text-gray-500">
                  Keine Schütten gefunden
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

