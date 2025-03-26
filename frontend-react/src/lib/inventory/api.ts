import axios from 'axios';

// Define base URL - adjust this based on your actual API configuration
const API_BASE_URL = '/api/inventory';

// Types based on the backend models
export interface BoxType {
  id: number;
  name: string;
  description?: string;
  length?: number;
  width?: number;
  height?: number;
  weight_capacity?: number;
  slot_count: number;
  slot_naming_scheme: string;
}

export interface StorageLocation {
  id: number;
  name: string;
  location_code?: string;
}

export interface Box {
  id: number;
  code: string;
  barcode?: string;
  box_type: {
    id: number;
    name: string;
  };
  storage_location?: StorageLocation;
  status: string;
  purpose: string;
  notes?: string;
  available_slots?: number;
}

export interface BoxWithSlots extends Box {
  slots: BoxSlot[];
}

export interface BoxSlot {
  id: number;
  slot_code: string;
  occupied: boolean;
  products?: BoxProduct[];
}

export interface BoxProduct {
  product_id: number;
  product_name: string;
  quantity: number;
  batch_number?: string;
  expiry_date?: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Mock data generation for boxes
const generateMockBoxes = (count: number = 10): Box[] => {
  const boxTypes = [
    { id: 1, name: 'Karton', slot_count: 6 },
    { id: 2, name: 'Behälter', slot_count: 8 },
    { id: 3, name: 'Palette', slot_count: 4 },
    { id: 4, name: 'Gitterbox', slot_count: 12 },
  ];

  const locations = [
    { id: 1, name: 'Hauptlager A', location_code: 'HL-A' },
    { id: 2, name: 'Hauptlager B', location_code: 'HL-B' },
    { id: 3, name: 'Außenlager', location_code: 'AL' },
    { id: 4, name: 'Werkstatt', location_code: 'WS' },
  ];

  const statuses = ['AVAILABLE', 'IN_USE', 'RESERVED', 'DAMAGED', 'RETIRED'];
  const purposes = ['STORAGE', 'PICKING', 'TRANSPORT', 'WORKSHOP'];

  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    code: `BOX${String(i + 1).padStart(5, '0')}`,
    barcode: `BAR${String(i + 1).padStart(8, '0')}`,
    box_type: boxTypes[i % boxTypes.length],
    storage_location: i % 5 === 0 ? undefined : locations[i % locations.length],
    status: statuses[i % statuses.length],
    purpose: purposes[i % purposes.length],
    notes: i % 3 === 0 ? `Notes for box ${i + 1}` : '',
    available_slots: Math.floor(Math.random() * 6) + 1,
  }));
};

// Fetch all box types (mock)
export const fetchBoxTypes = async (): Promise<BoxType[]> => {
  // Return mock data
  return [
    { id: 1, name: 'Karton', description: 'Standard cardboard box', slot_count: 6, slot_naming_scheme: 'alpha-numeric' },
    { id: 2, name: 'Behälter', description: 'Plastic container', slot_count: 8, slot_naming_scheme: 'alpha-numeric' },
    { id: 3, name: 'Palette', description: 'Wooden pallet', slot_count: 4, slot_naming_scheme: 'numeric' },
    { id: 4, name: 'Gitterbox', description: 'Metal grid box', slot_count: 12, slot_naming_scheme: 'alpha-numeric' }
  ];
};

// Fetch boxes with pagination (mock)
export const fetchBoxes = async (page = 1, pageSize = 10): Promise<PaginatedResponse<Box>> => {
  // Generate mock data
  const allBoxes = generateMockBoxes(100);
  
  // Apply pagination
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const results = allBoxes.slice(start, end);
  
  return {
    results,
    total: allBoxes.length,
    page,
    page_size: pageSize,
    total_pages: Math.ceil(allBoxes.length / pageSize)
  };
};

// Fetch all storage locations (mock)
export const fetchStorageLocations = async (): Promise<StorageLocation[]> => {
  // Return mock data
  return [
    { id: 1, name: 'Hauptlager A', location_code: 'HL-A' },
    { id: 2, name: 'Hauptlager B', location_code: 'HL-B' },
    { id: 3, name: 'Außenlager', location_code: 'AL' },
    { id: 4, name: 'Werkstatt', location_code: 'WS' }
  ];
};

// Fetch products by location (mock)
export const fetchProductsByLocation = async (locationId: number): Promise<any[]> => {
  // Mock data with products for a given location
  return [
    {
      box_id: 1,
      box_code: 'BOX00001',
      slots: [
        {
          slot_id: 101,
          slot_code: 'A1',
          products: [
            {
              product_id: 1001,
              product_name: 'Schrauben M5',
              quantity: 50,
              batch_number: 'BT-2024-01',
              expiry_date: '2025-12-31'
            }
          ]
        }
      ]
    }
  ];
};

// Add a product to a box (mock)
export const addProductToBox = async (
  productId: number,
  boxSlotId: number,
  quantity: number,
  batchNumber?: string,
  expiryDate?: string
): Promise<any> => {
  // Return mock success response
  return {
    status: 'success',
    message: `Added ${quantity} of product ${productId} to box slot ${boxSlotId}`,
    data: {
      box_storage_id: Math.floor(Math.random() * 1000) + 1,
      product: {
        id: productId,
        name: 'Product ' + productId,
      },
      box_slot: {
        id: boxSlotId,
        code: 'A1',
        box_code: 'BOX00001',
      },
      quantity: quantity,
    }
  };
};

// Move a box to a different location (mock)
export const moveBox = async (boxId: number, targetLocationId: number): Promise<any> => {
  // Return mock success response
  return {
    status: 'success',
    message: 'Box moved successfully',
    data: {
      box_id: boxId,
      current_location: {
        id: targetLocationId,
        name: 'Location ' + targetLocationId,
      },
      moved_at: new Date().toISOString(),
      moved_by: 'Current User',
    },
  };
};

// Remove a product from a box (mock)
export const removeProductFromBox = async (
  boxStorageId: number,
  quantity: number,
  reason?: string
): Promise<any> => {
  // Return mock success response
  return {
    status: 'success',
    message: `Removed ${quantity} units of product from box storage ${boxStorageId}`,
    data: {
      product: {
        id: 1001,
        name: 'Product 1001',
      },
      box_slot: {
        id: 101,
        code: 'A1',
        box_code: 'BOX00001',
      },
      quantity_removed: quantity,
      remaining_quantity: 0,
    }
  };
}; 