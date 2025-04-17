import { useState, useEffect, useCallback, useMemo } from 'react';
import { Employee } from '@/lib/api/employees';
import { UseQueryResult } from '@tanstack/react-query';
import { EmployeeFilters } from '@/components/employees/employee-filter-dialog';

type SortDirection = 'asc' | 'desc';

interface SortConfig {
  key: keyof Employee | null;
  direction: SortDirection;
}

interface UseEmployeesTableProps {
  employees: Employee[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  initialSortKey?: keyof Employee | null;
  initialSortDirection?: SortDirection;
  initialSearchTerm?: string;
  searchableFields?: (keyof Employee)[];
  initialFilters?: EmployeeFilters;
}

interface UseEmployeesTableReturn {
  filteredEmployees: Employee[];
  sortConfig: SortConfig;
  requestSort: (key: keyof Employee) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  pagination: {
    currentPage: number;
    totalPages: number;
    pageSize: number;
    totalItems: number;
  };
  goToPage: (page: number) => void;
  goToNextPage: () => void;
  goToPreviousPage: () => void;
  paginatedEmployees: Employee[];
  filters: EmployeeFilters;
  setFilters: (filters: EmployeeFilters) => void;
}

// Default filters
const defaultFilters: EmployeeFilters = {
  isActive: null,
  isTerminated: null,
  employmentStatus: 'all',
};

// Filter function for employees
const employeeFilterFunction = (employee: Employee, filters: EmployeeFilters): boolean => {
  // Filter by active status
  if (filters.isActive !== null) {
    if (filters.isActive !== employee.is_active) {
      return false;
    }
  }

  // Filter by terminated status
  if (filters.isTerminated !== null) {
    if (filters.isTerminated !== employee.is_terminated) {
      return false;
    }
  }

  // Filter by employment status
  if (filters.employmentStatus !== 'all') {
    switch (filters.employmentStatus) {
      case 'active':
        if (!employee.is_active) return false;
        break;
      case 'terminated':
        if (!employee.is_terminated) return false;
        break;
      case 'present':
        if (!employee.is_present) return false;
        break;
    }
  }

  return true;
};

export function useEmployeesTable({
  employees,
  isLoading,
  isError,
  error,
  initialSortKey = null,
  initialSortDirection = 'asc',
  initialSearchTerm = '',
  searchableFields = ['employee_number', 'first_name', 'last_name', 'email'],
  initialFilters = defaultFilters,
}: UseEmployeesTableProps): UseEmployeesTableReturn {
  const [sortConfig, setSortConfig] = useState<SortConfig>({
    key: initialSortKey,
    direction: initialSortDirection,
  });
  const [searchTerm, setSearchTerm] = useState(initialSearchTerm);
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState(initialSearchTerm);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [filters, setFilters] = useState<EmployeeFilters>(initialFilters);

  // Debounce search term with a longer delay (800ms) for large datasets
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), 800);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Handle sort request
  const requestSort = useCallback((key: keyof Employee) => {
    // Determine the new sort direction
    let direction: SortDirection = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    
    // Update local sort config
    setSortConfig({ key, direction });
    console.log(`Sorting employees by ${String(key)} in ${direction} order`);
    
    // Reset to first page when sorting changes
    setCurrentPage(0);
  }, [sortConfig]);

  // Filter and sort employees
  const filteredEmployees = useMemo(() => {
    if (isLoading || isError || !employees) {
      return [];
    }

    // First, filter by search term if provided
    let filtered = [...employees];
    if (debouncedSearchTerm && searchableFields.length > 0) {
      const lowerCaseSearchTerm = debouncedSearchTerm.toLowerCase();
      filtered = filtered.filter(employee => {
        return searchableFields.some(field => {
          const value = employee[field];
          return value !== null && value !== undefined &&
                 String(value).toLowerCase().includes(lowerCaseSearchTerm);
        });
      });
    }

    // Apply custom filters
    filtered = filtered.filter(employee => 
      employeeFilterFunction(employee, filters)
    );
    
    console.log(`Filtered employees: ${filtered.length} of ${employees.length}`);

    // Then, sort the filtered results
    if (sortConfig.key) {
      filtered.sort((a, b) => {
        const aValue = a[sortConfig.key!];
        const bValue = b[sortConfig.key!];
        
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
    }

    return filtered;
  }, [employees, debouncedSearchTerm, searchableFields, sortConfig, isLoading, isError, filters]);

  // Reset to first page when search term or filters change
  useEffect(() => {
    setCurrentPage(0);
  }, [debouncedSearchTerm, filters]);

  // Handle filter changes
  const handleSetFilters = useCallback((newFilters: EmployeeFilters) => {
    setFilters(newFilters);
    // Reset to first page when filters change is handled by the useEffect above
  }, []);

  // Pagination
  const totalItems = filteredEmployees.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  
  const goToPage = useCallback((page: number) => {
    if (page >= 0 && page < totalPages) {
      setCurrentPage(page);
    }
  }, [totalPages]);

  const goToNextPage = useCallback(() => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(prev => prev + 1);
    }
  }, [currentPage, totalPages]);

  const goToPreviousPage = useCallback(() => {
    if (currentPage > 0) {
      setCurrentPage(prev => prev - 1);
    }
  }, [currentPage]);

  // Get paginated employees
  const paginatedEmployees = useMemo(() => {
    const start = currentPage * pageSize;
    const end = start + pageSize;
    return filteredEmployees.slice(start, end);
  }, [filteredEmployees, currentPage, pageSize]);

  return {
    filteredEmployees,
    sortConfig,
    requestSort,
    searchTerm,
    setSearchTerm,
    pagination: {
      currentPage,
      totalPages,
      pageSize,
      totalItems,
    },
    goToPage,
    goToNextPage,
    goToPreviousPage,
    paginatedEmployees,
    filters,
    setFilters: handleSetFilters,
  };
}
