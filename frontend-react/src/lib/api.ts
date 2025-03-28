import type { Item, BookingItem, HistoryEntry, Order, OrderItem, BinLocation } from "@/types/types"
import ky from 'ky';
import { API_URL, AUTH_CONFIG } from './config';
import { csrfService } from './auth/authService';

// Create an API client instance with the correct base URL and auth
const api = ky.create({
  prefixUrl: API_URL,
  timeout: 30000,
  credentials: 'include', // Include cookies in requests
  hooks: {
    beforeRequest: [
      request => {
        // Add CSRF token to non-GET requests if available
        if (request.method !== 'GET') {
          const csrfToken = csrfService.getToken();
          if (csrfToken) {
            request.headers.set('X-CSRFToken', csrfToken);
          }
        }
        
        // Add Authorization header with JWT token if available
        const token = document.cookie.match(new RegExp(`(^| )${AUTH_CONFIG.tokenStorage.accessToken}=([^;]+)`))?.at(2);
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
      }
    ]
  }
});

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

// Mock orders data
const mockOrders = [
  {
    id: "1",
    orderNumber: "ORD-001",
    customerNumber: "CUST-001",
    customerName: "Acme Corp",
    deliveryDate: new Date("2024-04-10"),
    orderDate: new Date("2024-04-01"),
    isOrder: true,
    isDeliveryNote: false,
    itemsPicked: 3,
    totalItems: 5,
    pickingStatus: "in_progress",
    pickingSequence: 1,
    items: [
      {
        id: "1",
        oldArticleNumber: "A1001",
        newArticleNumber: "N2001",
        description: "Wireless Headphones",
        quantityPicked: 2,
        quantityTotal: 3,
        binLocations: ["S101", "S102"]
      },
      {
        id: "2",
        oldArticleNumber: "A1002",
        newArticleNumber: "N2002",
        description: "USB-C Cable",
        quantityPicked: 1,
        quantityTotal: 2,
        binLocations: ["S103"]
      }
    ],
    binLocations: [
      { id: "S101", name: "Shelf A1" },
      { id: "S102", name: "Shelf A2" },
      { id: "S103", name: "Shelf B1" }
    ]
  },
  {
    id: "2",
    orderNumber: "ORD-002",
    customerNumber: "CUST-002",
    customerName: "TechCo Ltd",
    deliveryDate: new Date("2024-04-12"),
    orderDate: new Date("2024-04-02"),
    isOrder: true,
    isDeliveryNote: false,
    itemsPicked: 0,
    totalItems: 3,
    pickingStatus: "pending",
    pickingSequence: 2,
    items: [
      {
        id: "3",
        oldArticleNumber: "A1003",
        newArticleNumber: "N2003",
        description: "Wireless Mouse",
        quantityPicked: 0,
        quantityTotal: 2,
        binLocations: ["S104", "S105"]
      },
      {
        id: "4",
        oldArticleNumber: "A1004",
        newArticleNumber: "N2004",
        description: "Power Bank",
        quantityPicked: 0,
        quantityTotal: 1,
        binLocations: ["S106"]
      }
    ],
    binLocations: [
      { id: "S104", name: "Shelf B2" },
      { id: "S105", name: "Shelf B3" },
      { id: "S106", name: "Shelf C1" }
    ]
  }
];

export async function fetchOrders(): Promise<Order[]> {
  try {
    // Fetch sales records and their items using the configured api client
    const response = await api.get('sales/records/').json<{results: any[]}>();
    const salesRecords = response.results;
    
    // Transform the sales records into the Order format
    const orders: Order[] = await Promise.all(salesRecords.map(async (record) => {
      // Fetch items for this sales record
      const items = await api.get(`sales/records/${record.id}/items/`).json<any[]>();
      
      // Transform items into OrderItems
      const orderItems: OrderItem[] = items.map(item => ({
        id: item.id.toString(),
        oldArticleNumber: item.product?.old_sku || item.legacy_sku || '',
        newArticleNumber: item.product?.sku || '',
        description: item.product?.name || item.description || '',
        quantityPicked: item.quantity_picked || 0,
        quantityTotal: item.quantity,
        binLocations: item.bin_locations || []
      }));

      // Get bin locations for this order
      const binLocations: BinLocation[] = await api.get(`inventory/bin-locations/by-order/${record.id}/`).json<BinLocation[]>();

      // Calculate picking progress
      const itemsPicked = orderItems.reduce((sum, item) => sum + item.quantityPicked, 0);
      const totalItems = orderItems.reduce((sum, item) => sum + item.quantityTotal, 0);

      // Determine picking status
      let pickingStatus: Order['pickingStatus'] = 'notStarted';
      if (itemsPicked === totalItems) {
        pickingStatus = 'completed';
      } else if (itemsPicked > 0) {
        pickingStatus = 'inProgress';
      }

      return {
        id: record.id.toString(),
        orderNumber: record.order_number,
        customerNumber: record.customer.customer_number,
        customerName: record.customer.name,
        deliveryDate: new Date(record.delivery_date),
        orderDate: new Date(record.created_at),
        isOrder: record.type === 'order',
        isDeliveryNote: record.type === 'delivery_note',
        itemsPicked,
        totalItems,
        pickingStatus,
        pickingSequence: record.picking_sequence || 0,
        customerAddress: record.customer.address,
        contactPerson: record.customer.contact_person,
        phoneNumber: record.customer.phone,
        email: record.customer.email,
        notes: record.notes,
        items: orderItems,
        binLocations
      };
    }));

    return orders;
  } catch (error) {
    console.error('Error fetching orders:', error);
    throw error;
  }
}

