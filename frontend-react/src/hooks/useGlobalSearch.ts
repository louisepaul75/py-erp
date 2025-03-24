'use client';

import { useCallback } from 'react';

// Define types
export interface SearchResult {
  id: number;
  type: string;
  name?: string;
  customer_number?: string;
  record_number?: string;
  record_type?: string;
  customer?: string;
  sku?: string;
  legacy_sku?: string;
  barcode?: string;
  legacy_id?: string;
  box_code?: string;
  slot_code?: string;
  location_code?: string;
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
  results: {
    customers: SearchResult[];
    sales_records: SearchResult[];
    parent_products: SearchResult[];
    variant_products: SearchResult[];
    box_slots: SearchResult[];
    storage_locations: SearchResult[];
  };
}

// Completely disabled version of useGlobalSearch
export function useGlobalSearch() {
  // No state, no effects, no DOM operations
  
  // Empty callback that does nothing
  const setQuery = useCallback((newQuery: string) => {
    // Do nothing
  }, []);
  
  // Empty reset function
  const reset = useCallback(() => {
    // Do nothing
  }, []);

  // Empty results function
  const getAllResults = useCallback((): SearchResult[] => {
    return [];
  }, []);

  // Return an object with dummy values
  return {
    query: '',
    setQuery,
    results: null,
    isLoading: false,
    error: null,
    reset,
    getAllResults
  };
}
