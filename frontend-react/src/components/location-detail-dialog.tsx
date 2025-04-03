"use client"

import { useState, useEffect, useCallback } from "react"
import { X, Search, ChevronDown, ChevronRight, History, Trash2 } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import type { WarehouseLocation, ContainerItem } from "@/types/warehouse-types"
import { generateMockContainers } from "@/lib/warehouse-service"
import { moveBox } from "@/lib/inventory/api"
import ActivityLogDialog from "./activity-log-dialog"
import ScannerInputDialog from "./scanner-input-dialog"
import ContainerSelectionDialog from "./container-selection-dialog"
import RemoveContainerDialog from "./remove-container-dialog"
import React from "react"
import { toast } from "sonner"

interface LocationDetailDialogProps {
  isOpen: boolean
  onClose: () => void
  location: WarehouseLocation
}

export default function LocationDetailDialog({ isOpen, onClose, location }: LocationDetailDialogProps) {
  const [containers, setContainers] = useState<ContainerItem[]>([])
  const [isEditing, setIsEditing] = useState(false)
  const [editedLocation, setEditedLocation] = useState<WarehouseLocation>({ ...location })
  const [isScannerDialogOpen, setIsScannerDialogOpen] = useState(false)
  const [isContainerSelectionOpen, setIsContainerSelectionOpen] = useState(false)
  const [isActivityLogOpen, setIsActivityLogOpen] = useState(false)
  const [isRemoveContainerDialogOpen, setIsRemoveContainerDialogOpen] = useState(false)
  const [selectedContainer, setSelectedContainer] = useState<ContainerItem | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredContainers, setFilteredContainers] = useState<ContainerItem[]>([])
  const [expandedContainers, setExpandedContainers] = useState<Record<string, boolean>>({})
  const [hasLocation, setHasLocation] = useState(false)
  const [selectedContainerIds, setSelectedContainerIds] = useState<string[]>([])
  const [mockContainersLoaded, setMockContainersLoaded] = useState(false)
  const [initialExpandedState, setInitialExpandedState] = useState<Record<string, boolean>>({})

  useEffect(() => {
    setHasLocation(!!location)
  }, [location])

  const updateEditedLocation = useCallback(() => {
    if (location) {
      setEditedLocation({ ...location })
    }
  }, [location])

  useEffect(() => {
    updateEditedLocation()
  }, [updateEditedLocation])

  useEffect(() => {
    if (containers.length > 0) {
      const newState: Record<string, boolean> = {}
      containers.forEach((container) => {
        newState[container.containerCode] = true // Set to true to expand by default
      })
      setInitialExpandedState(newState)
    }
  }, [containers])

  useEffect(() => {
    setExpandedContainers(initialExpandedState)
  }, [initialExpandedState])

  useEffect(() => {
    // Lade Mock-Daten für Container, wenn der Lagerort belegt ist
    if (location?.status === "in-use" && location?.containerCount > 0 && !mockContainersLoaded) {
      const mockContainers = generateMockContainers(location.containerCount).map((container) => ({
        ...container,
        // Add multiple articles (1-5 articles per container)
        articles: Array.from({ length: Math.floor(Math.random() * 5) + 1 }, () => ({
          id: crypto.randomUUID(),
          articleNumber: Math.floor(Math.random() * 900000) + 100000,
          oldArticleNumber: `${13200 + Math.floor(Math.random() * 10)}-BE`,
          description: ["Dampfer Herrschung", "neuer Raddampfer Diessen", "Teufel", "Mond mit Mütze", "Kuckucksuhr"][
            Math.floor(Math.random() * 5)
          ],
          stock: Math.floor(Math.random() * 100) + 1,
        })),
      }))
      setContainers(mockContainers)
      setMockContainersLoaded(true)
    }
  }, [location, mockContainersLoaded])

  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredContainers(containers)
      return
    }

    const term = searchTerm.toLowerCase()
    const filtered = containers.filter(
      (container) =>
        container.containerCode.toLowerCase().includes(term) ||
        container.articles?.some(
          (article) =>
            article.articleNumber.toString().includes(term) ||
            article.oldArticleNumber.toLowerCase().includes(term) ||
            article.description.toLowerCase().includes(term),
        ),
    )
    setFilteredContainers(filtered)
  }, [containers, searchTerm])

  const handleSave = () => {
    // Only update the checkbox values
    const updatedLocation = {
      ...location,
      forSale: editedLocation.forSale,
      specialStorage: editedLocation.specialStorage,
    }

    // Here would be the logic to save the changes to the server
    console.log("Saving updated location:", updatedLocation)

    setIsEditing(false)
  }

  const handleScannerSubmit = (scannerCode: string) => {
    console.log("Scanner Code:", scannerCode)

    // Find if the container already exists in the system
    const existingContainer = generateMockContainers(1)[0]
    existingContainer.containerCode = scannerCode
    existingContainer.articles = Array.from({ length: Math.floor(Math.random() * 5) + 1 }, () => ({
      id: crypto.randomUUID(),
      articleNumber: Math.floor(Math.random() * 900000) + 100000,
      oldArticleNumber: `${13200 + Math.floor(Math.random() * 10)}-BE`,
      description: ["Dampfer Herrschung", "neuer Raddampfer Diessen", "Teufel", "Mond mit Mütze", "Kuckucksuhr"][
        Math.floor(Math.random() * 5)
      ],
      stock: Math.floor(Math.random() * 100) + 1,
    }))

    // Add the container to this location
    addContainerToLocation(existingContainer)

    // Close the scanner dialog
    setIsScannerDialogOpen(false)
  }

  const handleContainerSelect = async (container: ContainerItem) => {
    // Add the selected container to this location
    // addContainerToLocation(container); // Move state update after successful API call

    // Close the container selection dialog
    setIsContainerSelectionOpen(false)

    // --- API Call to assign container to location ---
    if (!location || !container) {
      console.error("Missing location or container data for API call")
      toast.error("Fehler: Fehlende Daten zum Zuweisen der Schütte.")
      return
    }

    try {
      // Use the imported moveBox function instead of fetch
      const responseData = await moveBox(
        parseInt(container.id, 10), 
        parseInt(location.id, 10)
      )
      
      console.log("Move box successful:", responseData) // Log success data

      // On successful API call, update the local state
      addContainerToLocation(container)
      toast.success(`Schütte ${container.containerCode} erfolgreich zum Lagerort ${location.laNumber} hinzugefügt.`)
    } catch (error) {
      console.error("Error assigning container to location:", error)
      toast.error(`Fehler beim Zuweisen der Schütte: ${error instanceof Error ? error.message : String(error)}`)
    }
    // --- End API Call ---
  }

  const addContainerToLocation = (container: ContainerItem) => {
    // Add the container to the current location
    setContainers((prev) => [...prev, container])

    // Update the location status and container count
    setEditedLocation((prev) => ({
      ...prev,
      status: "in-use",
      containerCount: prev.containerCount + 1,
    }))
  }

  const handleRemoveContainer = () => {
    if (selectedContainerIds.length === 0) return

    // If only one container is selected, set it as the selected container
    if (selectedContainerIds.length === 1) {
      const containerToRemove = containers.find((c) => c.id === selectedContainerIds[0])
      if (containerToRemove) {
        setSelectedContainer(containerToRemove)
        setIsRemoveContainerDialogOpen(true)
      }
    } else {
      // If multiple containers are selected, show a dialog asking for confirmation to remove all
      setSelectedContainer(null) // No specific container selected
      setIsRemoveContainerDialogOpen(true)
    }
  }

  const confirmRemoveContainer = () => {
    if (selectedContainer) {
      // Remove a single container
      setContainers((prev) => prev.filter((c) => c.id !== selectedContainer.id))
      setSelectedContainerIds((prev) => prev.filter((id) => id !== selectedContainer.id))

      // Update the location status and container count
      const newContainerCount = containers.length - 1
      setEditedLocation((prev) => ({
        ...prev,
        status: newContainerCount === 0 ? "free" : "in-use",
        containerCount: newContainerCount,
      }))
    } else if (selectedContainerIds.length > 0) {
      // Remove multiple containers
      setContainers((prev) => prev.filter((c) => !selectedContainerIds.includes(c.id)))

      // Update the location status and container count
      const newContainerCount = containers.length - selectedContainerIds.length
      setEditedLocation((prev) => ({
        ...prev,
        status: newContainerCount === 0 ? "free" : "in-use",
        containerCount: newContainerCount,
      }))

      // Clear selected container IDs
      setSelectedContainerIds([])
    }

    // Close the dialog
    setIsRemoveContainerDialogOpen(false)
    setSelectedContainer(null)
  }

  const toggleContainerExpand = (containerCode: string) => {
    setExpandedContainers((prev) => ({
      ...prev,
      [containerCode]: !prev[containerCode],
    }))
  }

  const handleSelectContainer = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedContainerIds((prev) => [...prev, id])
    } else {
      setSelectedContainerIds((prev) => prev.filter((containerId) => containerId !== id))
    }
  }

  const handleSelectAllContainers = (checked: boolean) => {
    if (checked) {
      setSelectedContainerIds(filteredContainers.map((c) => c.id))
    } else {
      setSelectedContainerIds([])
    }
  }

  if (!hasLocation) {
    return null
  }

  return (
    <>
      <Dialog.Root open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-4xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-popover p-0 shadow-lg focus:outline-none overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <Dialog.Title className="text-xl font-semibold text-foreground">{location.laNumber}</Dialog.Title>
              <Dialog.Description className="sr-only">
                Details und Aktionen für den Lagerort {location.laNumber}.
              </Dialog.Description>
              <div className="flex items-center gap-2">
                {isEditing ? (
                  <>
                    <Button variant="outline" className="text-foreground" onClick={() => setIsEditing(false)}>
                      Abbrechen
                    </Button>
                    <Button onClick={handleSave}>Speichern</Button>
                  </>
                ) : (
                  <Button variant="outline" className="text-foreground" onClick={() => setIsEditing(true)}>
                    Bearbeiten
                  </Button>
                )}
                <Dialog.Close asChild>
                  <Button variant="ghost" size="icon" onClick={onClose}>
                    <X className="h-4 w-4" />
                  </Button>
                </Dialog.Close>
              </div>
            </div>

            <div className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-foreground">Lager</Label>
                    <div className="p-2 border rounded-md bg-muted text-foreground">{location.location}</div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label className="text-foreground">Land (LKZ)</Label>
                      <div className="p-2 border rounded-md bg-muted text-foreground">DE</div>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-foreground">Ort/Gebäude</Label>
                      <div className="p-2 border rounded-md bg-muted text-foreground">{location.location}</div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      {isEditing ? (
                        <Checkbox
                          id="forSale"
                          checked={editedLocation.forSale}
                          onCheckedChange={(checked: boolean | 'indeterminate') => setEditedLocation({ ...editedLocation, forSale: !!checked })}
                        />
                      ) : (
                        <Checkbox id="forSale" checked={location.forSale} disabled />
                      )}
                      <Label htmlFor="forSale" className="text-foreground">Lagerort für Abverkauf</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      {isEditing ? (
                        <Checkbox
                          id="specialStorage"
                          checked={editedLocation.specialStorage}
                          onCheckedChange={(checked: boolean | 'indeterminate') =>
                            setEditedLocation({ ...editedLocation, specialStorage: !!checked })
                          }
                        />
                      ) : (
                        <Checkbox id="specialStorage" checked={location.specialStorage} disabled />
                      )}
                      <Label htmlFor="specialStorage" className="text-foreground">Sonderlagerort Lagerort</Label>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label className="text-foreground">Regal</Label>
                      <div className="p-2 border rounded-md bg-muted text-foreground">{location.shelf}</div>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-foreground">Fach</Label>
                      <div className="p-2 border rounded-md bg-muted text-foreground">{location.compartment}</div>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-foreground">Boden</Label>
                      <div className="p-2 border rounded-md bg-muted text-foreground">{location.floor}</div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-lg text-foreground">Schütten/Artikel</h3>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex items-center gap-1 text-foreground"
                        onClick={() => setIsActivityLogOpen(true)}
                      >
                        <History className="h-4 w-4" />
                        Aktivitätslog
                      </Button>
                    </div>
                    <div className="relative w-64">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        type="text"
                        placeholder="Suche nach Artikel, Schütte..."
                        className="pl-8"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="border rounded-md overflow-hidden max-h-[400px] overflow-y-auto">
                    <table className="min-w-full divide-y divide-border">
                      <thead className="bg-muted/50 sticky top-0 z-10">
                        <tr>
                          <th className="w-10 px-3 py-2 text-left">
                            <Checkbox
                              checked={
                                selectedContainerIds.length > 0 &&
                                selectedContainerIds.length === filteredContainers.length
                              }
                              onCheckedChange={handleSelectAllContainers}
                              aria-label="Alle Schütten auswählen"
                            />
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground">Schütten/Code</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground">Aktionen</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border bg-background">
                        {filteredContainers.length > 0 ? (
                          filteredContainers.map((container) => (
                            <React.Fragment key={container.id}>
                              <tr
                                className="bg-muted/50 cursor-pointer"
                                onClick={() => toggleContainerExpand(container.containerCode)}
                              >
                                <td className="px-3 py-2">
                                  <Checkbox
                                    checked={selectedContainerIds.includes(container.id)}
                                    onCheckedChange={(checked: boolean | 'indeterminate') => handleSelectContainer(container.id, !!checked)}
                                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                                    aria-label={`Schütte ${container.containerCode} auswählen`}
                                  />
                                </td>
                                <td className="px-3 py-2 text-xs font-medium text-foreground">
                                  <div className="flex items-center">
                                    {expandedContainers[container.containerCode] ? (
                                      <ChevronDown className="h-4 w-4 mr-1" />
                                    ) : (
                                      <ChevronRight className="h-4 w-4 mr-1" />
                                    )}
                                    {container.containerCode}
                                  </div>
                                </td>
                                <td className="px-3 py-2">
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      setSelectedContainer(container)
                                      setIsRemoveContainerDialogOpen(true)
                                    }}
                                  >
                                    <Trash2 className="h-4 w-4 text-destructive" />
                                  </Button>
                                </td>
                              </tr>
                              {expandedContainers[container.containerCode] &&
                                container.articles &&
                                container.articles.length > 0 && (
                                  <tr key={`articles-${container.id}`}>
                                    <td colSpan={4} className="px-3 py-0">
                                      <div className="bg-muted/50 p-2 rounded my-1 ml-6">
                                        <table className="min-w-full">
                                          <thead>
                                            <tr>
                                              <th className="px-2 py-1 text-left text-xs font-medium text-muted-foreground">
                                                Artikel-Nr.
                                              </th>
                                              <th className="px-2 py-1 text-left text-xs font-medium text-muted-foreground">
                                                Alte Artikel-Nr.
                                              </th>
                                              <th className="px-2 py-1 text-left text-xs font-medium text-muted-foreground">
                                                Bezeichnung
                                              </th>
                                              <th className="px-2 py-1 text-left text-xs font-medium text-muted-foreground">
                                                Bestand
                                              </th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {container.articles.map((article) => (
                                              <tr key={article.id} className="border-t border-border">
                                                <td className="px-2 py-1 text-xs text-foreground">{article.articleNumber}</td>
                                                <td className="px-2 py-1 text-xs text-foreground">{article.oldArticleNumber}</td>
                                                <td className="px-2 py-1 text-xs text-foreground">{article.description}</td>
                                                <td className="px-2 py-1 text-xs text-foreground">{article.stock}</td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      </div>
                                    </td>
                                  </tr>
                                )}
                            </React.Fragment>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={4} className="px-3 py-4 text-center text-muted-foreground">
                              {searchTerm ? "Keine Ergebnisse gefunden" : "Keine Schütten vorhanden"}
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
            <div className="p-6 border-t">
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="text-foreground" onClick={() => setIsContainerSelectionOpen(true)}>
                  Schütte hier platzieren
                </Button>
                <Button variant="outline" size="sm" className="text-foreground" onClick={() => setIsScannerDialogOpen(true)}>
                  Schütte platzieren mit Scanner
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-foreground"
                  disabled={selectedContainerIds.length === 0}
                  onClick={handleRemoveContainer}
                >
                  Schütte Entfernen
                </Button>
              </div>
            </div>
          </Dialog.Content>
        </Dialog.Portal>

        {isActivityLogOpen && (
          <ActivityLogDialog
            isOpen={isActivityLogOpen}
            onClose={() => setIsActivityLogOpen(false)}
            locationId={location.id}
            locationType="container"
          />
        )}
      </Dialog.Root>

      {/* Scanner Dialog */}
      {isScannerDialogOpen && (
        <ScannerInputDialog
          isOpen={isScannerDialogOpen}
          onClose={() => setIsScannerDialogOpen(false)}
          onSubmit={handleScannerSubmit}
        />
      )}

      {/* Container Selection Dialog */}
      {isContainerSelectionOpen && (
        <ContainerSelectionDialog
          isOpen={isContainerSelectionOpen}
          onClose={() => setIsContainerSelectionOpen(false)}
          onSelect={handleContainerSelect}
        />
      )}

      {/* Remove Container Dialog */}
      {isRemoveContainerDialogOpen && (
        <RemoveContainerDialog
          isOpen={isRemoveContainerDialogOpen}
          onClose={() => {
            setIsRemoveContainerDialogOpen(false)
            setSelectedContainer(null)
          }}
          container={
            selectedContainer || {
              id: "multiple",
              containerCode: `${selectedContainerIds.length} Schütten`,
              type: "",
              description: "",
              status: "",
              purpose: "",
              stock: 0,
              slots: [],
              units: []
            }
          }
          onConfirm={confirmRemoveContainer}
        />
      )}
    </>
  )
}

