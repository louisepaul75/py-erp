export type WarehouseLocation = {
  id: string
  laNumber: string
  location: string
  forSale: boolean
  specialStorage: boolean
  shelf: number
  compartment: number
  floor: number
  containerCount: number
  status: "free" | "in-use"
}

export type SlotCode = {
  code: string
  color: string
}

export type ContainerSlot = {
  id: string
  code: SlotCode
  unitId: string
}

export type ContainerUnit = {
  id: string
  unitNumber: number
  slots: string[] // Array of slot IDs
  articleNumber?: string
  oldArticleNumber?: string
  description?: string
  stock?: number
}

export type ContainerLocation = {
  laNumber: string
  shelf: number
  compartment: number
  floor: number
}

export type ContainerArticle = {
  id: string
  articleNumber: number
  oldArticleNumber: string
  description: string
  stock: number
}

export interface ContainerItem {
  id: string;
  containerCode: string; // Box code
  displayCode?: string; // For display purposes
  type: string; // Box type code (e.g., "AR", "KC")
  description: string;
  status: string;
  purpose: string;
  location?: string; // Storage location name
  shelf?: number;
  compartment?: number;
  floor?: number;
  stock: number;
  articleNumber?: string; // Primary article number (if any)
  oldArticleNumber?: string; // Legacy article number (if any)
  lastPrintDate?: Date | null;
  slots: SlotItem[]; // Box slots
  units: UnitItem[]; // Logical units within the box
  customSlotCount?: number; // Custom number of slots for the container
  articles?: ContainerArticle[]; // Articles in the container
}

export interface SlotItem {
  id: string;
  code: {
    code: string; // Slot code
    color: string; // CSS class for slot color
  };
}

export interface UnitItem {
  id: string;
  unitNumber: number;
  slots: string[]; // IDs of slots that belong to this unit
  articleNumber?: string;
  oldArticleNumber?: string;
  description?: string;
  stock?: number;
}

export type ContainerTypeDefinition = {
  id: string
  name: string
  standardSlots: number
}

