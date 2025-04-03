"use client"

import { useState, useEffect } from "react"
import { X, Search, ExternalLink, ChevronRight, ChevronDown } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { generateMockContainers } from "@/lib/warehouse-service"
import type { ContainerItem } from "@/types/warehouse-types"
import ConfirmationDialog from "./confirmation-dialog"

interface ContainerSelectionDialogProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (container: ContainerItem) => void
}

export default function ContainerSelectionDialog({ isOpen, onClose, onSelect }: ContainerSelectionDialogProps) {
  const [containers, setContainers] = useState<ContainerItem[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredContainers, setFilteredContainers] = useState<ContainerItem[]>([])
  const [selectedContainer, setSelectedContainer] = useState<ContainerItem | null>(null)
  const [isConfirmationOpen, setIsConfirmationOpen] = useState(false)
  const [existingLocation, setExistingLocation] = useState<string | null>(null)
  const [expandedContainers, setExpandedContainers] = useState<Record<string, boolean>>({})

  useEffect(() => {
    // Lade Mock-Daten für verfügbare Container
    const mockContainers = generateMockContainers(20, true)
    setContainers(mockContainers)

    // Initialize all containers as collapsed
    const initialExpandedState: Record<string, boolean> = {}
    mockContainers.forEach((container) => {
      initialExpandedState[container.containerCode] = false
    })
    setExpandedContainers(initialExpandedState)
  }, [])

  useEffect(() => {
    if (!searchTerm) {
      setFilteredContainers(containers)
      return
    }

    const term = searchTerm.toLowerCase()
    const filtered = containers.filter(
      (container) =>
        container.containerCode.toLowerCase().includes(term) ||
        container.units.some(
          (unit) =>
            unit.articleNumber?.toString().includes(term) ||
            unit.oldArticleNumber?.toLowerCase().includes(term) ||
            unit.description?.toLowerCase().includes(term),
        ),
    )
    setFilteredContainers(filtered)
  }, [containers, searchTerm])

  const handleSelectContainer = (container: ContainerItem) => {
    // Check if container already has a location
    if (container.location) {
      setSelectedContainer(container)
      setExistingLocation(`${container.shelf}/${container.compartment}/${container.floor}`)
      setIsConfirmationOpen(true)
    } else {
      // If no existing location, proceed directly
      onSelect(container)
    }
  }

  const handleConfirmMove = () => {
    if (selectedContainer) {
      onSelect(selectedContainer)
    }
    setIsConfirmationOpen(false)
    setSelectedContainer(null)
    setExistingLocation(null)
  }

  const toggleContainerExpand = (containerCode: string) => {
    setExpandedContainers((prev) => ({
      ...prev,
      [containerCode]: !prev[containerCode],
    }))
  }

  return (
    <>
      <Dialog.Root open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
          <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-2xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-popover p-0 shadow-lg focus:outline-none">
            <div className="flex items-center justify-between p-4 border-b">
              <Dialog.Title className="text-xl font-semibold text-foreground">Schütte auswählen</Dialog.Title>
              <Dialog.Close asChild>
                <Button variant="ghost" size="icon" onClick={onClose}>
                  <X className="h-4 w-4" />
                </Button>
              </Dialog.Close>
            </div>

            <div className="p-4 space-y-4">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Suche nach Schüttennummer, Artikel..."
                  className="pl-8"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <div className="border rounded-md overflow-hidden max-h-[400px] overflow-y-auto">
                <table className="min-w-full divide-y divide-border">
                  <thead className="bg-muted/50 sticky top-0 z-10">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Schütten</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Aktueller Lagerort</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border bg-background">
                    {filteredContainers.length > 0 ? (
                      filteredContainers.map((container) => (
                        <>
                          <tr
                            key={container.id}
                            className="hover:bg-muted/50 cursor-pointer"
                            onClick={() => toggleContainerExpand(container.containerCode)}
                          >
                            <td className="px-4 py-3 text-sm text-foreground">
                              <div className="flex items-center">
                                {expandedContainers[container.containerCode] ? (
                                  <ChevronDown className="h-4 w-4 mr-1" />
                                ) : (
                                  <ChevronRight className="h-4 w-4 mr-1" />
                                )}
                                {container.containerCode}
                              </div>
                            </td>
                            <td className="px-4 py-3 text-sm text-foreground">
                              {container.location ? (
                                <div className="flex items-center text-primary">
                                  {container.shelf}/{container.compartment}/{container.floor}
                                  <ExternalLink className="h-3 w-3 ml-1" />
                                </div>
                              ) : (
                                <span className="text-muted-foreground">-</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-foreground"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleSelectContainer(container)
                                }}
                              >
                                Auswählen
                              </Button>
                            </td>
                          </tr>
                          {expandedContainers[container.containerCode] &&
                            container.units &&
                            container.units.length > 0 && (
                              <tr key={`units-${container.id}`}>
                                <td colSpan={3} className="px-4 py-0">
                                  <div className="bg-muted/50 p-2 rounded my-1">
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
                                        {container.units.map((unit) => (
                                          <tr key={unit.id} className="border-t border-border">
                                            <td className="px-2 py-1 text-xs text-foreground">{unit.articleNumber}</td>
                                            <td className="px-2 py-1 text-xs text-foreground">{unit.oldArticleNumber}</td>
                                            <td className="px-2 py-1 text-xs text-foreground">{unit.description}</td>
                                            <td className="px-2 py-1 text-xs text-foreground">{unit.stock}</td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </td>
                              </tr>
                            )}
                        </>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3} className="px-4 py-6 text-center text-muted-foreground">
                          Keine Schütten gefunden
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="pt-4 flex justify-end space-x-2">
                <Button variant="outline" className="text-foreground" onClick={onClose}>
                  Abbrechen
                </Button>
              </div>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      {isConfirmationOpen && existingLocation && (
        <ConfirmationDialog
          isOpen={isConfirmationOpen}
          onClose={() => {
            setIsConfirmationOpen(false)
            setSelectedContainer(null)
            setExistingLocation(null)
          }}
          onConfirm={handleConfirmMove}
          title="Schütte verschieben"
          message={`Die Schütte befindet sich bereits im Lagerort ${existingLocation}. Möchten Sie die Schütte wirklich in diesen Lagerort verschieben?`}
          confirmText="Ja, verschieben"
          cancelText="Abbrechen"
        />
      )}
    </>
  )
}

