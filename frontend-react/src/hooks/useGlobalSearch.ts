'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { API_URL } from '@/lib/config';
import { api } from '@/lib/auth/authService';

// Debug logger function with hook identification
const logDebug = (message: string, data?: any) => {
  const timestamp = new Date().toISOString();
  console.log(`[useGlobalSearch][${timestamp}] ${message}`, data || '');
};

// Error logger with hook identification
const logError = (message: string, error?: any) => {
  const timestamp = new Date().toISOString();
  console.error(`[useGlobalSearch][${timestamp}] ERROR: ${message}`, error || '');
  
  // Log stack trace if available
  if (error?.stack) {
    console.error(`[useGlobalSearch][${timestamp}] Stack:`, error.stack);
  }
};

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

export function useGlobalSearch() {
  // Generate a unique ID for this hook instance to track in logs
  const hookId = useRef(`search-hook-${Math.random().toString(36).substring(2, 9)}`);
  
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debouncedQuery, setDebouncedQuery] = useState('');
  
  // Log hook initialization
  useEffect(() => {
    logDebug(`Hook initialized. ID: ${hookId.current}`);
    
    return () => {
      logDebug(`Hook cleanup. ID: ${hookId.current}`);
    };
  }, []);

  // Debounce search query to avoid excessive API calls
  useEffect(() => {
    logDebug(`Setting up debounce timer. ID: ${hookId.current}`, { query });
    
    const timer = setTimeout(() => {
      logDebug(`Debounce timer fired. ID: ${hookId.current}`, { 
        current: query, 
        previous: debouncedQuery 
      });
      setDebouncedQuery(query);
    }, 300);

    return () => {
      logDebug(`Clearing debounce timer. ID: ${hookId.current}`);
      clearTimeout(timer);
    };
  }, [query, debouncedQuery]);

  // Fetch search results when debounced query changes
  useEffect(() => {
    // Don't start a search on empty query
    if (!debouncedQuery || !debouncedQuery.trim()) {
      logDebug(`Empty query, not fetching. ID: ${hookId.current}`);
      setResults(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    // Create a new AbortController for each request
    const controller = new AbortController();
    let isMounted = true;
    const requestId = `req-${Math.random().toString(36).substring(2, 9)}`;
    
    logDebug(`Starting fetch request. ID: ${hookId.current}, RequestID: ${requestId}`, {
      query: debouncedQuery,
      timestamp: new Date().toISOString()
    });
    
    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);

      try {
        logDebug(`Fetching search results. ID: ${hookId.current}, RequestID: ${requestId}`, {
          endpoint: `search/search/?q=${encodeURIComponent(debouncedQuery)}`
        });
        
        // Pass the AbortController signal to the fetch request
        const response = await api.get(
          `search/search/?q=${encodeURIComponent(debouncedQuery)}`,
          { signal: controller.signal }
        );
        
        logDebug(`Response received. ID: ${hookId.current}, RequestID: ${requestId}`, {
          status: response.status,
          statusText: response.statusText
        });
        
        const data = await response.json();
        
        logDebug(`Response parsed. ID: ${hookId.current}, RequestID: ${requestId}`, {
          dataType: typeof data,
          hasResults: Boolean(data && typeof data === 'object' && 'results' in data),
          responseShape: data && typeof data === 'object' ? Object.keys(data) : null
        });
        
        // Make sure component is still mounted before updating state
        if (isMounted) {
          // Type guard to validate the complete response structure
          const isSearchResponse = (obj: any): obj is SearchResponse => {
            return obj && 
              typeof obj === 'object' &&
              'query' in obj &&
              'total_count' in obj &&
              'counts' in obj &&
              'results' in obj &&
              typeof obj.counts === 'object' &&
              typeof obj.results === 'object' &&
              [
                'customers',
                'sales_records',
                'parent_products',
                'variant_products',
                'box_slots',
                'storage_locations'
              ].every(key => 
                key in obj.counts && 
                key in obj.results && 
                (obj.results[key] === null || Array.isArray(obj.results[key]))
              );
          };

          if (isSearchResponse(data)) {
            
            // Create a safe copy with proper type assertions and default values
            const safeData: SearchResponse = {
              query: String(data.query),
              total_count: Number(data.total_count),
              counts: {
                customers: Number(data.counts.customers),
                sales_records: Number(data.counts.sales_records),
                parent_products: Number(data.counts.parent_products),
                variant_products: Number(data.counts.variant_products),
                box_slots: Number(data.counts.box_slots),
                storage_locations: Number(data.counts.storage_locations),
              },
              results: {
                customers: Array.isArray(data.results.customers) ? data.results.customers.filter(Boolean) : [],
                sales_records: Array.isArray(data.results.sales_records) ? data.results.sales_records.filter(Boolean) : [],
                parent_products: Array.isArray(data.results.parent_products) ? data.results.parent_products.filter(Boolean) : [],
                variant_products: Array.isArray(data.results.variant_products) ? data.results.variant_products.filter(Boolean) : [],
                box_slots: Array.isArray(data.results.box_slots) ? data.results.box_slots.filter(Boolean) : [],
                storage_locations: Array.isArray(data.results.storage_locations) ? data.results.storage_locations.filter(Boolean) : []
              }
            };

            setResults(safeData);
          } else {
            console.error('Invalid search response structure:', data);
            setResults(null);
          }
        }
      } catch (err) {
        if (isMounted) {
          console.error('Error fetching search results:', err);
          setError(err instanceof Error ? err.message : 'An unknown error occurred');
          setResults(null);
        }
        // Ensure we don't leave any pending promises that might cause issues
        return;
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchResults();
    return () => {
      // When cleanup runs (component unmounts or effect reruns), abort any in-flight requests
      controller.abort();
      isMounted = false;
    };
  }, [debouncedQuery]);

  const reset = useCallback(() => {
    setQuery('');
    setResults(null);
    setError(null);
    setDebouncedQuery('');
  }, []);

  // Get all results flattened into a single array with proper type validation
  const getAllResults = useCallback((): SearchResult[] => {
    try {
      if (!results?.results) return [];
      
      // Helper to safely get array with type validation
      const getValidResults = (arr: any[] | null | undefined): SearchResult[] => {
        if (!Array.isArray(arr)) return [];
        return arr.filter((item): item is SearchResult => {
          if (!item || typeof item !== 'object') return false;
          
          // Required fields
          if (!('id' in item) || typeof item.id !== 'number') return false;
          if (!('type' in item) || typeof item.type !== 'string') return false;
          
          // Optional fields should be strings if present
          const stringFields = [
            'name', 'customer_number', 'record_number', 'record_type',
            'customer', 'sku', 'legacy_sku', 'barcode', 'legacy_id',
            'box_code', 'slot_code', 'location_code'
          ];
          
          return stringFields.every(field => 
            !(field in item) || 
            item[field] === null || 
            typeof item[field] === 'string'
          );
        });
      };
      
      // Safely extract and validate each result type
      const validResults = [
        ...getValidResults(results.results.customers),
        ...getValidResults(results.results.sales_records),
        ...getValidResults(results.results.parent_products),
        ...getValidResults(results.results.variant_products),
        ...getValidResults(results.results.box_slots),
        ...getValidResults(results.results.storage_locations)
      ];
      
      return validResults;
    } catch (err) {
      console.error('Error processing search results:', err);
      return [];
    }
  }, [results]);

  return {
    query,
    setQuery,
    results,
    isLoading,
    error,
    reset,
    getAllResults
  };
}
