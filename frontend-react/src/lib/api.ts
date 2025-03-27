import type { Item, BookingItem, HistoryEntry } from "./types"

// Mock data for demonstration
const mockItems: Item[] = [
  {
    id: "1",
    articleOld: "A1001",
    articleNew: "N2001",
    description: "Wireless Headphones",
    quantity: 10,
    slotCodes: ["S101", "S102"],
    boxNumber: "B001",
  },
  {
    id: "2",
    articleOld: "A1002",
    articleNew: "N2002",
    description: "USB-C Cable",
    quantity: 25,
    slotCodes: ["S103"],
    boxNumber: "B001",
  },
  {
    id: "3",
    articleOld: "A1003",
    articleNew: "N2003",
    description: "Wireless Mouse",
    quantity: 15,
    slotCodes: ["S104", "S105"],
    boxNumber: "B002",
  },
  {
    id: "4",
    articleOld: "A1004",
    articleNew: "N2004",
    description: "Power Bank",
    quantity: 8,
    slotCodes: ["S106"],
    orderNumber: "O001",
  },
  {
    id: "5",
    articleOld: "A1005",
    articleNew: "N2005",
    description: "Bluetooth Speaker",
    quantity: 12,
    slotCodes: ["S107"],
    orderNumber: "O001",
  },
]

// Aktualisiere die Mock-History-Einträge, um Korrekturen zu enthalten
export const mockHistoryEntries: HistoryEntry[] = [
  {
    id: "h1",
    timestamp: "2023-06-15T10:30:00Z",
    user: "John Doe",
    articleOld: "A1001",
    articleNew: "N2001",
    quantity: 5,
    sourceSlot: "S101",
    targetSlot: "T201",
    boxNumber: "B001",
  },
  {
    id: "h2",
    timestamp: "2023-06-15T11:45:00Z",
    user: "Jane Smith",
    articleOld: "A1002",
    articleNew: "N2002",
    quantity: 10,
    sourceSlot: "S103",
    targetSlot: "T202",
    boxNumber: "B001",
  },
  {
    id: "h3",
    timestamp: "2023-06-16T09:15:00Z",
    user: "John Doe",
    articleOld: "A1004",
    articleNew: "N2004",
    quantity: 3,
    sourceSlot: "S106",
    targetSlot: "T203",
    orderNumber: "O001",
  },
  {
    id: "mock-h4",
    timestamp: "2023-06-17T14:20:00Z",
    user: "mock-admin",
    articleOld: "A1001",
    articleNew: "N2001",
    quantity: 2,
    sourceSlot: "mock-inventory",
    targetSlot: "mock-inventory",
    boxNumber: "B001",
    correction: {
      type: "inventory_correction",
      reason: "additional_found",
      amount: 2,
      note: "Zusätzliche Artikel im Lager gefunden",
      oldQuantity: 8,
      newQuantity: 10,
    },
  },
  {
    id: "mock-h5",
    timestamp: "2023-06-18T09:30:00Z",
    user: "mock-warehouse",
    articleOld: "A1003",
    articleNew: "N2003",
    quantity: 3,
    sourceSlot: "mock-inventory",
    targetSlot: "mock-inventory",
    boxNumber: "B002",
    correction: {
      type: "inventory_correction",
      reason: "damage_broken_irrepairable",
      amount: 3,
      note: "Beschädigte Artikel aussortiert",
      oldQuantity: 18,
      newQuantity: 15,
    },
  },
  {
    id: "mock-h6",
    timestamp: "2023-06-18T15:45:00Z",
    user: "mock-supervisor",
    articleOld: "A1005",
    articleNew: "N2005",
    quantity: 2,
    sourceSlot: "S107",
    targetSlot: "T205",
    orderNumber: "O001",
    correction: {
      type: "excess",
      reason: "wrong_previous_booking",
      amount: 2,
      note: "Falsche Buchung korrigiert",
    },
  },
]

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// API functions
export async function fetchItemsByBox(boxNumber: string): Promise<Item[]> {
  await delay(500) // Simulate network delay
  return mockItems.filter((item) => item.boxNumber === boxNumber)
}

export async function fetchItemsByOrder(orderNumber: string): Promise<Item[]> {
  await delay(500) // Simulate network delay
  return mockItems.filter((item) => item.orderNumber === orderNumber)
}

export async function bookItems(items: BookingItem[]): Promise<BookingItem[]> {
  await delay(1000) // Simulate network delay

  // In a real implementation, this would send the booking to the server
  // and update the inventory

  // Simulate WebSocket message to other clients using our custom event
  if (typeof window !== "undefined") {
    const mockEvent = new CustomEvent("mock-ws-message", {
      detail: {
        type: "INVENTORY_UPDATED",
        items: items.map((item) => item.id),
        timestamp: new Date().toISOString(),
      },
    })

    window.dispatchEvent(mockEvent)
  }

  return items
}

export async function fetchMovementHistory(fromDate?: Date, toDate?: Date): Promise<HistoryEntry[]> {
  // Diese Funktion wird nicht mehr verwendet, da wir jetzt den HistoryContext verwenden
  await delay(500) // Simulate network delay
  return []
}

