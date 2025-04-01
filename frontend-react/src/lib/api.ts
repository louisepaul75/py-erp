import type { Order, OrderItem, BinLocation } from "@/types/types"
import ky, { HTTPError, Options, KyResponse } from 'ky';
import { API_URL, AUTH_CONFIG } from './config';
import { csrfService } from './auth/authService';
import { cookies } from 'next/headers';
import { clientCookieStorage } from './auth/clientCookies';

// Create an API client instance with the correct base URL and auth
// Export the instance so it can be used in other modules
export const instance = ky.create({
  prefixUrl: API_URL,
  timeout: 30000,
  credentials: 'include', // Include cookies in requests
  hooks: {
    beforeRequest: [
      async (request) => {
        // Get token from client cookie storage
        const token = typeof window !== 'undefined' 
          ? clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken)
          : null;
        
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
        
        // Add CSRF token if available and if method requires it (e.g., POST, PUT, PATCH, DELETE)
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method.toUpperCase())) {
           // Use getToken as suggested by linter
          const csrfToken = await csrfService.getToken(); 
          if (csrfToken) {
             request.headers.set('X-CSRFToken', csrfToken);
          }
        }
      }
    ],
    beforeError: [
      async (error: HTTPError): Promise<HTTPError> => {
        const { response } = error;
        
        // Handle 401 Unauthorized errors (token expired)
        if (response?.status === 401) {
          try {
            const refreshToken = clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
            if (refreshToken) {
              console.log("Attempting token refresh...");
              const refreshResponse = await ky.post(`${API_URL}/token/refresh/`, {
                json: { refresh: refreshToken },
                credentials: 'include',
                throwHttpErrors: false 
              }).json<{ access?: string }>();
              
              if (refreshResponse?.access) {
                  console.log("Token refreshed successfully.");
                  clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, refreshResponse.access);
              } else {
                  console.error("Token refresh failed: No access token in response.");
                  clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.accessToken);
                  clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.refreshToken);
              }
            } else {
                console.log("No refresh token found, cannot refresh.");
            }
          } catch (refreshError) {
            console.error('Token refresh attempt failed:', refreshError);
            clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.accessToken);
            clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.refreshToken);
          }
        }
        return error; 
      }
    ]
  }
});

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
    const targetUrl = 'v1/sales/records/';
    console.log(`[api.ts] Attempting to fetch: ${API_URL}/${targetUrl}`); // Log the intended URL using API_URL
    const response = await instance.get(targetUrl).json<{results: any[]}>();
    const salesRecords = response.results;
    
    const orders: Order[] = await Promise.all(salesRecords.map(async (record) => {
      const itemsResponse = await instance.get(`v1/sales/records/${record.id}/items/`).json<{results: any[]}>();
      const items = itemsResponse.results;
      
      const orderItems: OrderItem[] = items.map(item => ({
        id: item.id.toString(),
        oldArticleNumber: item.product?.old_sku || item.legacy_sku || '',
        newArticleNumber: item.product?.sku || '',
        description: item.product?.name || item.description || '',
        quantityPicked: item.quantity_picked || 0,
        quantityTotal: item.quantity,
        binLocations: item.product?.bin_locations?.map((loc: any) => loc.name) || [] 
      }));

      const binLocationsResponse = await instance.get(`v1/inventory/bin-locations/by-order/${record.id}/`).json<{results: BinLocation[]}>();
      const binLocations = binLocationsResponse.results;

      const itemsPicked = orderItems.reduce((sum, item) => sum + item.quantityPicked, 0);
      const totalItems = orderItems.reduce((sum, item) => sum + item.quantityTotal, 0);

      let pickingStatus: Order['pickingStatus'] = 'notStarted';
      if (totalItems === 0) {
         pickingStatus = 'completed'; 
      } else if (itemsPicked === totalItems) {
        pickingStatus = 'completed';
      } else if (itemsPicked > 0) {
        pickingStatus = 'inProgress';
      }

      return {
        id: record.id.toString(),
        orderNumber: record.order_number,
        customerNumber: record.customer?.customer_number || 'N/A',
        customerName: record.customer?.name || 'N/A',
        deliveryDate: record.delivery_date ? new Date(record.delivery_date) : new Date(),
        orderDate: record.created_at ? new Date(record.created_at) : new Date(),
        isOrder: record.type === 'order',
        isDeliveryNote: record.type === 'delivery_note',
        itemsPicked,
        totalItems,
        pickingStatus,
        pickingSequence: record.picking_sequence || 0,
        customerAddress: record.customer?.address || 'N/A',
        contactPerson: record.customer?.contact_person || 'N/A',
        phoneNumber: record.customer?.phone || 'N/A',
        email: record.customer?.email || 'N/A',
        notes: record.notes || '',
        items: orderItems,
        binLocations
      };
    }));

    return orders;
  } catch (error) {
    console.error('Error fetching orders:', error);
    if (error instanceof HTTPError) {
        console.error('Status:', error.response.status);
        console.error('Body:', await error.response.text());
    }
    throw error;
  }
}

