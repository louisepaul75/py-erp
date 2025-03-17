import api from './api';
import { i18n } from '@/i18n';

export interface SearchResult {
  id: number;
  type: string;
  [key: string]: any;
}

export interface SearchResultsGroup {
  customers: SearchResult[];
  sales_records: SearchResult[];
  parent_products: SearchResult[];
  variant_products: SearchResult[];
  box_slots: SearchResult[];
  storage_locations: SearchResult[];
}

export interface SearchResponse {
  query: string;
  total_count: number;
  counts: {
    customers: number;
    sales_records: number;
    parent_products: number;
    variant_products: number;
    box_slots: number;
    storage_locations: number;
  };
  results: SearchResultsGroup;
}

/**
 * Search service that provides methods for searching across different entity types
 */
const searchService = {
  /**
   * Perform a global search across all entity types
   * @param query The search query
   * @returns Promise with the search results
   */
  globalSearch: async (query: string): Promise<SearchResponse> => {
    try {
      const response = await api.get('/search/search/', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      console.error('Global search failed:', error);
      throw error;
    }
  },

  /**
   * Get the route for a specific search result based on its type
   * @param result The search result
   * @returns The route object for the result
   */
  getRouteForResult: (result: SearchResult) => {
    switch (result.type) {
      case 'customer':
        return { name: 'CustomerDetail', params: { id: result.id } };
      case 'sales_record':
        return { name: 'SalesRecordDetail', params: { id: result.id } };
      case 'parent_product':
      case 'variant_product':
        return { name: 'ProductDetail', params: { id: result.id } };
      case 'box_slot':
        return { name: 'BoxSlotDetail', params: { id: result.id } };
      case 'storage_location':
        return { name: 'StorageLocationDetail', params: { id: result.id } };
      default:
        return { name: 'Dashboard' };
    }
  },

  /**
   * Get a display icon for a search result based on its type
   * @param result The search result
   * @returns The icon name
   */
  getIconForResult: (result: SearchResult): string => {
    switch (result.type) {
      case 'customer':
        return 'mdi-account';
      case 'sales_record':
        return 'mdi-file-document';
      case 'parent_product':
      case 'variant_product':
        return 'mdi-package-variant';
      case 'box_slot':
        return 'mdi-package';
      case 'storage_location':
        return 'mdi-map-marker';
      default:
        return 'mdi-help-circle';
    }
  },

  /**
   * Get a display label for a search result category
   * @param category The category key
   * @returns The translated label
   */
  getCategoryLabel: (category: string): string => {
    // Use i18n to translate category names
    return i18n.global.t(`search.categories.${category}`, category);
  },

  /**
   * Get a primary display text for a search result
   * @param result The search result
   * @returns The primary display text
   */
  getPrimaryText: (result: SearchResult): string => {
    switch (result.type) {
      case 'customer':
        return `${result.name} (${result.customer_number})`;
      case 'sales_record':
        return `${result.record_type} #${result.record_number}`;
      case 'parent_product':
      case 'variant_product':
        return `${result.name} (${result.sku})`;
      case 'box_slot':
        return `${result.box_code}.${result.slot_code} - ${result.barcode}`;
      case 'storage_location':
        return result.name || result.location_code || result.legacy_id;
      default:
        return 'Unknown result';
    }
  },

  /**
   * Get secondary display text for a search result
   * @param result The search result
   * @returns The secondary display text
   */
  getSecondaryText: (result: SearchResult): string => {
    switch (result.type) {
      case 'customer':
        return 'Customer';
      case 'sales_record':
        return result.customer ? `Customer: ${result.customer}` : 'Sales Record';
      case 'parent_product':
        return 'Parent Product';
      case 'variant_product':
        return result.legacy_sku ? `Legacy SKU: ${result.legacy_sku}` : 'Variant Product';
      case 'box_slot':
        return 'Box Slot';
      case 'storage_location':
        return 'Storage Location';
      default:
        return '';
    }
  }
};

export default searchService; 