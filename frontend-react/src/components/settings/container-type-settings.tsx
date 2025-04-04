"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Trash2, Edit, Plus, Loader2 } from "lucide-react"
import { useContainerTypeStore, type ContainerType } from "@/lib/stores/container-type-store"
import ContainerTypeDialog from "./container-type-dialog"
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function ContainerTypeSettings() {
  const { containerTypes, isLoading, error, fetchContainerTypes, deleteContainerType } = useContainerTypeStore()
  const [selectedContainerType, setSelectedContainerType] = useState<ContainerType | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    fetchContainerTypes()
  }, [fetchContainerTypes])

  const handleEdit = (containerType: ContainerType) => {
    setSelectedContainerType(containerType)
    setIsCreating(false)
    setIsDialogOpen(true)
  }

  const handleCreate = () => {
    setSelectedContainerType(null)
    setIsCreating(true)
    setIsDialogOpen(true)
  }

  const handleDelete = (containerType: ContainerType) => {
    if (confirm(`Möchten Sie den Schüttentyp "${containerType.name}" wirklich löschen?`)) {
      deleteContainerType(containerType.id)
      // Wichtig: Nach dem Löschen nicht in die Einstellungen springen
      setSelectedContainerType(null)
      setIsDialogOpen(false)
    }
  }

  const handleCloseDialog = () => {
    setIsDialogOpen(false)
    setSelectedContainerType(null)
    setIsCreating(false)
  }

  const columns = [
    { id: "name", header: "Schüttentype", cell: (row: ContainerType) => row.name },
    { id: "manufacturer", header: "Hersteller", cell: (row: ContainerType) => row.manufacturer },
    { id: "articleNumber", header: "Art.-Nr.", cell: (row: ContainerType) => row.articleNumber },
    { id: "length", header: "Länge mm", cell: (row: ContainerType) => row.length, className: "text-right" },
    { id: "width", header: "Breite mm", cell: (row: ContainerType) => row.width, className: "text-right" },
    { id: "height", header: "Höhe mm", cell: (row: ContainerType) => row.height, className: "text-right" },
    { id: "boxWeight", header: "Box g", cell: (row: ContainerType) => row.boxWeight, className: "text-right" },
    { id: "dividerWeight", header: "Trenner g", cell: (row: ContainerType) => row.dividerWeight, className: "text-right" },
    { id: "standardSlots", header: "Slots", cell: (row: ContainerType) => row.standardSlots, className: "text-right" },
    {
      id: "actions",
      header: "Aktionen",
      cell: (row: ContainerType) => (
        <div className="flex items-center justify-end space-x-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation()
              handleEdit(row)
            }}
            title="Bearbeiten"
          >
            <Edit className="h-4 w-4 text-primary" />
            <span className="sr-only">Bearbeiten</span>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={(e) => {
              e.stopPropagation()
              handleDelete(row)
            }}
            title="Löschen"
          >
            <Trash2 className="h-4 w-4 text-destructive" />
            <span className="sr-only">Löschen</span>
          </Button>
        </div>
      ),
      className: "text-right"
    },
  ]

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Fehler beim Laden der Schüttentypen: {error}
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium">Schüttentypen</h2>
        <Button onClick={handleCreate} className="flex items-center gap-1">
          <Plus className="h-4 w-4" />
          Neue
        </Button>
      </div>

      <div className="border rounded-md overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center items-center p-8">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50 hover:bg-muted">
                {columns.map((column) => (
                  <TableHead key={column.id} className={`${column.className ?? ""} font-medium text-muted-foreground`}>
                    {column.header}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {containerTypes.length > 0 ? (
                containerTypes.map((row: ContainerType) => (
                  <TableRow
                    key={row.id}
                    className="hover:bg-muted/50 cursor-pointer"
                    onClick={() => handleEdit(row)}
                  >
                    {columns.map((column) => (
                      <TableCell key={`${row.id}-${column.id}`} className={column.className}>
                        {column.cell(row)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center text-muted-foreground">
                    Keine Schüttentypen konfiguriert
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </div>

      {isDialogOpen && (
        <ContainerTypeDialog
          isOpen={isDialogOpen}
          onClose={handleCloseDialog}
          containerType={selectedContainerType}
          isCreating={isCreating}
        />
      )}
    </div>
  )
}

