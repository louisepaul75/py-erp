/**
 * Enum for article activity status
 * - ACTIVE: Article is currently in production
 * - INACTIVE: Article is not in production but may be in the future
 * - DISCONTINUED: Article is permanently discontinued (not shown in UI)
 * - MIXED: Some instances are active, some are inactive
 */
export enum ArticleStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  DISCONTINUED = "discontinued", // Behalten, aber nicht in der UI anzeigen
  MIXED = "mixed",
}

/**
 * Interface for an article instance on a mold
 * Represents a single occurrence of an article on the mold
 */
export interface ArticleInstance {
  id: string
  position: number // Position number on the mold (1, 2, 3, etc.)
  isActive: boolean // Whether this specific instance is active
}

/**
 * Interface for an article on a mold
 */
export interface Article {
  id: string
  oldArticleNumber: string
  newArticleNumber: string
  description: string
  frequency: number // How often this figurine appears on the mold
  status: ArticleStatus // Overall status of the article
  moldId: string // Reference to the parent mold
  instances?: ArticleInstance[] // Individual instances of this article on the mold
}

