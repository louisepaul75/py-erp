import type { DocumentHistoryEntry, User } from "@/types/document/document-history"

/**
 * Mock users for history entries
 */
export const mockUsers: User[] = [
  {
    id: "user-1",
    name: "Max Mustermann",
    role: "Administrator",
    email: "max.mustermann@example.com",
  },
  {
    id: "user-2",
    name: "Anna Schmidt",
    role: "Sachbearbeiter",
    email: "anna.schmidt@example.com",
  },
  {
    id: "user-3",
    name: "Thomas Weber",
    role: "Vertriebsmitarbeiter",
    email: "thomas.weber@example.com",
  },
  {
    id: "user-4",
    name: "Julia Becker",
    role: "Buchhaltung",
    email: "julia.becker@example.com",
  },
  {
    id: "user-5",
    name: "System",
    role: "Automatisierung",
    email: "system@example.com",
  },
]

/**
 * Generate mock history entries for a document
 */
export function generateMockHistoryEntries(documentId: string): DocumentHistoryEntry[] {
  // Get a random user
  const getRandomUser = () => mockUsers[Math.floor(Math.random() * (mockUsers.length - 1))]

  // Current date for the most recent entry
  const now = new Date()

  // Generate random dates in the past (up to 30 days ago)
  const getRandomPastDate = (maxDaysAgo: number) => {
    const date = new Date(now)
    date.setDate(date.getDate() - Math.floor(Math.random() * maxDaysAgo))
    date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60))
    return date
  }

  // Create entries based on document lifecycle
  const creationDate = getRandomPastDate(30)
  const updateDate = getRandomPastDate(20)
  const statusChangeDate = getRandomPastDate(15)
  const itemAddDate = getRandomPastDate(10)
  const relationAddDate = getRandomPastDate(5)

  // Sort dates chronologically
  const dates = [
    { date: creationDate, type: "CREATE" },
    { date: updateDate, type: "UPDATE" },
    { date: statusChangeDate, type: "STATUS_CHANGE" },
    { date: itemAddDate, type: "ITEM_ADD" },
    { date: relationAddDate, type: "RELATION_ADD" },
  ].sort((a, b) => a.date.getTime() - b.date.getTime())

  // Generate entries
  return dates.map((entry, index) => {
    const user = getRandomUser()
    let description = ""
    let oldValue = ""
    let newValue = ""

    switch (entry.type) {
      case "CREATE":
        description = "Dokument erstellt"
        break
      case "UPDATE":
        description = "Dokumentdetails aktualisiert"
        oldValue = "Kunde: Alte Firma GmbH"
        newValue = "Kunde: Neue Firma AG"
        break
      case "STATUS_CHANGE":
        description = "Status geändert"
        oldValue = "OPEN"
        newValue = "CONFIRMED"
        break
      case "ITEM_ADD":
        description = "Position hinzugefügt"
        newValue = "PROD-123 - Laptop Computer (2 x 899.99 €)"
        break
      case "RELATION_ADD":
        description = "Dokumentbeziehung hinzugefügt"
        newValue = "Lieferschein DEL-2023-042 basierend auf diesem Dokument"
        break
    }

    return {
      id: `history-${documentId}-${index}`,
      documentId,
      timestamp: entry.date.toISOString(),
      userId: user.id,
      userName: user.name,
      actionType: entry.type as any,
      description,
      oldValue,
      newValue,
      metadata: {
        userRole: user.role,
      },
    }
  })
}

/**
 * Predefined cancellation reasons
 */
export const cancellationReasons = [
  // Kundengründe
  { id: "customer-1", category: "Kundengrund", description: "Kunde hat storniert" },
  { id: "customer-2", category: "Kundengrund", description: "Kunde hat Zahlungsprobleme" },
  { id: "customer-3", category: "Kundengrund", description: "Kunde hat Artikel anderweitig beschafft" },
  { id: "customer-4", category: "Kundengrund", description: "Kunde hat falsch bestellt" },

  // Interne Gründe
  { id: "internal-1", category: "Interner Grund", description: "Artikel nicht lieferbar" },
  { id: "internal-2", category: "Interner Grund", description: "Preisfehler" },
  { id: "internal-3", category: "Interner Grund", description: "Doppelte Bestellung" },
  { id: "internal-4", category: "Interner Grund", description: "Bestellung kann nicht erfüllt werden" },

  // Technische Gründe
  { id: "technical-1", category: "Technischer Grund", description: "Systemfehler" },
  { id: "technical-2", category: "Technischer Grund", description: "Datenfehler" },
  { id: "technical-3", category: "Technischer Grund", description: "Import/Export-Fehler" },

  // Sonstige Gründe
  { id: "other-1", category: "Sonstiger Grund", description: "Testbestellung" },
  { id: "other-2", category: "Sonstiger Grund", description: "Sonstiger Grund" },
]
