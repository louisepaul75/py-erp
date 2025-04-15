import { useState, useMemo, useCallback } from 'react';

type SortDirection = 'asc' | 'desc';

interface SortConfig<T> {
  key: keyof T | null;
  direction: SortDirection;
}

// Configuration for the hook
interface UseDataTableProps<T> {
  initialData: T[];
  initialSortKey?: keyof T | null;
  initialSortDirection?: SortDirection;
  searchableFields?: (keyof T)[]; // Fields to search within
}

// Return type of the hook
interface UseDataTableReturn<T> {
  processedData: T[];       // Data after filtering and sorting
  sortConfig: SortConfig<T>;
  requestSort: (key: keyof T) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
}

export function useDataTable<T>({
  initialData,
  initialSortKey = null,
  initialSortDirection = 'asc',
  searchableFields = [], // Default to no searchable fields if not provided
}: UseDataTableProps<T>): UseDataTableReturn<T> {
  const [sortConfig, setSortConfig] = useState<SortConfig<T>>({
    key: initialSortKey,
    direction: initialSortDirection,
  });
  const [searchTerm, setSearchTerm] = useState('');

  const processedData = useMemo(() => {
    let items = [...initialData];

    // 1. Filtering (if searchTerm and searchableFields are provided)
    if (searchTerm && searchableFields.length > 0) {
      const lowerCaseSearchTerm = searchTerm.toLowerCase();
      items = items.filter(item => {
        return searchableFields.some(field => {
          const value = item[field];
          // Basic check: convert value to string and check if it includes the search term
          return value !== null && value !== undefined &&
                 String(value).toLowerCase().includes(lowerCaseSearchTerm);
        });
      });
    }

    // 2. Sorting
    if (sortConfig.key !== null) {
      items.sort((a, b) => {
        const aValue = a[sortConfig.key!];
        const bValue = b[sortConfig.key!];

        // Handle null/undefined values
        if (aValue === null || aValue === undefined) return sortConfig.direction === 'asc' ? -1 : 1;
        if (bValue === null || bValue === undefined) return sortConfig.direction === 'asc' ? 1 : -1;

        // Handle string comparison
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          return aValue.localeCompare(bValue) * (sortConfig.direction === 'asc' ? 1 : -1);
        }
        
        // Handle numeric/other comparable types
        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    return items;
  }, [initialData, sortConfig, searchTerm, searchableFields]);

  const requestSort = useCallback((key: keyof T) => {
    let direction: SortDirection = 'asc';
    if (
      sortConfig.key === key &&
      sortConfig.direction === 'asc'
    ) {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  }, [sortConfig]);

  // Simple setter for search term
  const handleSetSearchTerm = useCallback((term: string) => {
      setSearchTerm(term);
  }, []);

  return { 
    processedData, 
    sortConfig, 
    requestSort, 
    searchTerm, 
    setSearchTerm: handleSetSearchTerm 
  };
} 