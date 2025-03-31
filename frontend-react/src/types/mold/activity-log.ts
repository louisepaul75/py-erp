/**
 * Enum für die verschiedenen Arten von Aktivitäten
 */
export enum ActivityType {
  CREATE = "create",
  UPDATE = "update",
  DELETE = "delete",
}

/**
 * Enum für die verschiedenen Entitätstypen
 */
export enum EntityType {
  MOLD = "mold",
  ARTICLE = "article",
  ARTICLE_INSTANCE = "article_instance",
  TECHNOLOGY = "technology",
  ALLOY = "alloy",
  TAG = "tag",
  MOLD_SIZE = "mold_size",
}

/**
 * Interface für einen Activity Log Eintrag
 */
export interface ActivityLogEntry {
  id: string
  timestamp: string
  userId: string
  userName: string
  activityType: ActivityType
  entityType: EntityType
  entityId: string
  entityName: string
  details: string
  changes?: {
    field: string
    oldValue: any
    newValue: any
  }[]
}

/**
 * Mock-Benutzer für das Activity Log
 */
export const mockUsers = [
  { id: "user1", name: "Admin User" },
  { id: "user2", name: "Production Manager" },
  { id: "user3", name: "Quality Inspector" },
]

/**
 * Aktueller Benutzer (in einer echten Anwendung würde dies aus der Authentifizierung kommen)
 */
export const currentUser = mockUsers[0]

