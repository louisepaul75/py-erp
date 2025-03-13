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
 * Interface for StorageLocation data
 */
export interface StorageLocation {
  id: number;
  name: string;
  country: string;
  city_building: string;
  unit: number | null;
  compartment: number | null;
  shelf: number | null;
  location_code: string;
  is_active: boolean;
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
    return api.get('/inventory/box-types/').then(response => response.data);
  },

  /**
   * Get a specific box type by ID
   * @param id Box type ID
   * @returns Promise with box type data
   */
  getBoxType(id: number): Promise<BoxType> {
    return api.get(`/inventory/box-types/${id}/`).then(response => response.data);
  },

  /**
   * Get all storage locations
   * @returns Promise with storage locations data
   */
  getStorageLocations(): Promise<StorageLocation[]> {
    return api.get('/inventory/storage-locations/').then(response => response.data);
  },

  /**
   * Get a specific storage location by ID
   * @param id Storage location ID
   * @returns Promise with storage location data
   */
  getStorageLocation(id: number): Promise<StorageLocation> {
    return api.get(`/inventory/storage-locations/${id}/`).then(response => response.data);
  }
};

// Re-export for backward compatibility
export default inventoryService; 