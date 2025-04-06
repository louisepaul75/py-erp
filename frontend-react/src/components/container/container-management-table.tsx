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
  StatusBadge,
} from "@/components/ui/data/Table"

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
  const [expandedContainers, setExpandedContainers] = useState<string[]>([])

  const handleToggleExpand = (containerId: string) => {
    setExpandedContainers(prev => 
      prev.includes(containerId) 
        ? prev.filter(id => id !== containerId) 
        : [...prev, containerId]
    )
  }

  const navigateToLocation = (locationString: string, e: React.MouseEvent) => {
    e.stopPropagation() 
    const [shelf, compartment, floor] = locationString.split("-").map(Number)
    if (onLocationClick) {
      onLocationClick(shelf, compartment, floor)
    } else {
      window.location.href = `/?shelf=${shelf}&compartment=${compartment}&floor=${floor}`
    }
  }

  const columns = [
    {
      id: "checkbox",
      header: () => (
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
          onClick={(e) => e.stopPropagation()}
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
            aria-label={expandedContainers.includes(container.id) ? "Details ausblenden" : "Details anzeigen"}
          >
            {expandedContainers.includes(container.id) ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
          <div className="font-medium text-lg text-primary">{container.containerCode || "N/A"}</div>
        </div>
      )
    },
    {
      id: "type",
      header: "Typ",
      cell: (container: ContainerItem) => (
        <span className="text-xs font-medium text-muted-foreground">
          {container.type || 'AR'}
        </span>
      )
    },
    {
      id: "purpose",
      header: "Zweck",
      cell: (container: ContainerItem) => {
        let status: 'info' | 'active' | 'pending' | 'inactive' | 'default' = 'default';
        switch (container.purpose) {
          case "Lager": status = "info"; break;
          case "Picken": status = "active"; break;
          case "Transport": status = "pending"; break;
          case "Werkstatt": status = "inactive"; break;
          default: status = "default";
        }
        return (
          <StatusBadge status={status}>
            {container.purpose || 'Lager'}
          </StatusBadge>
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
        const createdDate = container.createdAt ? new Date(container.createdAt) : new Date();
        return createdDate.toLocaleDateString("de-DE");
      }
    },
    {
      id: "createdTime",
      header: "AZ",
      cell: (container: ContainerItem) => {
        const createdDate = container.createdAt ? new Date(container.createdAt) : new Date();
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
        <div className="flex items-center gap-1 justify-end">
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
    <Table>
      <TableHeader>
        <TableRow>
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
                className="cursor-pointer"
              >
                {columns.map((column) => (
                  <TableCell key={`${container.id}-${column.id}`} className={column.className}>
                    {column.cell(container)}
                  </TableCell>
                ))}
              </TableRow>
              {expandedContainers.includes(container.id) && (
                <TableRow className="bg-muted/50 hover:bg-muted/50">
                  <TableCell colSpan={columns.length} className="p-0">
                    <div className="p-4">
                      <h4 className="font-medium mb-2 text-sm">Details für {container.containerCode}</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-xs">
                        <div>
                          <p className="font-semibold text-muted-foreground">Lagerdaten</p>
                          <div className="mt-1 space-y-1">
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
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="h-8 px-3 text-xs">Einheit Nr.</TableHead>
                            <TableHead className="h-8 px-3 text-xs">Artikelnummer</TableHead>
                            <TableHead className="h-8 px-3 text-xs">Alte Artikelnummer</TableHead>
                            <TableHead className="h-8 px-3 text-xs">Beschreibung</TableHead>
                            <TableHead className="h-8 px-3 text-xs">Bestand</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {container.units?.length > 0 ? container.units.map((unit) => (
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
                          )) : (
                            <TableRow>
                              <TableCell colSpan={5} className="h-16 text-center text-xs text-muted-foreground">
                                Keine Einheiten vorhanden
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
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
  );
}

