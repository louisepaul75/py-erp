import axios, { InternalAxiosRequestConfig } from 'axios';
import { API_URL } from '../config';
import { authService } from '../auth/authService';

// Extend AxiosRequestConfig to include retryCount
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    retryCount?: number;
  }
}

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

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  withCredentials: true // Include cookies in requests
});

// Add request interceptor to handle auth
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      // Get the token
      const token = await authService.getToken();
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      } else {
        // If no token and not a login request, redirect to login
        if (!config.url?.includes('token')) {
          window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
          throw new Error('No authentication token available');
        }
      }
      
      return config;
    } catch (error) {
      return Promise.reject(error);
    }
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If the error is 401 and we haven't tried to refresh the token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh the token
        const refreshSuccess = await authService.refreshToken();
        
        if (refreshSuccess) {
          // Get the new token
          const token = await authService.getToken();
          
          if (token) {
            // Update the authorization header
            originalRequest.headers.Authorization = `Bearer ${token}`;
            // Retry the original request
            return api(originalRequest);
          }
        }
        
        // If refresh failed, redirect to login
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        return Promise.reject(error);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Fetch all box types
export const fetchBoxTypes = async (): Promise<BoxType[]> => {
  try {
    const response = await api.get('/api/inventory/box-types/');
    return response.data;
  } catch (error) {
    console.error('Error fetching box types:', error);
    throw error;
  }
};

// Fetch boxes with pagination and configurable timeout
export const fetchBoxes = async (page = 1, pageSize = 20, timeout = 30000): Promise<PaginatedResponse<Box>> => {
  try {
    const response = await api.get('/api/v1/inventory/boxes/', {
      params: {
        page,
        page_size: pageSize
      },
      timeout
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching boxes:', error);
    throw error;
  }
};

// Fetch all storage locations
export const fetchStorageLocations = async (): Promise<StorageLocation[]> => {
  try {
    const response = await api.get('/api/inventory/storage-locations/');
    return response.data;
  } catch (error) {
    console.error('Error fetching storage locations:', error);
    throw error;
  }
};

// Fetch products by location
export const fetchProductsByLocation = async (locationId: number): Promise<any[]> => {
  try {
    const response = await api.get(`/api/inventory/products-by-location/${locationId}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching products by location:', error);
    throw error;
  }
};

// Add a product to a box
export const addProductToBox = async (
  productId: number,
  boxSlotId: number,
  quantity: number,
  batchNumber?: string,
  expiryDate?: string
): Promise<any> => {
  try {
    const response = await api.post('/api/inventory/add-product-to-box/', {
      product_id: productId,
      box_slot_id: boxSlotId,
      quantity,
      batch_number: batchNumber,
      expiry_date: expiryDate
    });
    return response.data;
  } catch (error) {
    console.error('Error adding product to box:', error);
    throw error;
  }
};

// Move a box to a different location
export const moveBox = async (boxId: number, targetLocationId: number): Promise<any> => {
  try {
    const response = await api.post('/api/inventory/move-box/', {
      box_id: boxId,
      target_location_id: targetLocationId
    });
    return response.data;
  } catch (error) {
    console.error('Error moving box:', error);
    throw error;
  }
};

// Move products between box slots
export const moveProductBetweenBoxes = async (
  sourceBoxStorageId: number,
  targetBoxSlotId: number,
  quantity: number
): Promise<any> => {
  try {
    const response = await api.post('/api/inventory/move-product-between-boxes/', {
      source_box_storage_id: sourceBoxStorageId,
      target_box_slot_id: targetBoxSlotId,
      quantity
    });
    return response.data;
  } catch (error) {
    console.error('Error moving product between boxes:', error);
    throw error;
  }
};

// Remove a product from a box
export const removeProductFromBox = async (
  boxStorageId: number,
  quantity: number,
  reason?: string
): Promise<any> => {
  try {
    const response = await api.post('/api/inventory/remove-product-from-box/', {
      box_storage_id: boxStorageId,
      quantity,
      reason
    });
    return response.data;
  } catch (error) {
    console.error('Error removing product from box:', error);
    throw error;
  }
}; 