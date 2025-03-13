import { defineStore } from 'pinia';
import inventoryService, { BoxType, Box, StorageLocation } from '@/services/inventory';

interface InventoryState {
  boxTypes: BoxType[];
  boxes: Box[];
  storageLocations: StorageLocation[];
  loading: {
    boxTypes: boolean;
    boxes: boolean;
    storageLocations: boolean;
  };
  error: {
    boxTypes: string | null;
    boxes: string | null;
    storageLocations: string | null;
  };
}

export const useInventoryStore = defineStore('inventory', {
  state: (): InventoryState => ({
    boxTypes: [],
    boxes: [],
    storageLocations: [],
    loading: {
      boxTypes: false,
      boxes: false,
      storageLocations: false
    },
    error: {
      boxTypes: null,
      boxes: null,
      storageLocations: null
    }
  }),
  
  getters: {
    getBoxTypes: (state) => state.boxTypes,
    getBoxes: (state) => state.boxes,
    getStorageLocations: (state) => state.storageLocations,
    isBoxTypesLoading: (state) => state.loading.boxTypes,
    isBoxesLoading: (state) => state.loading.boxes,
    isStorageLocationsLoading: (state) => state.loading.storageLocations,
    getBoxTypesError: (state) => state.error.boxTypes,
    getBoxesError: (state) => state.error.boxes,
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

    async fetchBoxes() {
      this.loading.boxes = true;
      this.error.boxes = null;
      
      try {
        const boxes = await inventoryService.getBoxes();
        this.boxes = boxes;
      } catch (error) {
        console.error('Error fetching boxes:', error);
        this.error.boxes = error instanceof Error ? error.message : 'Failed to fetch boxes';
      } finally {
        this.loading.boxes = false;
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