import { instance as api } from '@/lib/api'; // Import shared ky instance
import type { Options, KyResponse } from 'ky'; // Import ky types if needed

// Types based on the backend models
export interface BoxType {
  id: number;
  name: string;
  description?: string;
  length?: number;
  width?: number;
  height?: number;
  weight_capacity?: number;  // This is actually weight_empty from the backend
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
  barcode: string;
  box_type: {
    id: number;
    name: string;
  };
  storage_location?: {
    id: number;
    name: string;
  };
  status: string;
  purpose: string;
  notes: string;
  available_slots: number;
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

// Fetch all box types using ky
export const fetchBoxTypes = async (): Promise<BoxType[]> => {
  try {
    // Use ky instance (now named 'api')
    const response = await api.get('api/v1/inventory/box-types/').json<BoxType[]>();
    return response;
  } catch (error) {
    console.error('Error fetching box types:', error);
    throw error;
  }
};

// Fetch boxes with pagination using ky
export const fetchBoxes = async (page = 1, pageSize = 20, timeout = 30000): Promise<PaginatedResponse<Box>> => {
  try {
    // Use ky instance (now named 'api') with searchParams and timeout
    const response = await api.get('api/v1/inventory/boxes/', {
      searchParams: { // Use searchParams for query parameters with ky
        page,
        page_size: pageSize
      },
      timeout
    }).json<PaginatedResponse<Box>>();
    return response;
  } catch (error) {
    console.error('Error fetching boxes:', error);
    throw error; // Consider handling potential failed refresh more explicitly if needed
  }
};

// Fetch boxes by location ID using ky
export const fetchBoxesByLocationId = async (locationId: number): Promise<Box[]> => {
  try {
    // Use ky instance (now named 'api') with searchParams
    const response = await api.get('api/v1/inventory/boxes/', {
      searchParams: {
        location_id: locationId
      }
    }).json<PaginatedResponse<Box>>(); // Assuming the endpoint still returns a paginated response structure
    return response.results || []; // Extract results
  } catch (error) {
    console.error('Error fetching boxes by location ID:', error);
    throw error;
  }
};

// Fetch all storage locations using ky
export const fetchStorageLocations = async (): Promise<StorageLocation[]> => {
  try {
    // Use ky instance (now named 'api')
    const response = await api.get('api/v1/inventory/storage-locations/').json<StorageLocation[]>();
    return response;
  } catch (error) {
    console.error('Error fetching storage locations:', error);
    throw error;
  }
};

// Fetch products by location using ky
export const fetchProductsByLocation = async (locationId: number): Promise<any[]> => {
  try {
    // Use ky instance (now named 'api')
    // Ensure the URL structure is correct for ky (no trailing slash needed usually unless required by backend)
    const response = await api.get(`api/v1/inventory/storage-locations/${locationId}/products/`).json<any[]>();
    return response;
  } catch (error) {
    console.error('Error fetching products by location:', error);
    throw error;
  }
};

// Fetch boxes (containers) by location ID using ky (redundant? same as fetchProductsByLocation URL)
// Consider renaming or removing if it fetches the same data as fetchProductsByLocation
export const fetchBoxesByLocation = async (locationId: number): Promise<any[]> => {
  try {
    // Use ky instance (now named 'api')
    const response = await api.get(`api/v1/inventory/storage-locations/${locationId}/products/`).json<any[]>();
    return response;
  } catch (error) {
    console.error('Error fetching boxes by location:', error);
    throw error;
  }
};

// Add a product to a box using ky
export const addProductToBox = async (
  productId: number,
  boxSlotId: number,
  quantity: number,
  batchNumber?: string,
  expiryDate?: string
): Promise<any> => {
  try {
    // Use ky instance (now named 'api') with json payload
    const response = await api.post('api/v1/inventory/add-product-to-box/', {
      json: { // Use json for request body with ky
        product_id: productId,
        box_slot_id: boxSlotId,
        quantity,
        batch_number: batchNumber,
        expiry_date: expiryDate
      }
    }).json<any>();
    return response;
  } catch (error) {
    console.error('Error adding product to box:', error);
    throw error;
  }
};

// Move a box to a different location using ky
export const moveBox = async (boxId: number, targetLocationId: number): Promise<any> => {
  try {
    // Use ky instance (now named 'api') with json payload
    const response = await api.post('api/v1/inventory/move-box/', {
      json: {
        box_id: boxId,
        target_location_id: targetLocationId
      }
    }).json<any>();
    return response;
  } catch (error) {
    console.error('Error moving box:', error);
    throw error;
  }
};

// Move products between box slots using ky
export const moveProductBetweenBoxes = async (
  sourceBoxStorageId: number,
  targetBoxSlotId: number,
  quantity: number
): Promise<any> => {
  try {
    // Use ky instance (now named 'api') with json payload
    const response = await api.post('api/v1/inventory/move-product-between-boxes/', {
      json: {
        source_box_storage_id: sourceBoxStorageId,
        target_box_slot_id: targetBoxSlotId,
        quantity
      }
    }).json<any>();
    return response;
  } catch (error) {
    console.error('Error moving product between boxes:', error);
    throw error;
  }
};

// Remove a product from a box using ky
export const removeProductFromBox = async (
  boxStorageId: number,
  quantity: number,
  reason?: string
): Promise<any> => {
  try {
    // Use ky instance (now named 'api') with json payload
    const response = await api.post('api/v1/inventory/remove-product-from-box/', {
      json: {
        box_storage_id: boxStorageId,
        quantity,
        reason
      }
    }).json<any>();
    return response;
  } catch (error) {
    console.error('Error removing product from box:', error);
    throw error;
  }
};

// Remove a box from its current location using ky
export const removeBoxFromLocation = async (boxId: number): Promise<any> => {
  try {
    // Use ky instance (now named 'api') with json payload
    const response = await api.post('api/v1/inventory/remove-box-from-location/', {
      json: {
        box_id: boxId
      }
    }).json<any>();
    return response;
  } catch (error) {
    console.error('Error removing box from location:', error);
    throw error;
  }
}; 