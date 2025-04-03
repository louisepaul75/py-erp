"use client"

import React from "react"

import { useState } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Edit, Trash2, ChevronDown, ChevronRight } from "lucide-react"
import type { ContainerItem } from "@/types/warehouse-types"
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table"

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

  // Define columns for the main table
  const columns = [
    {
      id: "checkbox",
      header: (
        <Checkbox
          checked={selectedContainers.length === filteredContainers.length && filteredContainers.length > 0}
          onCheckedChange={(checked) => handleSelectAll(!!checked)}
          aria-label="Alle auswählen"
        />
      ),
      cell: (container: ContainerItem) => (
        <Checkbox
          checked={selectedContainers.includes(container.id)}
          onCheckedChange={(checked) => handleSelectContainer(container.id, !!checked)}
          aria-label={`Schütte ${container.containerCode} auswählen`}
          onClick={(e) => e.stopPropagation()} // Prevent row click when clicking checkbox
        />
      ),
      className: "w-[40px]"
    },
    {
      id: "container",
      header: "Schütten",
      cell: (container: ContainerItem) => (
        <div className="flex items-center">
          <Button
            variant="ghost"
            size="sm"
            className="mr-2 p-0 h-6 w-6"
            onClick={(e) => { e.stopPropagation(); handleToggleExpand(container.id); }}
          >
            {expandedContainers.includes(container.id) ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
          <div>
            <div className="font-medium">{container.containerCode}</div>
            <div className="text-xs text-muted-foreground">{container.displayCode || ''}</div>
          </div>
        </div>
      )
    },
    {
      id: "type",
      header: "Typ",
      cell: (container: ContainerItem) => (
        <div className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-muted text-muted-foreground">
          {container.type || 'AR'}
        </div>
      )
    },
    {
      id: "purpose",
      header: "Zweck",
      cell: (container: ContainerItem) => {
        let purposeClass = "";
        switch (container.purpose) {
          case "Lager": purposeClass = "text-primary"; break;
          case "Picken": purposeClass = "text-success"; break;
          case "Transport": purposeClass = "text-warning"; break;
          case "Werkstatt": purposeClass = "text-info"; break;
          default: purposeClass = "text-gray-800 dark:text-gray-200"; // Keep gray as is
        }
        return (
          <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${purposeClass}`}>
            {container.purpose || 'Lager'}
          </div>
        );
      }
    },
    {
      id: "slots",
      header: "Slots",
      cell: (container: ContainerItem) => container.slots?.length || 0
    },
    {
      id: "units",
      header: "Einh.",
      cell: (container: ContainerItem) => `${container.units?.length || 0}/${container.slots?.length || 0}`
    },
    {
      id: "createdDate",
      header: "angelegt",
      cell: (container: ContainerItem) => {
        const createdDate = container.createdAt ? new Date(container.createdAt) : new Date(); // Fallback for demo
        return createdDate.toLocaleDateString("de-DE");
      }
    },
    {
      id: "createdTime",
      header: "AZ",
      cell: (container: ContainerItem) => {
        const createdDate = container.createdAt ? new Date(container.createdAt) : new Date(); // Fallback for demo
        return createdDate.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
      }
    },
    {
      id: "printedDate",
      header: "gedruckt",
      cell: (container: ContainerItem) => lastPrintDate && selectedContainers.includes(container.id) ? lastPrintDate.toLocaleDateString("de-DE") : "-"
    },
    {
      id: "printedTime",
      header: "GZ",
      cell: (container: ContainerItem) => lastPrintDate && selectedContainers.includes(container.id) ? lastPrintDate.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }) : "-"
    },
    {
      id: "actions",
      header: "Aktionen",
      cell: (container: ContainerItem) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => handleEditClick(container, e)}
            title="Bearbeiten"
          >
            <Edit className="h-4 w-4 text-primary" />
            <span className="sr-only">Bearbeiten</span>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => handleDeleteClick(container, e)}
            title="Löschen"
          >
            <Trash2 className="h-4 w-4 text-destructive" />
            <span className="sr-only">Löschen</span>
          </Button>
        </div>
      ),
      className: "text-right"
    }
  ];

  return (
    <div className="border rounded-md">
      <Table>
        <TableHeader>
          <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800/50">
            {columns.map((column) => (
              <TableHead key={column.id} className={column.className}>
                {typeof column.header === 'function' ? column.header() : column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredContainers.length > 0 ? (
            filteredContainers.map((container) => (
              <React.Fragment key={container.id}>
                <TableRow
                  data-state={selectedContainers.includes(container.id) ? "selected" : undefined}
                  className={`hover:bg-slate-50 dark:hover:bg-slate-800/70 cursor-pointer ${expandedContainers.includes(container.id) ? "bg-slate-50 dark:bg-slate-800/70" : ""}`}
                >
                  {columns.map((column) => (
                    <TableCell key={`${container.id}-${column.id}`} className={column.className}>
                      {column.cell(container)}
                    </TableCell>
                  ))}
                </TableRow>
                {expandedContainers.includes(container.id) && (
                  <TableRow className="bg-slate-50 dark:bg-slate-800/70">
                    <TableCell colSpan={columns.length} className="p-0">
                      <div className="p-4">
                        <h4 className="font-medium mb-2 text-sm">Details für {container.containerCode}</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-xs">
                          <div>
                            <p className="font-semibold text-muted-foreground">Lagerdaten</p>
                            <div className="mt-1">
                              <p>
                                <span className="font-medium">Lagerort:</span>{" "}
                                {container.location ? (
                                  <button
                                    onClick={(e) => navigateToLocation(container.location!, e)}
                                    className="text-primary hover:underline"
                                  >
                                    {container.location}
                                  </button>
                                ) : (
                                  "Kein Lagerort"
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
                            <p className="font-semibold text-muted-foreground">Beschreibung</p>
                            <p className="mt-1">
                              {container.description || "-"}
                            </p>
                          </div>
                          <div>
                            <p className="font-semibold text-muted-foreground">Inhalt</p>
                            <p className="mt-1">
                              {container.units && container.units.some(
                                (unit) => unit.articleNumber || unit.description
                              )
                                ? `${container.units.filter(
                                    (unit) => unit.articleNumber || unit.description
                                  ).length} Artikel`
                                : "-"}
                            </p>
                          </div>
                        </div>

                        <h4 className="font-medium mb-2 text-sm">Einheiten</h4>
                        <div className="border rounded-md overflow-hidden">
                          <Table size="sm">
                            <TableHeader className="bg-slate-100 dark:bg-slate-700">
                              <TableRow>
                                <TableHead className="h-8 px-3 text-xs">Einheit Nr.</TableHead>
                                <TableHead className="h-8 px-3 text-xs">Artikelnummer</TableHead>
                                <TableHead className="h-8 px-3 text-xs">Alte Artikelnummer</TableHead>
                                <TableHead className="h-8 px-3 text-xs">Beschreibung</TableHead>
                                <TableHead className="h-8 px-3 text-xs">Bestand</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {container.units?.map((unit) => (
                                <TableRow key={unit.id}>
                                  <TableCell className="px-3 py-1.5 text-xs">{unit.unitNumber}</TableCell>
                                  <TableCell className="px-3 py-1.5 text-xs">
                                    {unit.articleNumber || "-"}
                                  </TableCell>
                                  <TableCell className="px-3 py-1.5 text-xs">
                                    {unit.oldArticleNumber || "-"}
                                  </TableCell>
                                  <TableCell className="px-3 py-1.5 text-xs">
                                    {unit.description || "-"}
                                  </TableCell>
                                  <TableCell className="px-3 py-1.5 text-xs">{unit.stock || 0}</TableCell>
                                </TableRow>
                              ))}
                              {(!container.units || container.units.length === 0) && (
                                <TableRow>
                                  <TableCell colSpan={5} className="h-16 text-center text-xs text-muted-foreground">
                                    Keine Einheiten vorhanden
                                  </TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </React.Fragment>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                Keine Schütten gefunden.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}

