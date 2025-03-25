"use client"

import { useState, useEffect, useCallback } from "react"
import { ListChecks, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import NewWarehouseLocationModal from "@/components/new-warehouse-location-modal"
import MultipleWarehouseLocationsModal from "@/components/multiple-warehouse-locations-modal"
import PrintDialog from "@/components/print-dialog"
import DeleteConfirmDialog from "@/components/delete-confirm-dialog"
import LocationDetailDialog from "@/components/location-detail-dialog"
import WarehouseLocationFilters from "@/components/warehouse-location/warehouse-location-filters"
import WarehouseLocationMobile from "@/components/warehouse-location/warehouse-location-mobile"
import WarehouseLocationTable from "@/components/warehouse-location/warehouse-location-table"
import { generateMockData } from "@/lib/warehouse-service"
import type { WarehouseLocation, ContainerItem } from "@/types/warehouse-types"

const PRINTERS = [
  { value: "none", label: "Drucker auswählen" },
  { value: "Hauptlager-Drucker", label: "Hauptlager-Drucker" },
  { value: "Büro-Drucker", label: "Büro-Drucker" },
  { value: "Externer Drucker", label: "Externer Drucker" },
]

export type { ContainerItem, WarehouseLocation }
export default function WarehouseLocationList() {
  const [locations, setLocations] = useState<WarehouseLocation[]>([])
  const [filteredLocations, setFilteredLocations] = useState<WarehouseLocation[]>([])
  const [selectedLocations, setSelectedLocations] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [locationFilter, setLocationFilter] = useState("all")
  const [shelfFilter, setShelfFilter] = useState("")
  const [compartmentFilter, setCompartmentFilter] = useState("")
  const [floorFilter, setFloorFilter] = useState("")
  const [saleFilter, setSaleFilter] = useState("all")
  const [specialFilter, setSpecialFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [isNewLocationModalOpen, setIsNewLocationModalOpen] = useState(false)
  const [isMultipleNewLocationModalOpen, setIsMultipleNewLocationModalOpen] = useState(false)
  const [isPrintDialogOpen, setIsPrintDialogOpen] = useState(false)
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false)
  const [isLocationDetailOpen, setIsLocationDetailOpen] = useState(false)
  const [selectedLocation, setSelectedLocation] = useState<WarehouseLocation | null>(null)
  const [selectedPrinter, setSelectedPrinter] = useState("")
  const [highlightedLocationId, setHighlightedLocationId] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(500)

  useEffect(() => {
    // Load mock data
    const mockData = generateMockData(3000)
    setLocations(mockData)
    setFilteredLocations(mockData)
  }, [])

  // Highlight location from URL params
  useEffect(() => {
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search)
    const shelf = urlParams.get("shelf")
    const compartment = urlParams.get("compartment")
    const floor = urlParams.get("floor")

    if (shelf && compartment && floor) {
      // Find the location that matches the URL parameters
      const foundLocation = locations.find(
        (loc) => loc.shelf === Number(shelf) && loc.compartment === Number(compartment) && loc.floor === Number(floor),
      )

      if (foundLocation) {
        setHighlightedLocationId(foundLocation.id)
      }
    }
  }, [locations])

  useEffect(() => {
    let filtered = [...locations]

    // Search
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(
        (location) => location.laNumber.toLowerCase().includes(term) || location.location.toLowerCase().includes(term),
      )
    }

    // Filters
    if (locationFilter !== "all") {
      filtered = filtered.filter((location) => location.location === locationFilter)
    }
    if (statusFilter !== "all") {
      filtered = filtered.filter((location) => location.status === statusFilter)
    }
    if (shelfFilter) {
      filtered = filtered.filter((location) => location.shelf === Number(shelfFilter))
    }
    if (compartmentFilter) {
      filtered = filtered.filter((location) => location.compartment === Number(compartmentFilter))
    }
    if (floorFilter) {
      filtered = filtered.filter((location) => location.floor === Number(floorFilter))
    }
    if (saleFilter !== "all") {
      const forSale = saleFilter === "yes"
      filtered = filtered.filter((location) => location.forSale === forSale)
    }
    if (specialFilter !== "all") {
      const specialStorage = specialFilter === "yes"
      filtered = filtered.filter((location) => location.specialStorage === specialStorage)
    }

    setFilteredLocations(filtered)
  }, [
    locations,
    searchTerm,
    locationFilter,
    shelfFilter,
    compartmentFilter,
    floorFilter,
    saleFilter,
    specialFilter,
    statusFilter,
  ])

  // Berechne die Gesamtanzahl der Seiten
  const totalPages = Math.ceil(filteredLocations.length / itemsPerPage)

  // Berechne die aktuell anzuzeigenden Elemente
  const paginatedLocations = filteredLocations.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedLocations(filteredLocations.map((location) => location.id))
    } else {
      setSelectedLocations([])
    }
  }

  const handleSelectLocation = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedLocations([...selectedLocations, id])
    } else {
      setSelectedLocations(selectedLocations.filter((locationId) => locationId !== id))
    }
  }

  const handleCreateNewLocation = (newLocation: WarehouseLocation) => {
    setLocations([...locations, newLocation])
    setIsNewLocationModalOpen(false)
  }

  const handleCreateMultipleNewLocations = (newLocations: WarehouseLocation[]) => {
    setLocations([...locations, ...newLocations])
    setIsMultipleNewLocationModalOpen(false)
  }

  const handlePrint = () => {
    if (!selectedPrinter) return
    setIsPrintDialogOpen(true)
  }

  const handleRowClick = (location: WarehouseLocation) => {
    setSelectedLocation(location)
    setIsLocationDetailOpen(true)
  }

  const handleDeleteClick = (location: WarehouseLocation) => {
    setSelectedLocation(location)
    setIsDeleteConfirmOpen(true)
  }

  const handleConfirmDelete = () => {
    if (selectedLocation) {
      setLocations(locations.filter((location) => location.id !== selectedLocation.id))
      setIsDeleteConfirmOpen(false)
      setSelectedLocation(null)
    }
  }

  const clearURLParams = useCallback(() => {
    window.history.pushState({}, "", "/")
    setHighlightedLocationId(null)
  }, [])

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    // Scrolle zum Anfang der Tabelle
    window.scrollTo(0, 0)
  }

  const handleItemsPerPageChange = (value: string) => {
    const newItemsPerPage = value === "all" ? filteredLocations.length : Number.parseInt(value)
    setItemsPerPage(newItemsPerPage)
    setCurrentPage(1) // Zurück zur ersten Seite bei Änderung der Einträge pro Seite
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Lagerort-Verwaltung</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsMultipleNewLocationModalOpen(true)}>
            Mehrere Lagerorte
          </Button>
          <Button variant="outline" onClick={() => setIsNewLocationModalOpen(true)}>
            Neuer Lagerort
          </Button>
          {highlightedLocationId && (
            <Button variant="ghost" size="sm" onClick={clearURLParams}>
              <ListChecks className="h-4 w-4 mr-2" />
              Alle Lagerorte
            </Button>
          )}
        </div>
      </div>

      <WarehouseLocationFilters
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        locationFilter={locationFilter}
        setLocationFilter={setLocationFilter}
        shelfFilter={shelfFilter}
        setShelfFilter={setShelfFilter}
        compartmentFilter={compartmentFilter}
        setCompartmentFilter={setCompartmentFilter}
        floorFilter={floorFilter}
        setFloorFilter={setFloorFilter}
        saleFilter={saleFilter}
        setSaleFilter={setSaleFilter}
        specialFilter={specialFilter}
        setSpecialFilter={setSpecialFilter}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
      />

      {/* Table and Mobile List */}
      <div className="hidden md:block"> 
        <WarehouseLocationTable
          filteredLocations={paginatedLocations}
          selectedLocations={selectedLocations}
          handleSelectLocation={handleSelectLocation}
          handleRowClick={handleRowClick}
          handleDeleteClick={handleDeleteClick}
          highlightedLocationId={highlightedLocationId}
        />
      </div>
      <WarehouseLocationMobile
        filteredLocations={paginatedLocations}
        selectedLocations={selectedLocations}
        handleSelectLocation={handleSelectLocation}
        handleRowClick={handleRowClick}
        handleDeleteClick={handleDeleteClick}
      />

      {filteredLocations.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between mt-4 gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Einträge pro Seite:</span>
            <Select
              value={itemsPerPage === filteredLocations.length ? "all" : itemsPerPage.toString()}
              onValueChange={handleItemsPerPageChange}
              options={[
                { value: "100", label: "100" },
                { value: "500", label: "500" },
                { value: "1000", label: "1000" },
                { value: "all", label: "Alle" },
              ]}
            />
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
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
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}

          <div className="text-sm text-gray-500">
            Zeige {(currentPage - 1) * itemsPerPage + 1} bis{" "}
            {Math.min(currentPage * itemsPerPage, filteredLocations.length)} von {filteredLocations.length} Einträgen
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
        <Button variant="default" onClick={handlePrint} disabled={selectedLocations.length === 0 || !selectedPrinter}>
          Lagerorte drucken
        </Button>
      </div>

      {/* Modals */}
      <NewWarehouseLocationModal
        isOpen={isNewLocationModalOpen}
        onClose={() => setIsNewLocationModalOpen(false)}
        onSave={handleCreateNewLocation}
        existingLocations={locations}
      />

      <MultipleWarehouseLocationsModal
        isOpen={isMultipleNewLocationModalOpen}
        onClose={() => setIsMultipleNewLocationModalOpen(false)}
        onSave={handleCreateMultipleNewLocations}
        existingLocations={locations}
      />

      <PrintDialog
        isOpen={isPrintDialogOpen}
        onClose={() => setIsPrintDialogOpen(false)}
        selectedLocations={locations.filter((location) => selectedLocations.includes(location.id))}
        selectedPrinter={selectedPrinter}
      />

      {/* Only render DeleteConfirmDialog when selectedLocation is not null */}
      {isDeleteConfirmOpen && selectedLocation && (
        <DeleteConfirmDialog
          isOpen={isDeleteConfirmOpen}
          onClose={() => setIsDeleteConfirmOpen(false)}
          onConfirm={handleConfirmDelete}
          location={selectedLocation}
        />
      )}

      {/* Only render LocationDetailDialog when selectedLocation is not null */}
      {isLocationDetailOpen && selectedLocation && (
        <LocationDetailDialog
          isOpen={isLocationDetailOpen}
          onClose={() => setIsLocationDetailOpen(false)}
          location={selectedLocation}
        />
      )}
    </div>
  )
}

