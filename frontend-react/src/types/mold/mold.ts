import type { Article } from "./article"

/**
 * Enum for mold activity status
 */
export enum MoldActivityStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  MIXED = "mixed",
}

/**
 * Interface for a mold
 */
export interface Mold {
  id: string
  legacyMoldNumber: string
  moldNumber: string
  technology: string
  alloy: string
  warehouseLocation: string
  numberOfArticles: number
  isActive: boolean
  activityStatus?: MoldActivityStatus // Neues Feld für den detaillierten Status
  tags?: string[]
  createdDate: string

  // Neue Felder
  startDate?: string // ISO date string
  endDate?: string // ISO date string
  imageUrl?: string // URL to the mold image
  moldSize?: string // Reference to the mold size name
  articles?: Article[] // Articles on this mold
}

