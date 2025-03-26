"use client"

import React from "react"

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
  const [expandedContainers, setExpandedContainers] = useState<string[]>([])

  // Toggle expanded state for a container
  const handleToggleExpand = (containerId: string) => {
    setExpandedContainers(prev => 
      prev.includes(containerId) 
        ? prev.filter(id => id !== containerId) 
        : [...prev, containerId]
    )
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
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredContainers.length > 0 ? (
              filteredContainers.map((container) => {
                // Format today's date for display
                const today = new Date();
                const formattedDate = `${today.getDate().toString().padStart(2, '0')}.${(today.getMonth() + 1).toString().padStart(2, '0')}.${today.getFullYear()}`;
                const formattedTime = `${today.getHours().toString().padStart(2, '0')}:${today.getMinutes().toString().padStart(2, '0')}`;
                
                // Get the number of slots and units
                const slotCount = container.slots?.length || 0;
                const unitCount = container.units?.length || 0;
                
                // Set the purpose class for color coding
                let purposeClass = "";
                switch (container.purpose) {
                  case "Lager":
                    purposeClass = "bg-blue-100 text-blue-800";
                    break;
                  case "Picken":
                    purposeClass = "bg-green-100 text-green-800";
                    break;
                  case "Transport":
                    purposeClass = "bg-yellow-100 text-yellow-800";
                    break;
                  case "Werkstatt":
                    purposeClass = "bg-purple-100 text-purple-800";
                    break;
                  default:
                    purposeClass = "bg-gray-100 text-gray-800";
                }

                return (
                  <React.Fragment key={container.id}>
                    <tr
                      className={`hover:bg-gray-50 ${expandedContainers.includes(container.id) ? "bg-gray-50" : ""}`}
                    >
                      <td className="w-10 px-4 py-3">
                        <Checkbox
                          checked={selectedContainers.includes(container.id)}
                          onCheckedChange={(checked) => handleSelectContainer(container.id, !!checked)}
                          aria-label={`Schütte ${container.containerCode} auswählen`}
                        />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="mr-2 p-0 h-6 w-6"
                            onClick={() => handleToggleExpand(container.id)}
                          >
                            {expandedContainers.includes(container.id) ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronRight className="h-4 w-4" />
                            )}
                          </Button>
                          <div>
                            <div className="font-medium">{container.containerCode}</div>
                            <div className="text-xs text-gray-500">{container.displayCode || ''}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100">
                          {container.type || 'AR'}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${purposeClass}`}>
                          {container.purpose || 'Lager'}
                        </div>
                      </td>
                      <td className="px-4 py-3">{slotCount}</td>
                      <td className="px-4 py-3">{unitCount}/{slotCount}</td>
                      <td className="px-4 py-3">{formattedDate}</td>
                      <td className="px-4 py-3">{formattedTime}</td>
                      <td className="px-4 py-3">
                        {lastPrintDate && container.id === selectedContainers[0]
                          ? lastPrintDate.toLocaleDateString("de-DE")
                          : "-"}
                      </td>
                      <td className="px-4 py-3">
                        {lastPrintDate && container.id === selectedContainers[0]
                          ? lastPrintDate.toLocaleTimeString("de-DE", {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : "-"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => handleEditClick(container, e)}
                            title="Bearbeiten"
                          >
                            <Edit className="h-4 w-4 text-blue-500" />
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
                    {expandedContainers.includes(container.id) && (
                      <tr>
                        <td colSpan={11} className="p-0">
                          <div className="pl-10 pr-4 pb-4">
                            <div className="bg-gray-50 rounded-md p-3">
                              <h4 className="font-medium mb-2">Details</h4>
                              <div className="grid grid-cols-3 gap-4 mb-4">
                                <div>
                                  <p className="text-sm font-medium">Lagerdaten</p>
                                  <div className="text-sm mt-1">
                                    <p>
                                      <span className="font-medium">Lagerort:</span>{" "}
                                      {container.location ? (
                                        <button
                                          onClick={() =>
                                            onLocationClick(
                                              container.shelf,
                                              container.compartment,
                                              container.floor
                                            )
                                          }
                                          className="text-blue-600 hover:underline"
                                        >
                                          {container.location}
                                        </button>
                                      ) : (
                                        "Kein Lagerort zugewiesen"
                                      )}
                                    </p>
                                    <p>
                                      <span className="font-medium">Status:</span> {container.status || 'Verfügbar'}
                                    </p>
                                    <p>
                                      <span className="font-medium">Zweck:</span> {container.purpose || 'Lager'}
                                    </p>
                                  </div>
                                </div>
                                <div>
                                  <p className="text-sm font-medium">Beschreibung</p>
                                  <p className="text-sm mt-1">
                                    {container.description || "Keine Beschreibung verfügbar"}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-sm font-medium">Inhalt</p>
                                  <p className="text-sm mt-1">
                                    {container.units && container.units.some(
                                      (unit) => unit.articleNumber || unit.description
                                    )
                                      ? `${container.units.filter(
                                          (unit) => unit.articleNumber || unit.description
                                        ).length} Artikel`
                                      : "Keine Artikel"}
                                  </p>
                                </div>
                              </div>

                              <h4 className="font-medium mb-2">Einheiten</h4>
                              <div className="bg-white rounded border">
                                <table className="min-w-full divide-y divide-gray-200">
                                  <thead className="bg-gray-100">
                                    <tr>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                        Einheit Nr.
                                      </th>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                        Artikelnummer
                                      </th>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                        Alte Artikelnummer
                                      </th>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">
                                        Beschreibung
                                      </th>
                                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Bestand</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {container.units?.map((unit) => (
                                      <tr key={unit.id} className="border-t border-gray-200">
                                        <td className="px-3 py-2 text-sm">{unit.unitNumber}</td>
                                        <td className="px-3 py-2 text-sm">
                                          {unit.articleNumber || "Nicht zugewiesen"}
                                        </td>
                                        <td className="px-3 py-2 text-sm">
                                          {unit.oldArticleNumber || "Nicht zugewiesen"}
                                        </td>
                                        <td className="px-3 py-2 text-sm">
                                          {unit.description || "Keine Beschreibung"}
                                        </td>
                                        <td className="px-3 py-2 text-sm">{unit.stock || 0}</td>
                                      </tr>
                                    ))}
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
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
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
  );
}

