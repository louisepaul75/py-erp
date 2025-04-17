/**
 * Types of document history actions
 */
export type HistoryActionType =
  | "CREATE"
  | "UPDATE"
  | "STATUS_CHANGE"
  | "CANCEL"
  | "ITEM_ADD"
  | "ITEM_REMOVE"
  | "ITEM_UPDATE"
  | "RELATION_ADD"
  | "RELATION_REMOVE"

/**
 * Document history entry interface
 */
export interface DocumentHistoryEntry {
  id: string
  documentId: string
  timestamp: string
  userId: string
  userName: string
  actionType: HistoryActionType
  description: string
  oldValue?: string
  newValue?: string
  metadata?: Record<string, any>
}

/**
 * User interface for history tracking
 */
export interface User {
  id: string
  name: string
  role: string
  email: string
}
