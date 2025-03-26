"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Trash2, Edit, Plus, Loader2 } from "lucide-react"
import { useContainerTypeStore, type ContainerType } from "@/lib/stores/container-type-store"
import ContainerTypeDialog from "./container-type-dialog"
import { SortableTable } from "../ui/sortable-table"
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
    {
      id: "name",
      header: "Schüttentype",
      cell: (row: ContainerType) => row.name,
      sortable: true,
    },
    {
      id: "manufacturer",
      header: "Hersteller",
      cell: (row: ContainerType) => row.manufacturer,
      sortable: true,
    },
    {
      id: "articleNumber",
      header: "Art.-Nr.",
      cell: (row: ContainerType) => row.articleNumber,
      sortable: true,
    },
    {
      id: "length",
      header: "Länge mm",
      cell: (row: ContainerType) => row.length,
      sortable: true,
    },
    {
      id: "width",
      header: "Breite mm",
      cell: (row: ContainerType) => row.width,
      sortable: true,
    },
    {
      id: "height",
      header: "Höhe mm",
      cell: (row: ContainerType) => row.height,
      sortable: true,
    },
    {
      id: "boxWeight",
      header: "Box gewicht",
      cell: (row: ContainerType) => `${row.boxWeight} g`,
      sortable: true,
    },
    {
      id: "dividerWeight",
      header: "Trenner gewicht",
      cell: (row: ContainerType) => `${row.dividerWeight} g`,
      sortable: true,
    },
    {
      id: "standardSlots",
      header: "St. Slots",
      cell: (row: ContainerType) => row.standardSlots,
      sortable: true,
    },
    {
      id: "actions",
      header: "Aktionen",
      cell: (row: ContainerType) => (
        <div className="flex space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              handleEdit(row)
            }}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              handleDelete(row)
            }}
          >
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      ),
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
          <SortableTable data={containerTypes} columns={columns} onRowClick={handleEdit} />
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

