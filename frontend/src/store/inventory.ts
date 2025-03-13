import { defineStore } from 'pinia';
import inventoryService, { BoxType, Box, StorageLocation } from '@/services/inventory';

interface InventoryState {
  boxTypes: BoxType[];
  boxes: Box[];
  boxesPagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
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
    boxesPagination: {
      total: 0,
      page: 1,
      pageSize: 10,
      totalPages: 0
    },
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
    getBoxesPagination: (state) => state.boxesPagination,
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
        console.log('Fetching box types from store...');
        const boxTypes = await inventoryService.getBoxTypes();
        this.boxTypes = boxTypes;
        console.log('Box types fetched successfully:', boxTypes);
      } catch (error) {
        console.error('Error fetching box types:', error);
        this.error.boxTypes = error instanceof Error ? error.message : 'Failed to fetch box types';
      } finally {
        this.loading.boxTypes = false;
      }
    },

    async fetchBoxes(page?: number, pageSize?: number) {
      this.loading.boxes = true;
      this.error.boxes = null;
      
      try {
        console.log('Fetching boxes from store...');
        const response = await inventoryService.getBoxes(
          page || this.boxesPagination.page,
          pageSize || this.boxesPagination.pageSize
        );
        this.boxes = response.results;
        this.boxesPagination = {
          total: response.total,
          page: response.page,
          pageSize: response.page_size,
          totalPages: response.total_pages
        };
        console.log('Boxes fetched successfully:', response);
      } catch (error) {
        console.error('Error fetching boxes:', error);
        if (error instanceof Error) {
          this.error.boxes = error.message;
        } else if (error && typeof error === 'object' && 'response' in error) {
          const axiosError = error as any;
          this.error.boxes = axiosError.response?.data?.detail || axiosError.message || 'Failed to fetch boxes';
        } else {
          this.error.boxes = 'Failed to fetch boxes';
        }
      } finally {
        this.loading.boxes = false;
      }
    },
    
    async fetchStorageLocations() {
      this.loading.storageLocations = true;
      this.error.storageLocations = null;
      
      try {
        console.log('Fetching storage locations from store...');
        const locations = await inventoryService.getStorageLocations();
        this.storageLocations = locations;
        console.log('Storage locations fetched successfully:', locations);
      } catch (error) {
        console.error('Error fetching storage locations:', error);
        this.error.storageLocations = error instanceof Error ? error.message : 'Failed to fetch storage locations';
      } finally {
        this.loading.storageLocations = false;
      }
    }
  }
}); 