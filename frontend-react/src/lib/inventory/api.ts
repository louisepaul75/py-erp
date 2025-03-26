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

// Create axios instance with auth interceptor
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // Increased timeout to 30 seconds
  withCredentials: true, // Include cookies
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Timeout error message helper
const getTimeoutMessage = (ms: number) => {
  return `Die Anfrage hat das Zeitlimit von ${ms/1000} Sekunden überschritten. Bitte überprüfen Sie Ihre Netzwerkverbindung und versuchen Sie es später erneut.`;
};

// Add request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Initialize retry count
    config.retryCount = config.retryCount || 0;
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh and retries
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle timeout errors with retry logic
    if ((error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'))) 
        && originalRequest?.retryCount < MAX_RETRIES) {
      originalRequest.retryCount = (originalRequest.retryCount || 0) + 1;
      console.log(`Retrying request (${originalRequest.retryCount}/${MAX_RETRIES})...`);
      
      // Wait before retrying
      await sleep(RETRY_DELAY * originalRequest.retryCount);
      return api(originalRequest);
    }

    // If we've exhausted retries or it's not a timeout error
    if (error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'))) {
      console.error('Request timeout after retries:', error);
      return Promise.reject(new Error(getTimeoutMessage(originalRequest?.timeout || 30000)));
    }

    // Check if error has response and status is 401 and we haven't tried to refresh token yet
    if (error.response?.status === 401 && !originalRequest?._retry) {
      // Mark the request as retried to prevent infinite loops
      if (originalRequest) {
        originalRequest._retry = true;
      }

      try {
        // Try to refresh the token
        const newToken = await authService.refreshToken();
        if (newToken && originalRequest) {
          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, redirect to login
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // For network errors or other issues where response might not exist
    if (!error.response) {
      console.error('Network error or server not responding:', error.message);
      if (navigator.onLine) {
        return Promise.reject(new Error('Server ist nicht erreichbar. Bitte versuchen Sie es später erneut.'));
      } else {
        return Promise.reject(new Error('Keine Internetverbindung. Bitte überprüfen Sie Ihre Netzwerkverbindung.'));
      }
    }

    // For server errors
    if (error.response?.status >= 500) {
      return Promise.reject(new Error('Der Server hat einen internen Fehler gemeldet. Bitte versuchen Sie es später erneut.'));
    }

    return Promise.reject(error);
  }
);

// Fetch all box types
export const fetchBoxTypes = async (): Promise<BoxType[]> => {
  try {
    const response = await api.get('/inventory/box-types/');
    return response.data;
  } catch (error) {
    console.error('Error fetching box types:', error);
    throw error;
  }
};

// Fetch boxes with pagination and configurable timeout
export const fetchBoxes = async (page = 1, pageSize = 20, timeout = 30000): Promise<PaginatedResponse<Box>> => {
  try {
    const response = await api.get('/inventory/boxes/', {
      params: {
        page,
        page_size: pageSize
      },
      timeout // Allow custom timeout for this specific request
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
    const response = await api.get('/inventory/storage-locations/');
    return response.data;
  } catch (error) {
    console.error('Error fetching storage locations:', error);
    throw error;
  }
};

// Fetch products by location
export const fetchProductsByLocation = async (locationId: number): Promise<any[]> => {
  try {
    const response = await api.get(`/inventory/products-by-location/${locationId}/`);
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
    const response = await api.post('/inventory/add-product-to-box/', {
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
    const response = await api.post('/inventory/move-box/', {
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
    const response = await api.post('/inventory/move-product-between-boxes/', {
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
    const response = await api.post('/inventory/remove-product-from-box/', {
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