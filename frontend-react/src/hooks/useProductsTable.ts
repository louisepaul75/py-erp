import { useState, useEffect, useCallback, useMemo } from 'react';
import { Product, ApiResponse } from '@/components/types/product';
import { UseQueryResult } from '@tanstack/react-query';

type SortDirection = 'asc' | 'desc';

interface SortConfig {
  key: keyof Product | null;
  direction: SortDirection;
}

interface UseProductsTableProps {
  productsQuery: UseQueryResult<ApiResponse<Product>, Error>;
  onPaginationChange: (pageIndex: number) => void;
  onSearchChange: (term: string) => void;
  pagination: { pageIndex: number; pageSize: number };
  initialSortKey?: keyof Product | null;
  initialSortDirection?: SortDirection;
}

interface UseProductsTableReturn {
  products: Product[];
  totalCount: number;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  sortConfig: SortConfig;
  requestSort: (key: keyof Product) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  currentPage: number;
  totalPages: number;
  goToPage: (page: number) => void;
  goToNextPage: () => void;
  goToPreviousPage: () => void;
  isFetching: boolean;
}

export function useProductsTable({
  productsQuery,
  onPaginationChange,
  onSearchChange,
  pagination,
  initialSortKey = null,
  initialSortDirection = 'asc',
}: UseProductsTableProps): UseProductsTableReturn {
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    key: initialSortKey,
    direction: initialSortDirection,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  // Debounce search term with a longer delay (800ms) for large datasets
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), 800);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Propagate search term changes to parent
  useEffect(() => {
    onSearchChange(debouncedSearchTerm);
  }, [debouncedSearchTerm, onSearchChange]);

  // Handle sort request
  const requestSort = useCallback((key: keyof Product) => {
    // Determine the new sort direction
    let direction: SortDirection = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    
    // Update local sort config
    setSortConfig({ key, direction });
    console.log(`Sorting by ${String(key)} in ${direction} order`);
  }, [sortConfig]);

  // Pagination helpers
  const totalCount = productsQuery.data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / pagination.pageSize));
  
  const goToPage = useCallback((page: number) => {
    if (page >= 0 && page < totalPages) {
      onPaginationChange(page);
    }
  }, [totalPages, onPaginationChange]);

  const goToNextPage = useCallback(() => {
    if (pagination.pageIndex < totalPages - 1) {
      onPaginationChange(pagination.pageIndex + 1);
    }
  }, [pagination.pageIndex, totalPages, onPaginationChange]);

  const goToPreviousPage = useCallback(() => {
    if (pagination.pageIndex > 0) {
      onPaginationChange(pagination.pageIndex - 1);
    }
  }, [pagination.pageIndex, onPaginationChange]);

  // Get products from query result
  const rawProducts = productsQuery.data?.results ?? [];
  
  // Apply client-side sorting
  console.log(" products before sorting", rawProducts)
  const processedProducts = useMemo(() => {
    if (!sortConfig.key) {
      return rawProducts;
    }
    
    console.log(`Sorting ${rawProducts.length} products by ${String(sortConfig.key)}`);
    
    const sortedProducts = [...rawProducts].sort((a, b) => {
      const aValue = a[sortConfig.key!];
      const bValue = b[sortConfig.key!];
      
      // Log the values being compared for debugging
      // console.log(`Comparing: ${String(aValue)} vs ${String(bValue)}`);

      // Handle null/undefined values (always sort to the end)
      if (aValue === null || aValue === undefined) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      if (bValue === null || bValue === undefined) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }

      // Handle boolean values
      if (typeof aValue === 'boolean' && typeof bValue === 'boolean') {
        return (aValue === bValue) ? 0 : (aValue ? -1 : 1) * (sortConfig.direction === 'asc' ? 1 : -1);
      }

      // Handle number values
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return (aValue - bValue) * (sortConfig.direction === 'asc' ? 1 : -1);
      }

      // Handle string values
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return aValue.localeCompare(bValue) * (sortConfig.direction === 'asc' ? 1 : -1);
      }

      // Handle mixed types by converting to string
      return String(aValue).localeCompare(String(bValue)) * (sortConfig.direction === 'asc' ? 1 : -1);
    });
    
    console.log(`Sorted products (first 3):`, sortedProducts.slice(0, 3));
    return sortedProducts;
  }, [rawProducts, sortConfig]);

  console.log(" products after sorting", processedProducts)

  return {
    products: processedProducts,
    totalCount,
    isLoading: productsQuery.isLoading,
    isError: productsQuery.isError,
    error: productsQuery.error || null,
    sortConfig,
    requestSort,
    searchTerm,
    setSearchTerm,
    currentPage: pagination.pageIndex,
    totalPages,
    goToPage,
    goToNextPage,
    goToPreviousPage,
    isFetching: productsQuery.isFetching,
  };
}
