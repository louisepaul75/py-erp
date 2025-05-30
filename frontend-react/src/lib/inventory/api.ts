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
    const response = await api.get('inventory/box-types/').json<BoxType[]>();
    return response;
  } catch (error) {
    console.error('Error fetching box types:', error);
    throw error;
  }
};

// Fetch boxes with pagination using ky
export const fetchBoxes = async (page = 1, pageSize = 20, timeout = 30000): Promise<PaginatedResponse<Box>> => {
  try {
    console.log(`[DEBUG] Starting fetchBoxes API call: page=${page}, pageSize=${pageSize}`);
    
    // Use ky instance (now named 'api') with searchParams and timeout
    const response = await api.get('inventory/boxes/', {
      searchParams: { // Use searchParams for query parameters with ky
        page,
        page_size: pageSize
      },
      timeout
    });
    
    // Log the raw response before parsing JSON
    console.log('[DEBUG] API Response Status:', response.status);
    console.log('[DEBUG] API Response Headers:', Object.fromEntries(response.headers.entries()));
    
    // Clone the response to avoid consuming it twice
    const responseClone = response.clone();
    
    // Get the response text for debugging
    const responseText = await responseClone.text();
    console.log('[DEBUG] API Response Text:', responseText);
    
    // Try to parse as JSON
    let jsonData;
    try {
      jsonData = JSON.parse(responseText);
      console.log('[DEBUG] Parsed JSON Response:', jsonData);
    } catch (parseError) {
      console.error('[DEBUG] Error parsing JSON:', parseError);
    }
    
    // Get the actual data using ky's json method
    const data = await response.json<PaginatedResponse<Box>>();
    console.log('[DEBUG] API Final Response Data:', data);
    console.log('[DEBUG] Results Count:', data.results ? data.results.length : 0);
    
    return data;
  } catch (error) {
    console.error('[DEBUG] Error fetching boxes:', error);
    if (error.response) {
      console.error('[DEBUG] Error response status:', error.response.status);
      try {
        const errorText = await error.response.text();
        console.error('[DEBUG] Error response text:', errorText);
      } catch (textError) {
        console.error('[DEBUG] Could not read error response text');
      }
    }
    throw error;
  }
};

// Fetch boxes by location ID using ky
export const fetchBoxesByLocationId = async (locationId: number): Promise<Box[]> => {
  try {
    // Use ky instance (now named 'api') with searchParams
    const response = await api.get('inventory/boxes/', {
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

// Fetch all storage locations from the API
export const fetchStorageLocations = async (): Promise<StorageLocation[]> => {
  try {
    const response = await api.get('inventory/storage-locations/').json<StorageLocation[]>();
    return response;
  } catch (error) {
    console.error('Error fetching storage locations:', error);
    throw error;
  }
};

// Fetch products by location using ky
export const fetchProductsByLocation = async (locationId: number): Promise<any[]> => {
  try {
    const response = await api.get(`inventory/storage-locations/${locationId}/products/`).json<any[]>();
    return response;
  } catch (error) {
    console.error(`Error fetching products for location ${locationId}:`, error);
    throw error;
  }
};

// Fetch boxes (containers) by location ID using ky (redundant? same as fetchProductsByLocation URL)
// Consider renaming or removing if it fetches the same data as fetchProductsByLocation
export const fetchBoxesByLocation = async (locationId: number): Promise<any[]> => {
  try {
    const response = await api.get(`inventory/storage-locations/${locationId}/products/`).json<any[]>();
    return response;
  } catch (error) {
    console.error(`Error fetching boxes for location ${locationId}:`, error);
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
    const response = await api.post('inventory/add-product-to-box/', {
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
    const response = await api.post('inventory/move-box/', {
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
    const response = await api.post('inventory/move-product-between-boxes/', {
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
    const response = await api.post('inventory/remove-product-from-box/', {
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
    const response = await api.post('inventory/remove-box-from-location/', {
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

// Fetch boxes that contain a specific product from the API
export const fetchBoxesByProduct = async (productId: number): Promise<Box[]> => {
  try {
    const response = await api.get('inventory/boxes/', {
      searchParams: { product_id: productId }
    }).json<Box[]>();
    return response;
  } catch (error) {
    console.error(`Error fetching boxes for product ${productId}:`, error);
    throw error;
  }
};