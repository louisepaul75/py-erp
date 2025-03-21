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
    if (!debouncedQuery.trim()) {
      setResults(null);
      return;
    }

    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await api.get(`search/search/?q=${encodeURIComponent(debouncedQuery)}`).json();
        setResults(data);
      } catch (err) {
        console.error('Error fetching search results:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [debouncedQuery]);

  const reset = useCallback(() => {
    setQuery('');
    setResults(null);
    setError(null);
  }, []);

  // Get all results flattened into a single array
  const getAllResults = useCallback((): SearchResult[] => {
    if (!results) return [];
    
    return [
      ...results.results.customers,
      ...results.results.sales_records,
      ...results.results.parent_products,
      ...results.results.variant_products,
      ...results.results.box_slots,
      ...results.results.storage_locations
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