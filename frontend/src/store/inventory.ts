import { defineStore } from 'pinia';
import inventoryService, { BoxType, StorageLocation } from '@/services/inventory';

interface InventoryState {
  boxTypes: BoxType[];
  storageLocations: StorageLocation[];
  loading: {
    boxTypes: boolean;
    storageLocations: boolean;
  };
  error: {
    boxTypes: string | null;
    storageLocations: string | null;
  };
}

export const useInventoryStore = defineStore('inventory', {
  state: (): InventoryState => ({
    boxTypes: [],
    storageLocations: [],
    loading: {
      boxTypes: false,
      storageLocations: false
    },
    error: {
      boxTypes: null,
      storageLocations: null
    }
  }),
  
  getters: {
    getBoxTypes: (state) => state.boxTypes,
    getStorageLocations: (state) => state.storageLocations,
    isBoxTypesLoading: (state) => state.loading.boxTypes,
    isStorageLocationsLoading: (state) => state.loading.storageLocations,
    getBoxTypesError: (state) => state.error.boxTypes,
    getStorageLocationsError: (state) => state.error.storageLocations
  },
  
  actions: {
    async fetchBoxTypes() {
      this.loading.boxTypes = true;
      this.error.boxTypes = null;
      
      try {
        const boxTypes = await inventoryService.getBoxTypes();
        this.boxTypes = boxTypes;
      } catch (error) {
        console.error('Error fetching box types:', error);
        this.error.boxTypes = error instanceof Error ? error.message : 'Failed to fetch box types';
      } finally {
        this.loading.boxTypes = false;
      }
    },
    
    async fetchStorageLocations() {
      this.loading.storageLocations = true;
      this.error.storageLocations = null;
      
      try {
        const locations = await inventoryService.getStorageLocations();
        this.storageLocations = locations;
      } catch (error) {
        console.error('Error fetching storage locations:', error);
        this.error.storageLocations = error instanceof Error ? error.message : 'Failed to fetch storage locations';
      } finally {
        this.loading.storageLocations = false;
      }
    }
  }
}); 