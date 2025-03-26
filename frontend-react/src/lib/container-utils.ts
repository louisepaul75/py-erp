import type { ContainerItem, ContainerSlot, ContainerUnit, SlotCode } from "@/types/warehouse-types"

// Helper function to generate a random color
const generateRandomColor = (): string => {
  const colors = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD",
    "#D4A5A5", "#9FA8DA", "#CE93D8", "#80CBC4", "#FFE082"
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

// Helper function to generate a slot code
const generateSlotCode = (index: number): SlotCode => {
  return {
    code: `S${String(index + 1).padStart(2, '0')}`,
    color: generateRandomColor()
  }
}

/**
 * Generates container slots based on container type and count
 */
export const generateContainerSlots = (
  containerType: string,
  existingSlots: ContainerSlot[] = [],
  slotCount?: number
): ContainerSlot[] => {
  // If slotCount is not provided, determine it based on container type
  const count = slotCount ?? (containerType === "large" ? 8 : containerType === "medium" ? 4 : 2)
  
  return Array.from({ length: count }, (_, index) => {
    // Reuse existing slot if available
    if (existingSlots[index]) {
      return existingSlots[index]
    }
    
    return {
      id: crypto.randomUUID(),
      code: generateSlotCode(index),
      unitId: "" // Will be assigned when generating units
    }
  })
}

/**
 * Generates initial units for container slots
 */
export const generateInitialUnits = (slots: ContainerSlot[]): ContainerUnit[] => {
  if (!slots.length) return []

  // Create a single unit that contains all slots initially
  const unit: ContainerUnit = {
    id: crypto.randomUUID(),
    unitNumber: 1,
    slots: slots.map(slot => slot.id),
    articleNumber: "",
    oldArticleNumber: "",
    description: "",
    stock: 0
  }

  // Update slot unitIds
  slots.forEach(slot => {
    slot.unitId = unit.id
  })

  return [unit]
}

/**
 * Splits a unit into two units based on selected slots
 */
export const splitUnit = (
  container: ContainerItem,
  unitId: string,
  slotsToSplit: string[]
): ContainerItem => {
  const originalUnit = container.units.find(u => u.id === unitId)
  if (!originalUnit) return container

  // Create new unit for split slots
  const newUnit: ContainerUnit = {
    id: crypto.randomUUID(),
    unitNumber: container.units.length + 1,
    slots: slotsToSplit,
    articleNumber: "",
    oldArticleNumber: "",
    description: "",
    stock: 0
  }

  // Update original unit's slots
  const remainingSlots = originalUnit.slots.filter(id => !slotsToSplit.includes(id))
  const updatedOriginalUnit = { ...originalUnit, slots: remainingSlots }

  // Update slot unitIds
  const updatedSlots = container.slots.map(slot => {
    if (slotsToSplit.includes(slot.id)) {
      return { ...slot, unitId: newUnit.id }
    }
    return slot
  })

  // Update container with new and modified units
  return {
    ...container,
    slots: updatedSlots,
    units: container.units.map(u => 
      u.id === unitId ? updatedOriginalUnit : u
    ).concat(newUnit)
  }
}

/**
 * Renumbers all units in sequential order
 */
export const renumberUnits = (container: ContainerItem): ContainerItem => {
  const updatedUnits = container.units.map((unit, index) => ({
    ...unit,
    unitNumber: index + 1
  }))

  return {
    ...container,
    units: updatedUnits
  }
} 