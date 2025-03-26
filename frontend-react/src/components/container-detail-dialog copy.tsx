"use client"

import { useState, useEffect, useRef } from "react"
import { X, History } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import type { ContainerItem } from "@/types/warehouse-types"
import { generateContainerSlots, generateInitialUnits, splitUnit, renumberUnits } from "@/lib/container-utils"
import ActivityLogDialog from "./activity-log-dialog"
import React from "react"
import ConfirmationDialog from "./confirmation-dialog"
import ContainerInfoTab from "./container/container-info-tab"
import ContainerUnitsTab from "./container/container-units-tab"
import ContainerLocationTab from "./container/container-location-tab"

interface ContainerDetailDialogProps {
  isOpen: boolean
  onClose: () => void
  container: ContainerItem
  onLocationClick?: (shelf: number, compartment: number, floor: number) => void
  onSave?: (updatedContainer: ContainerItem) => void
}

export default function ContainerDetailDialog({
  isOpen,
  onClose,
  container,
  onLocationClick,
  onSave,
}: ContainerDetailDialogProps) {
  // Initialize with safe defaults
  const safeContainer = {
    ...container,
    slots: Array.isArray(container.slots) ? container.slots : [],
    units: Array.isArray(container.units) ? container.units : [],
  }

  const [isEditing, setIsEditing] = useState(false)
  const [editedContainer, setEditedContainer] = useState<ContainerItem>(safeContainer)
  const [isActivityLogOpen, setIsActivityLogOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("info")
  const [selectedUnitId, setSelectedUnitId] = useState<string | null>(null)
  const [selectedSlotIds, setSelectedSlotIds] = useState<string[]>([])
  const [slotCount, setSlotCount] = useState<number>(
    Array.isArray(safeContainer.slots) ? safeContainer.slots.length : 1,
  )
  const [isConfirmationOpen, setIsConfirmationOpen] = useState(false)
  const [pendingAction, setPendingAction] = useState<(() => void) | null>(null)
  const [expandedContainers, setExpandedContainers] = useState<Record<string, boolean>>({})

  // Store the original dates to prevent them from changing
  const dateInfoRef = useRef({
    createdAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000),
    lastModified: new Date(Date.now() - Math.floor(Math.random() * 10) * 24 * 60 * 60 * 1000),
    printedAt: new Date(Date.now() - Math.floor(Math.random() * 20) * 24 * 60 * 60 * 1000),
  })

  // Use useMemo to prevent recreating initialContainer on every render
  const initialContainer = React.useMemo(
    () => ({
      id: container.id,
      containerCode: container.containerCode,
      type: container.type,
      slots: Array.isArray(container.slots) ? container.slots : [],
      units: Array.isArray(container.units) ? container.units : [],
    }),
    [container.id, container.containerCode, container.type],
  ) // Only depend on stable props

  // Initialize state once with the initial container data
  useEffect(() => {
    if (!isOpen) return // Only run when dialog is open

    try {
      // Initialize container with slots and units if they don't exist
      const updatedContainer = { ...initialContainer }

      // Generate slots if needed
      if (!Array.isArray(updatedContainer.slots) || updatedContainer.slots.length === 0) {
        const newSlots = generateContainerSlots(updatedContainer.type || "")
        updatedContainer.slots = Array.isArray(newSlots) ? newSlots : []
      }

      // Generate units if needed
      if (!Array.isArray(updatedContainer.units) || updatedContainer.units.length === 0) {
        const newUnits = generateInitialUnits(updatedContainer.slots)
        updatedContainer.units = Array.isArray(newUnits) ? newUnits : []
      }

      // Ensure units are properly numbered
      const numberedContainer = renumberUnits(updatedContainer)

      setEditedContainer(numberedContainer)
      setSlotCount(numberedContainer.slots?.length || 1)
    } catch (error) {
      console.error("Error initializing container:", error)
      // Fallback to safe defaults
      setEditedContainer(initialContainer)
    }
  }, [isOpen, initialContainer]) // Only depend on isOpen and initialContainer

  useEffect(() => {
    const containers = [container] // Create an array containing only the current container
    if (containers.length > 0) {
      const initialExpandedState: Record<string, boolean> = {}
      containers.forEach((container) => {
        initialExpandedState[container.containerCode] = true // Set to true to expand by default
      })
      setExpandedContainers(initialExpandedState)
    }
  }, [container])

  const handleSave = () => {
    try {
      // Wenn die Slot-Anzahl geändert wurde, aktualisiere die Slots
      if (slotCount !== editedContainer.slots.length) {
        handleSlotCountChange(slotCount)
      }

      if (onSave) {
        onSave(editedContainer)
      }
    } catch (error) {
      console.error("Error saving container:", error)
    }
  }

  const handleSlotCountChange = (newSlotCount: number) => {
    try {
      let updatedContainer = { ...editedContainer }

      // Generate new slots based on the selected count
      const newSlots = generateContainerSlots(updatedContainer.type || "", [], newSlotCount)
      if (!Array.isArray(newSlots)) {
        throw new Error("Failed to generate slots")
      }

      // Create new units for the slots
      const newUnits = generateInitialUnits(newSlots)
      if (!Array.isArray(newUnits)) {
        throw new Error("Failed to generate units")
      }

      // Transfer article data from old units to new units if possible
      if (Array.isArray(updatedContainer.units) && updatedContainer.units.length > 0 && newUnits.length > 0) {
        const oldUnit = updatedContainer.units[0]
        if (oldUnit) {
          newUnits[0] = {
            ...newUnits[0],
            articleNumber: oldUnit.articleNumber,
            oldArticleNumber: oldUnit.oldArticleNumber,
            description: oldUnit.description,
            stock: oldUnit.stock,
          }
        }
      }

      updatedContainer = {
        ...updatedContainer,
        slots: newSlots,
        units: newUnits,
      }

      setEditedContainer(updatedContainer)
    } catch (error) {
      console.error("Error changing slot count:", error)
    }
  }

  const handleSplitUnit = () => {
    try {
      if (!selectedUnitId) return

      const unit = editedContainer.units.find((u) => u.id === selectedUnitId)
      if (!unit || !Array.isArray(unit.slots) || unit.slots.length <= 1) return

      // Check if this unit has article data
      const hasArticleData =
        unit.articleNumber || unit.oldArticleNumber || unit.description || (unit.stock && unit.stock > 0)

      if (hasArticleData) {
        // Show confirmation dialog
        setIsConfirmationOpen(true)
        setPendingAction(() => () => {
          // Split in the middle by default
          const splitIndex = Math.floor(unit.slots.length / 2)
          const slotsToSplit = unit.slots.slice(0, splitIndex)
          const updatedContainer = splitUnit(editedContainer, selectedUnitId, slotsToSplit)
          setEditedContainer(updatedContainer)
        })
      } else {
        // No article data to lose, proceed normally
        const splitIndex = Math.floor(unit.slots.length / 2)
        const slotsToSplit = unit.slots.slice(0, splitIndex)
        const updatedContainer = splitUnit(editedContainer, selectedUnitId, slotsToSplit)
        setEditedContainer(updatedContainer)
      }
    } catch (error) {
      console.error("Error splitting unit:", error)
    }
  }

  // Generiere zufällige Lagerinformationen
  const locationInfo = {
    location: ["Hauptlager 1", "Hauptlager 2", "Externes Lager", "Nebenlager"][Math.floor(Math.random() * 4)],
    shelf: Math.floor(Math.random() * 20) + 1,
    compartment: Math.floor(Math.random() * 10) + 1,
    floor: Math.floor(Math.random() * 5) + 1,
    status: Math.random() > 0.5 ? "Aktiv" : "Inaktiv",
  }

  const navigateToLocation = () => {
    // Close the current dialog
    onClose()

    // Use the callback if provided
    if (onLocationClick) {
      onLocationClick(locationInfo.shelf, locationInfo.compartment, locationInfo.floor)
    } else {
      // Fallback to direct navigation
      window.location.href = `/?shelf=${locationInfo.shelf}&compartment=${locationInfo.compartment}&floor=${locationInfo.floor}`
    }
  }

  // Function to show confirmation dialog
  const showConfirmationDialog = (action: () => void) => {
    setIsConfirmationOpen(true)
    setPendingAction(() => action)
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-4xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold">{container.containerCode}</Dialog.Title>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsActivityLogOpen(true)}
                className="flex items-center gap-1"
              >
                <History className="h-4 w-4" />
                Aktivitätslog
              </Button>
              {isEditing ? (
                <>
                  <Button variant="outline" onClick={() => setIsEditing(false)}>
                    Abbrechen
                  </Button>
                  <Button onClick={handleSave}>Speichern</Button>
                </>
              ) : (
                <Button variant="outline" onClick={() => setIsEditing(true)}>
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

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="w-full flex justify-start px-6 pt-4">
              <TabsTrigger value="info" className="flex-1">
                Schütten-Informationen
              </TabsTrigger>
              <TabsTrigger value="units" className="flex-1">
                Einheiten & Artikel
              </TabsTrigger>
              <TabsTrigger value="location" className="flex-1">
                Lagerort
              </TabsTrigger>
            </TabsList>

            <TabsContent value="info" className="p-6 space-y-6">
              <ContainerInfoTab
                container={container}
                editedContainer={editedContainer}
                setEditedContainer={setEditedContainer}
                isEditing={isEditing}
                slotCount={slotCount}
                setSlotCount={setSlotCount}
                dateInfo={dateInfoRef.current}
              />
            </TabsContent>

            <TabsContent value="units" className="p-6 space-y-6 overflow-y-auto max-h-[60vh]">
              <ContainerUnitsTab
                editedContainer={editedContainer}
                setEditedContainer={setEditedContainer}
                selectedUnitId={selectedUnitId}
                setSelectedUnitId={setSelectedUnitId}
                selectedSlotIds={selectedSlotIds}
                setSelectedSlotIds={setSelectedSlotIds}
                onSplitUnit={handleSplitUnit}
                showConfirmationDialog={showConfirmationDialog}
              />
            </TabsContent>

            <TabsContent value="location" className="p-6 space-y-6">
              <ContainerLocationTab locationInfo={locationInfo} onNavigateToLocation={navigateToLocation} />
            </TabsContent>
          </Tabs>

          <div className="p-6 border-t flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Schließen
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>

      {isConfirmationOpen && pendingAction && (
        <ConfirmationDialog
          isOpen={isConfirmationOpen}
          onClose={() => {
            setIsConfirmationOpen(false)
            setPendingAction(null)
          }}
          onConfirm={() => {
            pendingAction()
            setIsConfirmationOpen(false)
            setPendingAction(null)
          }}
          title="Artikel-Daten gehen verloren"
          message="Durch das Erstellen einer neuen Einheit werden Artikel-Daten gelöscht. Möchten Sie fortfahren?"
          confirmText="Ja, fortfahren"
          cancelText="Abbrechen"
        />
      )}

      {isActivityLogOpen && (
        <ActivityLogDialog
          isOpen={isActivityLogOpen}
          onClose={() => setIsActivityLogOpen(false)}
          entityId={container.id}
          locationType="container"
        />
      )}
    </Dialog.Root>
  )
}

