'use client';

import { useState, useEffect, useCallback } from 'react';
import { API_URL } from '@/lib/config';
import { api } from '@/lib/auth/authService';

export interface SearchResult {
  id: number;
  type: string;
  [key: string]: any;
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
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // Debounce search query to avoid excessive API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Fetch search results when debounced query changes
  useEffect(() => {
    if (!debouncedQuery || !debouncedQuery.trim()) {
      setResults(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await api.get(`search/search/?q=${encodeURIComponent(debouncedQuery)}`).json();
        if (isMounted && data) {
          setResults(data as SearchResponse);
        } else if (isMounted) {
          setResults(null);
        }
      } catch (err) {
        if (isMounted) {
          console.error('Error fetching search results:', err);
          setError(err instanceof Error ? err.message : 'An unknown error occurred');
          setResults(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchResults();
    return () => {
      isMounted = false;
    };
  }, [debouncedQuery]);

  const reset = useCallback(() => {
    setQuery('');
    setResults(null);
    setError(null);
    setDebouncedQuery('');
  }, []);

  // Get all results flattened into a single array
  const getAllResults = useCallback((): SearchResult[] => {
    try {
      if (!results || !results.results) return [];
      
      // Ensure all collections exist and are arrays before spreading
      const customers = Array.isArray(results.results.customers) ? results.results.customers : [];
      const salesRecords = Array.isArray(results.results.sales_records) ? results.results.sales_records : [];
      const parentProducts = Array.isArray(results.results.parent_products) ? results.results.parent_products : [];
      const variantProducts = Array.isArray(results.results.variant_products) ? results.results.variant_products : [];
      const boxSlots = Array.isArray(results.results.box_slots) ? results.results.box_slots : [];
      const storageLocations = Array.isArray(results.results.storage_locations) ? results.results.storage_locations : [];
      
      // Combine all arrays and filter out null/undefined values
      return [
        ...customers,
        ...salesRecords,
        ...parentProducts,
        ...variantProducts,
        ...boxSlots,
        ...storageLocations
      ].filter(result => result != null);
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