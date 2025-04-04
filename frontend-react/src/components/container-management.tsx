"use client"

import type React from "react"

import { useState, useEffect, useMemo, useCallback } from "react"
import { Printer, Plus, History, ChevronLeft, ChevronRight, Warehouse, Package2, Settings, RotateCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { fetchContainers, generateSlotItems, generateInitialUnits } from "@/lib/inventory/service"
import ActivityLogDialog from "./activity-log-dialog"
import ContainerDetailDialog from "./container-detail-dialog"
import CreateContainerDialog from "./create-container-dialog"
import EditContainerDialog from "./edit-container-dialog"
import DeleteContainerDialog from "./delete-container-dialog"
import PrintContainerDialog from "./print-container-dialog"
import ContainerManagementFilters from "./container/container-management-filters"
import ContainerManagementTable from "./container/container-management-table"
import type { ContainerItem } from "@/types/warehouse-types"
import Link from "next/link"
import SettingsDialog from "./settings/settings-dialog"
import ErrorMessage from "@/components/ui/error-message"
import { Card, CardHeader, CardContent } from "@/components/ui/card"

const PRINTERS = [
  { value: "none", label: "Drucker auswählen" },
  { value: "Hauptlager-Drucker", label: "Hauptlager-Drucker" },
  { value: "Büro-Drucker", label: "Büro-Drucker" },
  { value: "Externer Drucker", label: "Externer Drucker" },
]

// Function to renumber units sequentially
const renumberUnits = (container: ContainerItem) => {
  if (!container.units) {
    return container
  }

  const updatedUnits = container.units.map((unit, index) => ({
    ...unit,
    unitNumber: index + 1,
  }))

  return {
    ...container,
    units: updatedUnits,
  }
}

export default function ContainerManagement() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [containers, setContainers] = useState<ContainerItem[]>([])
  const [selectedContainers, setSelectedContainers] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [typeFilter, setTypeFilter] = useState("all")
  const [purposeFilter, setPurposeFilter] = useState("all")
  const [selectedPrinter, setSelectedPrinter] = useState("")
  const [multiplier, setMultiplier] = useState("1")
  const [isActivityLogOpen, setIsActivityLogOpen] = useState(false)
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isPrintDialogOpen, setIsPrintDialogOpen] = useState(false)
  const [selectedContainer, setSelectedContainer] = useState<ContainerItem | null>(null)
  const [lastPrintDate, setLastPrintDate] = useState<Date | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(20)
  const [totalContainerCount, setTotalContainerCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadContainers = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const { 
        containers: apiContainers, 
        totalCount 
      } = await fetchContainers(
        currentPage, 
        itemsPerPage, 
        searchTerm,
        typeFilter !== 'all' ? typeFilter : undefined,
        purposeFilter !== 'all' ? purposeFilter : undefined
      );
      
      setContainers(apiContainers.map(renumberUnits));
      
      setTotalContainerCount(totalCount);
      
    } catch (err) {
      console.error("Error loading containers:", err);
      setError(`Fehler beim Laden der Schütten: ${err instanceof Error ? err.message : 'Unbekannter Fehler'}`);
      setContainers([]);
      setTotalContainerCount(0);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, itemsPerPage, searchTerm, typeFilter, purposeFilter]);

  useEffect(() => {
    loadContainers();
  }, [loadContainers]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, typeFilter, purposeFilter, itemsPerPage]);

  const totalPages = useMemo(() => {
    return Math.ceil(totalContainerCount / itemsPerPage)
  }, [totalContainerCount, itemsPerPage]);

  const paginatedContainers = containers;

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedContainers(paginatedContainers.map((container) => container.id))
    } else {
      setSelectedContainers([])
    }
  }

  const handleSelectContainer = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedContainers([...selectedContainers, id])
    } else {
      setSelectedContainers(selectedContainers.filter((containerId) => containerId !== id))
    }
  }

  const handleCreateContainer = (newContainer: ContainerItem) => {
    loadContainers();
    setIsCreateDialogOpen(false)
  }

  const handleUpdateContainer = (updatedContainer: ContainerItem) => {
    loadContainers();
    
    if (isDetailDialogOpen) {
      setIsDetailDialogOpen(false)
    }
    if (isEditDialogOpen) {
      setIsEditDialogOpen(false)
    }
    setSelectedContainer(null)
  }

  const handleDeleteContainer = () => {
    if (selectedContainer) {
      console.log("Deleting container:", selectedContainer.id);
      setIsDeleteDialogOpen(false)
      setSelectedContainer(null)
      loadContainers();
    }
  }

  const handlePrint = () => {
    if (!selectedPrinter || selectedPrinter === "none") return

    setLastPrintDate(new Date())

    setIsPrintDialogOpen(true)
  }

  const handleEditClick = (container: ContainerItem, e: React.MouseEvent) => {
    e.stopPropagation()
    setSelectedContainer(container)
    setIsDetailDialogOpen(true)
  }

  const handleDeleteClick = (container: ContainerItem, e: React.MouseEvent) => {
    e.stopPropagation()
    setSelectedContainer(container)
    setIsDeleteDialogOpen(true)
  }

  const handleLocationClick = (shelf: number, compartment: number, floor: number) => {
    window.location.href = `/?shelf=${shelf}&compartment=${compartment}&floor=${floor}`
  }

  const generateContainerCode = () => {
    const prefix = "SC"
    const randomNum = Math.floor(100000 + Math.random() * 900000)
    return `${prefix}${randomNum}`
  }

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  const handleItemsPerPageChange = (value: string) => {
    const newItemsPerPage = value === "all" ? totalContainerCount : Number.parseInt(value)
    setItemsPerPage(Math.max(1, newItemsPerPage));
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary">Schüttenverwaltung</h1>
        <div className="flex items-center">
          <Link
            href="/warehouse"
            className={`flex items-center mx-2 px-4 py-2 rounded-t-lg border-b-2 border-transparent text-muted-foreground hover:border-muted`}
          >
            <Warehouse className="h-4 w-4 mr-2" />
            Lagerort-Verwaltung
          </Link>
          <Link
            href="/container-management"
            className={`flex items-center px-4 py-2 rounded-t-lg border-b-2 border-primary text-primary`}
          >
            <Package2 className="h-4 w-4 mr-2" />
            Schütten-Verwaltung
          </Link>
          <Button
              variant="outline"
              size="sm"
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center gap-1 mx-2 text-muted-foreground"
            >
            <Settings className="h-4 w-4" />
            Einstellungen
          </Button>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsActivityLogOpen(true)} className="flex items-center gap-2 text-muted-foreground">
            <History className="h-4 w-4" />
            Aktivitätslog
          </Button>
          <Button variant="outline" onClick={() => setIsCreateDialogOpen(true)} className="flex items-center gap-1 text-muted-foreground">
            <Plus className="h-4 w-4" />
            Schütte erstellen
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <ContainerManagementFilters
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            typeFilter={typeFilter}
            setTypeFilter={setTypeFilter}
            purposeFilter={purposeFilter}
            setPurposeFilter={setPurposeFilter}
          />
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center items-center py-10">
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mb-4"></div>
                <p className="text-gray-500">Schütten werden geladen...</p>
              </div>
            </div>
          ) : error ? (
            <ErrorMessage 
              message={error}
              onRetry={loadContainers}
              retryDisabled={isLoading}
            />
          ) : (
            <ContainerManagementTable
              filteredContainers={paginatedContainers}
              selectedContainers={selectedContainers}
              handleSelectContainer={handleSelectContainer}
              handleSelectAll={handleSelectAll}
              handleEditClick={handleEditClick}
              handleDeleteClick={handleDeleteClick}
              lastPrintDate={lastPrintDate}
              onLocationClick={handleLocationClick}
            />
          )}

          {!isLoading && totalContainerCount > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between mt-4 gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">Einträge pro Seite:</span>
                <Select
                  value={itemsPerPage === totalContainerCount ? "all" : itemsPerPage.toString()}
                  onValueChange={handleItemsPerPageChange}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Einträge pro Seite" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="20">20</SelectItem>
                    <SelectItem value="50">50</SelectItem>
                    <SelectItem value="100">100</SelectItem>
                    <SelectItem value="all">Alle ({totalContainerCount})</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {totalPages > 1 && (
                <div className="flex items-center justify-center space-x-1 sm:space-x-2 overflow-x-auto max-w-full py-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(1)}
                    disabled={currentPage === 1 || isLoading}
                    title="Erste Seite"
                    className="hidden sm:inline-flex"
                  >
                    <span className="sr-only">Erste Seite</span>
                    <ChevronLeft className="h-3 w-3 mr-1" />
                    <ChevronLeft className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1 || isLoading}
                    title="Vorherige Seite"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>

                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum: number;
                    const maxVisibleButtons = 5;
                    const halfVisible = Math.floor(maxVisibleButtons / 2);

                    if (totalPages <= maxVisibleButtons) {
                      pageNum = i + 1;
                    } else if (currentPage <= halfVisible + 1) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - halfVisible) {
                      pageNum = totalPages - maxVisibleButtons + 1 + i;
                    } else {
                      pageNum = currentPage - halfVisible + i;
                    }
                    
                    if (pageNum > totalPages || pageNum < 1) return null;

                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? "default" : "outline"}
                        size="sm"
                        onClick={() => handlePageChange(pageNum)}
                        disabled={isLoading}
                        className="min-w-8 h-8 px-2 sm:px-3"
                      >
                        {pageNum}
                      </Button>
                    )
                  })}

                  {totalPages > 5 && currentPage < totalPages - 2 && (
                    <>
                      <span className="mx-1 hidden sm:inline">...</span>
                       <Button 
                         variant="outline" 
                         size="sm" 
                         onClick={() => handlePageChange(totalPages)} 
                         disabled={isLoading}
                         className="hidden sm:inline-flex min-w-8 h-8 px-2 sm:px-3"
                       >
                        {totalPages}
                      </Button>
                    </>
                  )}

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages || isLoading}
                    title="Nächste Seite"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(totalPages)}
                    disabled={currentPage === totalPages || isLoading}
                    title="Letzte Seite"
                    className="hidden sm:inline-flex"
                  >
                    <span className="sr-only">Letzte Seite</span>
                    <ChevronRight className="h-3 w-3 mr-1" />
                    <ChevronRight className="h-3 w-3" />
                  </Button>
                </div>
              )}

              <div className="text-sm text-gray-500 whitespace-nowrap">
                Zeige {totalContainerCount > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} bis{" "}
                {Math.min(currentPage * itemsPerPage, totalContainerCount)} von {totalContainerCount} Einträgen
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex items-center gap-4 border-t pt-4">
        <div className="flex-1">
          <Select
            value={selectedPrinter}
            onValueChange={setSelectedPrinter}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Drucker auswählen" />
            </SelectTrigger>
            <SelectContent>
              {PRINTERS.map((printer) => (
                <SelectItem key={printer.value} value={printer.value} disabled={printer.value === "none"}>
                  {printer.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="multiplier" className="whitespace-nowrap">
            Multiplikator:
          </Label>
          <Input
            id="multiplier"
            type="number"
            min="1"
            max="10"
            value={multiplier}
            onChange={(e) => setMultiplier(e.target.value)}
            className="w-16"
          />
        </div>
        <Button
          variant="default"
          onClick={handlePrint}
          disabled={selectedContainers.length === 0 || !selectedPrinter || selectedPrinter === "none"}
          className="flex items-center gap-2"
        >
          <Printer className="h-4 w-4" />
          Schütten Etiketten
        </Button>
      </div>

      {isActivityLogOpen && (
        <ActivityLogDialog
          isOpen={isActivityLogOpen}
          onClose={() => setIsActivityLogOpen(false)}
          locationType="container"
        />
      )}

      {isDetailDialogOpen && selectedContainer && (
        <ContainerDetailDialog
          isOpen={isDetailDialogOpen}
          onClose={() => {
            setIsDetailDialogOpen(false)
            setSelectedContainer(null)
          }}
          container={selectedContainer}
          onLocationClick={handleLocationClick}
          onSave={handleUpdateContainer}
        />
      )}

      {isCreateDialogOpen && (
        <CreateContainerDialog
          isOpen={isCreateDialogOpen}
          onClose={() => setIsCreateDialogOpen(false)}
          onSave={handleCreateContainer}
          generateContainerCode={generateContainerCode}
        />
      )}

      {isEditDialogOpen && selectedContainer && (
        <EditContainerDialog
          isOpen={isEditDialogOpen}
          onClose={() => {
            setIsEditDialogOpen(false)
            setSelectedContainer(null)
          }}
          container={selectedContainer}
          onSave={handleUpdateContainer}
        />
      )}

      {isDeleteDialogOpen && selectedContainer && (
        <DeleteContainerDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => {
            setIsDeleteDialogOpen(false)
            setSelectedContainer(null)
          }}
          container={selectedContainer}
          onConfirm={handleDeleteContainer}
        />
      )}

      {isPrintDialogOpen && (
        <PrintContainerDialog
          isOpen={isPrintDialogOpen}
          onClose={() => setIsPrintDialogOpen(false)}
          selectedContainers={containers.filter((container) => selectedContainers.includes(container.id))}
          selectedPrinter={selectedPrinter}
          multiplier={Number(multiplier)}
        />
      )}

      <SettingsDialog isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  )
}

