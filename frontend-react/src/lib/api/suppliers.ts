import { Supplier, NewSupplier, UpdateSupplier } from '@/types/supplier';
import { instance } from '../api'; // Import the configured ky instance

// Define the relative path for the suppliers endpoint
const SUPPLIERS_RELATIVE_PATH = 'v1/business/suppliers'; 

// --- API Functions ---

// Fetch all suppliers
export async function fetchSuppliers(): Promise<Supplier[]> {
  // Use the shared ky instance with the relative path
  // ky automatically adds the trailing slash based on the prefixUrl if needed
  const response = await instance.get(`${SUPPLIERS_RELATIVE_PATH}/`).json<{ results: Supplier[] }>();
  return response.results || []; // Assuming API returns { results: [...] }
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