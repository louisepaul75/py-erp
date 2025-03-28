'use client';

import { useCallback, useState, useEffect } from 'react';
import { api } from '@/lib/auth/authService';

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

export function useGlobalSearch() {
  const [query, setQueryState] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!query) {
        setResults(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await api.get(`search/search/?q=${query}`);
        const data = await response.json();
        setResults(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'API error');
        setResults(null);
      } finally {
        setIsLoading(false);
      }
    };

    // Debounce the search
    const timeoutId = setTimeout(fetchResults, 300);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [query]);

  const setQuery = useCallback((newQuery: string) => {
    setQueryState(newQuery);
  }, []);

  const reset = useCallback(() => {
    setQueryState('');
    setResults(null);
    setError(null);
  }, []);

  const getAllResults = useCallback((): SearchResult[] => {
    if (!results) return [];

    return [
      ...results.results.customers,
      ...results.results.sales_records,
      ...results.results.parent_products,
      ...results.results.variant_products,
      ...results.results.box_slots,
      ...results.results.storage_locations,
    ];
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
