"use client"

import type React from "react"

import { useState, useEffect, useMemo, useCallback } from "react"
import { Printer, Plus, History, ChevronLeft, ChevronRight, Warehouse, Package2, Settings, RotateCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
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
  const [filteredContainers, setFilteredContainers] = useState<ContainerItem[]>([])
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
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const [isRetrying, setIsRetrying] = useState(false)

  const loadContainers = useCallback(async (retry = false) => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (retry) {
        setIsRetrying(true)
      }
      
      // Fetch containers with reasonable page size
      const { containers: apiContainers, totalCount, totalPages } = await fetchContainers(currentPage, itemsPerPage);
      
      // Transform containers efficiently
      const enhancedContainers = apiContainers.map((container) => {
        // Only generate slots and units if not already present
        const slots = container.slots || generateSlotItems(container.type);
        const units = container.units || generateInitialUnits(slots);
        
        return {
          ...container,
          slots,
          units,
        };
      });
      
      setContainers(prevContainers => {
        // Update only the current page data
        const newContainers = [...prevContainers];
        const startIndex = (currentPage - 1) * itemsPerPage;
        
        enhancedContainers.forEach((container, index) => {
          newContainers[startIndex + index] = container;
        });
        
        return newContainers;
      });
      
      setFilteredContainers(enhancedContainers);
      setRetryCount(0);
      setIsRetrying(false);
    } catch (error) {
      console.error("Error loading containers:", error);
      setError(`Fehler beim Laden der Schütten: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
      setIsRetrying(false);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, itemsPerPage]);

  // Optimize page data loading
  const loadPageData = useCallback(async () => {
    if (containers.length === 0) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Only fetch if not filtering locally
      if (searchTerm === "" && typeFilter === "all" && purposeFilter === "all") {
        const { containers: apiContainers } = await fetchContainers(currentPage, itemsPerPage);
        
        setContainers(prevContainers => {
          const newContainers = [...prevContainers];
          const startIndex = (currentPage - 1) * itemsPerPage;
          
          apiContainers.forEach((container, index) => {
            newContainers[startIndex + index] = container;
          });
          
          return newContainers;
        });
        
        setFilteredContainers(apiContainers);
      }
    } catch (error) {
      console.error("Error loading page data:", error);
      setError(`Fehler beim Laden der Seite: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, itemsPerPage, containers.length, searchTerm, typeFilter, purposeFilter]);

  useEffect(() => {
    // Call the async function to load containers
    loadContainers();
  }, [loadContainers]);

  // Add effect to reload containers when page changes
  useEffect(() => {
    loadPageData();
  }, [loadPageData]);

  // Memoize filtered containers to improve performance
  const filteredContainersMemo = useMemo(() => {
    let result = [...containers]

    // Combined search for container code, article numbers, description, and location
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter((container) => {
        // Check container code and basic properties
        if (
          container.containerCode.toLowerCase().includes(term) ||
          container.description.toLowerCase().includes(term)
        ) {
          return true
        }

        // Check units for article numbers and descriptions
        return container.units?.some(
          (unit) =>
            (unit.articleNumber && unit.articleNumber.toLowerCase().includes(term)) ||
            (unit.oldArticleNumber && unit.oldArticleNumber.toLowerCase().includes(term)) ||
            (unit.description && unit.description.toLowerCase().includes(term)),
        )
      })
    }

    // Apply type filter
    if (typeFilter !== "all") {
      result = result.filter((container) => container.type === typeFilter)
    }

    // Apply purpose filter
    if (purposeFilter !== "all") {
      // Filter by purpose based on container type
      result = result.filter((container) => {
        if (purposeFilter === "Transport") return container.type === "OD" || container.type === "KC"
        if (purposeFilter === "Picken") return container.type === "PT" || container.type === "JK"
        if (purposeFilter === "Lager") return container.type === "AR" || container.type === "HF"
        return true
      })
    }

    return result
  }, [containers, searchTerm, typeFilter, purposeFilter])

  // Update filtered containers when memoized value changes
  useEffect(() => {
    setFilteredContainers(filteredContainersMemo)
  }, [filteredContainersMemo])

  // Berechne die Gesamtanzahl der Seiten
  const totalPages = Math.ceil(filteredContainers.length / itemsPerPage)

  // Berechne die aktuell anzuzeigenden Elemente
  const paginatedContainers = filteredContainers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedContainers(filteredContainers.map((container) => container.id))
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

  // Function to handle creating a new container
  const handleCreateContainer = (newContainer: ContainerItem) => {
    // Generate slots and units for the new container
    const slots = generateSlotItems(newContainer.type, newContainer.customSlotCount)
    const units = generateInitialUnits(slots)

    // Create the enhanced container with proper unit numbering
    const enhancedContainer = renumberUnits({
      ...newContainer,
      slots,
      units,
    })

    setContainers([...containers, enhancedContainer])
    setIsCreateDialogOpen(false)
  }

  // Update the handleUpdateContainer function to ensure proper unit numbering
  const handleUpdateContainer = (updatedContainer: ContainerItem) => {
    // Ensure units are properly numbered
    const renumberedContainer = renumberUnits(updatedContainer)

    setContainers(
      containers.map((container) => (container.id === renumberedContainer.id ? renumberedContainer : container)),
    )

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
      setContainers(containers.filter((container) => container.id !== selectedContainer.id))
      setIsDeleteDialogOpen(false)
      setSelectedContainer(null)
    }
  }

  const handlePrint = () => {
    if (!selectedPrinter || selectedPrinter === "none") return

    // Set current date for "printed" timestamp
    setLastPrintDate(new Date())

    // Open print dialog
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

  // Handle location click
  const handleLocationClick = (shelf: number, compartment: number, floor: number) => {
    // Navigate to the warehouse location page
    window.location.href = `/?shelf=${shelf}&compartment=${compartment}&floor=${floor}`
  }

  // Generate a unique container code
  const generateContainerCode = () => {
    const prefix = "SC"
    const randomNum = Math.floor(100000 + Math.random() * 900000) // 6-digit number
    return `${prefix}${randomNum}`
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    // Scrolle zum Anfang der Tabelle
    window.scrollTo(0, 0)
  }

  const handleItemsPerPageChange = (value: string) => {
    const newItemsPerPage = value === "all" ? filteredContainers.length : Number.parseInt(value)
    setItemsPerPage(newItemsPerPage)
    setCurrentPage(1) // Zurück zur ersten Seite bei Änderung der Einträge pro Seite
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Schüttenverwaltung</h1>
        <div className="flex items-center">
          <Link
            href="/warehouse"
            className={`flex items-center mx-2 px-4 py-2 rounded-t-lg border-b-2 hover:border-gray-300 hover:text-gray-600`}
          >
            <Warehouse className="h-4 w-4 mr-2" />
            Lagerort-Verwaltung
          </Link>
          <Link
            href="/container-management"
            className={`flex items-center px-4 py-2 rounded-t-lg border-b-2  border-blue-500 text-blue-600`}
          >
            <Package2 className="h-4 w-4 mr-2" />
            Schütten-Verwaltung
          </Link>
          <Button
              variant="outline"
              size="sm"
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center gap-1 mx-2"
            >
            <Settings className="h-4 w-4" />
            Einstellungen
          </Button>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsActivityLogOpen(true)} className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Aktivitätslog
          </Button>
          <Button variant="outline" onClick={() => setIsCreateDialogOpen(true)} className="flex items-center gap-1">
            <Plus className="h-4 w-4" />
            Schütte erstellen
          </Button>
        </div>
      </div>

      {/* Search and Filter Section */}
      <ContainerManagementFilters
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        typeFilter={typeFilter}
        setTypeFilter={setTypeFilter}
        purposeFilter={purposeFilter}
        setPurposeFilter={setPurposeFilter}
      />

      {/* Loading, Error, and Container Table */}
      {isLoading ? (
        <div className="flex justify-center items-center py-10">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-500">
              {isRetrying ? "Verbindung wird erneut hergestellt..." : "Schütten werden geladen..."}
            </p>
          </div>
        </div>
      ) : error ? (
        <ErrorMessage 
          message={error}
          onRetry={loadContainers}
          retryDisabled={isRetrying}
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

      {filteredContainers.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between mt-4 gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Einträge pro Seite:</span>
            <Select
              value={itemsPerPage === filteredContainers.length ? "all" : itemsPerPage.toString()}
              onValueChange={handleItemsPerPageChange}
              options={[
                { value: "20", label: "20" },
                { value: "50", label: "50" },
                { value: "100", label: "100" },
                { value: "all", label: "Alle" },
              ]}
            />
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-2 overflow-x-auto max-w-full py-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(1)}
                disabled={currentPage === 1}
                title="Erste Seite"
              >
                <span className="sr-only">Erste Seite</span>
                <ChevronLeft className="h-3 w-3 mr-1" />
                <ChevronLeft className="h-3 w-3" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                title="Vorherige Seite"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>

              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                // Zeige maximal 5 Seiten an
                let pageNum: number

                if (totalPages <= 5) {
                  // Wenn es 5 oder weniger Seiten gibt, zeige alle an
                  pageNum = i + 1
                } else if (currentPage <= 3) {
                  // Wenn wir auf den ersten 3 Seiten sind
                  pageNum = i + 1
                } else if (currentPage >= totalPages - 2) {
                  // Wenn wir auf den letzten 3 Seiten sind
                  pageNum = totalPages - 4 + i
                } else {
                  // Sonst zeige 2 Seiten vor und 2 Seiten nach der aktuellen Seite
                  pageNum = currentPage - 2 + i
                }

                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => handlePageChange(pageNum)}
                    className="min-w-8"
                  >
                    {pageNum}
                  </Button>
                )
              })}

              {totalPages > 5 && currentPage < totalPages - 2 && (
                <>
                  <span className="mx-1">...</span>
                  <Button variant="outline" size="sm" onClick={() => handlePageChange(totalPages)}>
                    {totalPages}
                  </Button>
                </>
              )}

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                title="Nächste Seite"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(totalPages)}
                disabled={currentPage === totalPages}
                title="Letzte Seite"
              >
                <span className="sr-only">Letzte Seite</span>
                <ChevronRight className="h-3 w-3 mr-1" />
                <ChevronRight className="h-3 w-3" />
              </Button>
            </div>
          )}

          <div className="text-sm text-gray-500 whitespace-nowrap">
            Zeige {filteredContainers.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} bis{" "}
            {Math.min(currentPage * itemsPerPage, filteredContainers.length)} von {filteredContainers.length} Einträgen
          </div>
        </div>
      )}

      {/* Print Section */}
      <div className="flex items-center gap-4 border-t pt-4">
        <div className="flex-1">
          <Select
            value={selectedPrinter}
            onValueChange={setSelectedPrinter}
            placeholder="Drucker auswählen"
            options={PRINTERS}
          />
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

      {/* Dialogs */}
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

