"use client"

import { useState, useEffect, useCallback } from "react"
import { ListChecks, ChevronLeft, ChevronRight, Warehouse, Package2, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
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
import { API_URL } from "@/lib/config"
import { authService } from "@/lib/auth/authService"
import Link from "next/link"
import SettingsDialog from "./settings/settings-dialog"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

const PRINTERS = [
  { value: "none", label: "Drucker auswählen" },
  { value: "Hauptlager-Drucker", label: "Hauptlager-Drucker" },
  { value: "Büro-Drucker", label: "Büro-Drucker" },
  { value: "Externer Drucker", label: "Externer Drucker" },
]

export type { ContainerItem, WarehouseLocation }
export default function WarehouseLocationList() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
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
  const [itemsPerPage, setItemsPerPage] = useState(20)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<string>("/")

  useEffect(() => {
    const fetchStorageLocations = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Get the authentication token
        const token = await authService.getToken();
        
        if (!token) {
          // No token found, redirect to login
          window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
          return;
        }
        
        // Construct the correct API endpoint URL including the /api/v1/ prefix
        const inventoryEndpoint = `${API_URL}/api/v1/inventory/storage-locations/`;

        const response = await fetch(inventoryEndpoint, {
          headers: {
            "Accept": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          credentials: "include" // Include cookies for session auth
        });
        
        if (!response.ok) {
          if (response.status === 401) {
            // Try to refresh the token
            const refreshSuccess = await authService.refreshToken();
            if (refreshSuccess) {
              // Retry the request with new token
              const newToken = await authService.getToken();
              const retryResponse = await fetch(inventoryEndpoint, {
                headers: {
                  "Accept": "application/json",
                  "Authorization": `Bearer ${newToken}`,
                },
                credentials: "include"
              });
              
              if (!retryResponse.ok) {
                throw new Error('Authentication failed after token refresh. Please log in again.');
              }
              
              const data = await retryResponse.json();
              handleSuccessResponse(data);
              return;
            } else {
              // Token refresh failed, redirect to login
              window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
              return;
            }
          } else if (response.status === 403) {
            throw new Error('Permission denied. You may need to refresh the page to update your session.');
          } else if (response.status === 404) {
            throw new Error('API endpoint not found. The inventory API might not be properly configured.');
          }
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        handleSuccessResponse(data);
        
      } catch (error) {
        console.error("Error fetching storage locations:", error);
        setError(error instanceof Error ? error.message : "Failed to load storage locations");
        
        // Only use mock data in development
        if (process.env.NODE_ENV === 'development') {
          const mockData = generateMockData(50);
          setLocations(mockData);
          setFilteredLocations(mockData);
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    // Helper function to handle successful response
    const handleSuccessResponse = (data: any[]) => {
      // Map the API response to match our WarehouseLocation type
      const warehouseLocations: WarehouseLocation[] = data.map((item: any) => ({
        id: item.id.toString(),
        laNumber: item.legacy_id ? `LA-${item.legacy_id}` : `LA-${item.id}`,
        location: item.name,
        forSale: item.sale || false,
        specialStorage: item.special_spot || false,
        shelf: parseInt(item.shelf) || 0,
        compartment: parseInt(item.compartment) || 0,
        floor: parseInt(item.unit) || 0,
        containerCount: item.product_count || 0,
        status: item.product_count > 0 ? "in-use" : "free"
      }));
      
      setLocations(warehouseLocations);
      setFilteredLocations(warehouseLocations);
    };
    
    fetchStorageLocations();
  }, []);

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
        <div className="flex">
          <Link
            href="/"
            className={`flex  mx-2 items-center px-4 py-2 rounded-t-lg border-b-2 border-primary text-primary`}
          >
            <Warehouse className="h-4 w-4 mr-2" />
            Lagerort-Verwaltung
          </Link>
          <Link
            href="/container-management"
            className={`flex items-center px-4 py-2 rounded-t-lg border-b-2 border-transparent hover:border-muted hover:text-muted-foreground`}
          >
            <Package2 className="h-4 w-4 mr-2" />
            Schütten-Verwaltung
          </Link>
          <Button
              variant="outline"
              size="sm"
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center gap-1"
            >
            <Settings className="h-4 w-4  mx-2" />
            Einstellungen
          </Button>
        </div>
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

      {error && (
        <div className="p-4 border border-status-error bg-status-error/10 text-status-error rounded-md">
          {error}
        </div>
      )}

      <Card>
        <CardHeader>
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
        </CardHeader>
        <CardContent>
          {/* Loading indicator */}
          {isLoading ? (
            <div className="flex justify-center items-center p-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              <span className="ml-3">Lade Lagerorte...</span>
            </div>
          ) : (
            <>
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
            </>
          )}

          {!isLoading && filteredLocations.length > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between mt-4 gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Einträge pro Seite:</span>
                <Select
                  value={itemsPerPage === filteredLocations.length ? "all" : itemsPerPage.toString()}
                  onValueChange={handleItemsPerPageChange}
                >
                  <SelectTrigger className="w-[100px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="20">20</SelectItem>
                    <SelectItem value="50">50</SelectItem>
                    <SelectItem value="100">100</SelectItem>
                    <SelectItem value="500">500</SelectItem>
                    <SelectItem value="1000">1000</SelectItem>
                    <SelectItem value="all">Alle</SelectItem>
                  </SelectContent>
                </Select>
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

              <div className="text-sm text-muted-foreground">
                Zeige {(currentPage - 1) * itemsPerPage + 1} bis{" "}
                {Math.min(currentPage * itemsPerPage, filteredLocations.length)} von {filteredLocations.length} Einträgen
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Print Section */}
      {!isLoading && (
        <div className="flex items-center gap-4 border-t pt-4">
          <div className="flex-1">
            <Select
              value={selectedPrinter || "none"}
              onValueChange={setSelectedPrinter}
            >
              <SelectTrigger>
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
          <Button variant="default" onClick={handlePrint} disabled={selectedLocations.length === 0 || !selectedPrinter || selectedPrinter === "none"}>
            Lagerorte drucken
          </Button>
        </div>
      )}

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
      <SettingsDialog isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />

    </div>
  )
}

