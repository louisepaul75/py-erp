import { Supplier, NewSupplier, UpdateSupplier } from '@/types/supplier';
import { instance } from '../api'; // Import the configured ky instance

// Define the relative path for the suppliers endpoint
const SUPPLIERS_RELATIVE_PATH = 'v1/business/suppliers'; 

// Define the expected response structure with pagination
interface PaginatedSuppliersResponse {
  results: Supplier[];
  count: number; // Total number of items
}

// Define the structure returned by our fetch function
export interface FetchSuppliersResult {
  data: Supplier[];
  meta: {
    totalCount: number;
    totalPages: number;
    currentPage: number;
    pageSize: number;
  };
}

// Type for sync status filter
export type SyncStatus = "all" | "synced" | "not_synced";

// --- API Functions ---

// Fetch suppliers with pagination, search, and filter
export async function fetchSuppliers(
  search?: string,
  page: number = 1,
  pageSize: number = 10,
  syncStatus: SyncStatus = "all" // Default to 'all'
): Promise<FetchSuppliersResult> {
  // Build options with search, page, limit, and sync_status parameters
  const params: Record<string, string> = {
    page: page.toString(),
    limit: pageSize.toString(),
  };

  if (search && search.trim() !== '') {
    params.search = search;
  }

  // Only add sync_status if it's not 'all'
  if (syncStatus && syncStatus !== "all") {
    params.sync_status = syncStatus;
  }

  const options = { searchParams: params };

  // Use the shared ky instance with the relative path and options
  const response = await instance
    .get(`${SUPPLIERS_RELATIVE_PATH}/`, options)
    .json<PaginatedSuppliersResponse>();

  const totalCount = response.count || 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  return {
    data: response.results || [],
    meta: {
      totalCount,
      totalPages,
      currentPage: page,
      pageSize,
    },
  };
}

// Fetch a single supplier by ID
export async function fetchSupplierById(id: number | string): Promise<Supplier> {
  // Use ky instance with relative path and ID
  const response = await instance.get(`${SUPPLIERS_RELATIVE_PATH}/${id}/`).json<Supplier>();
  return response;
}

// Create a new supplier
export async function createSupplier(supplierData: NewSupplier): Promise<Supplier> {
  // Use ky instance with post method and relative path
  const response = await instance.post(`${SUPPLIERS_RELATIVE_PATH}/`, {
    json: supplierData,
  }).json<Supplier>();
  return response;
}

// Update an existing supplier (using PATCH for partial updates)
export async function updateSupplier(
  id: number | string,
  supplierData: Partial<UpdateSupplier> // Allow partial updates
): Promise<Supplier> {
  // Use ky instance with patch method and relative path
  const response = await instance.patch(`${SUPPLIERS_RELATIVE_PATH}/${id}/`, {
    json: supplierData,
  }).json<Supplier>();
  return response;
}

// Delete a supplier by ID
export async function deleteSupplier(id: number | string): Promise<void> {
  // Use ky instance with delete method and relative path
  // No need to call .json() for a 204 response
  await instance.delete(`${SUPPLIERS_RELATIVE_PATH}/${id}/`);
} 