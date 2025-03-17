import api from './api';

/**
 * Interface for BoxType data
 */
export interface BoxType {
  id: number;
  name: string;
  description: string;
  length: number | null;
  width: number | null;
  height: number | null;
  weight_capacity: number | null;
  slot_count: number;
  slot_naming_scheme: string;
}

/**
 * Interface for Box data
 */
export interface Box {
  id: number;
  code: string;
  barcode: string;
  box_type: {
    id: number;
    name: string;
  };
  storage_location: {
    id: number;
    name: string;
  } | null;
  status: string;
  purpose: string;
  notes: string;
  available_slots: number;
}

/**
 * Interface for StorageLocation data
 */
export interface StorageLocation {
  id: number;
  name: string;
  description: string;
  country: string;
  city_building: string;
  unit: string;
  compartment: string;
  shelf: string;
  sale: boolean;
  special_spot: boolean;
  is_active: boolean;
}

/**
 * Interface for Product in Storage data
 */
export interface StoredProduct {
  id: number;
  sku: string;
  name: string;
  quantity: number;
  reservation_status: string;
  batch_number: string;
  date_stored: string;
}

/**
 * Interface for BoxSlot with Products data
 */
export interface BoxSlotWithProducts {
  slot_id: number;
  slot_code: string;
  products: StoredProduct[];
}

/**
 * Interface for Box with Slots and Products data
 */
export interface BoxWithProducts {
  box_id: number;
  box_code: string;
  slots: BoxSlotWithProducts[];
}

/**
 * Interface for Product Storage Location data
 */
export interface ProductStorageLocation {
  id: number;
  name: string;
  location_code: string;
  quantity: number;
  reservation_status: string;
  country: string;
  city_building: string;
  unit: string;
  compartment: string;
  shelf: string;
}

/**
 * Inventory API service functions
 */
export const inventoryService = {
  /**
   * Get all box types
   * @returns Promise with box types data
   */
  getBoxTypes(): Promise<BoxType[]> {
    console.log('Fetching box types...');
    return api.get('/inventory/box-types/').then(response => {
      console.log('Box types response:', response.data);
      return response.data;
    });
  },

  /**
   * Get a specific box type by ID
   * @param id Box type ID
   * @returns Promise with box type data
   */
  getBoxType(id: number): Promise<BoxType> {
    console.log(`Fetching box type ${id}...`);
    return api.get(`/inventory/box-types/${id}/`).then(response => {
      console.log('Box type response:', response.data);
      return response.data;
    });
  },

  /**
   * Get all boxes
   * @returns Promise with boxes data
   */
  getBoxes(page = 1, pageSize = 10): Promise<{ results: Box[], total: number, page: number, page_size: number, total_pages: number }> {
    console.log('Fetching boxes...');
    return api.get('/inventory/boxes/', {
      params: {
        page,
        page_size: pageSize
      }
    }).then(response => {
      console.log('Boxes response:', response.data);
      return response.data;
    }).catch(error => {
      console.error('Error fetching boxes:', error);
      throw error;
    });
  },

  /**
   * Get all storage locations
   * @returns Promise with storage locations data
   */
  getStorageLocations(): Promise<StorageLocation[]> {
    console.log('Fetching storage locations...');
    return api.get('/inventory/storage-locations/').then(response => {
      console.log('Storage locations response:', response.data);
      return response.data;
    });
  },

  /**
   * Get a specific storage location by ID
   * @param id Storage location ID
   * @returns Promise with storage location data
   */
  getStorageLocation(id: number): Promise<StorageLocation> {
    console.log(`Fetching storage location ${id}...`);
    return api.get(`/inventory/storage-locations/${id}/`).then(response => {
      console.log('Storage location response:', response.data);
      return response.data;
    });
  },

  /**
   * Get products by storage location
   * @param locationId Storage location ID
   * @returns Promise with products data grouped by box and slot
   */
  getProductsByLocation(locationId: number): Promise<BoxWithProducts[]> {
    console.log(`Fetching products for location ${locationId}...`);
    return api.get(`/inventory/storage-locations/${locationId}/products/`).then(response => {
      console.log('Raw products by location response:', response);
      console.log('Products by location response data:', response.data);
      if (!Array.isArray(response.data)) {
        console.warn('API response is not an array:', response.data);
      }
      return response.data;
    }).catch(error => {
      console.error('Error in getProductsByLocation:', error);
      console.error('Error response:', error.response);
      throw error;
    });
  },

  /**
   * Get storage locations for a specific product
   * @param productId Product ID
   * @returns Promise with storage locations data for the product
   */
  getLocationsByProduct(productId: number): Promise<ProductStorageLocation[]> {
    console.log(`Fetching storage locations for product ${productId}...`);
    return api.get(`/inventory/products/${productId}/locations/`).then(response => {
      console.log('Storage locations for product response:', response.data);
      return response.data;
    }).catch(error => {
      console.error('Error in getLocationsByProduct:', error);
      console.error('Error response:', error.response);
      throw error;
    });
  }
};

// Re-export for backward compatibility
export default inventoryService; 