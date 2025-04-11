import { Supplier, NewSupplier, UpdateSupplier } from '@/types/supplier';

const API_BASE_URL = '/api/v1/business/suppliers'; // Adjust if your base URL is different

// --- Helper Functions ---

// Generic function to handle fetch responses and errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    // Attempt to parse error details from the response body
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      // Ignore if response body is not JSON
    }
    console.error('API Error:', response.status, response.statusText, errorData);
    throw new Error(
      `API request failed with status ${response.status}: ${response.statusText}`
    );
  }
  // Check if the response has content before trying to parse JSON
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json();
  } else if (response.status === 204) { // Handle No Content response (e.g., for DELETE)
      // biome-ignore lint/suspicious/noExplicitAny: <explanation>
      return null as any; // Return null or an appropriate value for no content
  } else {
    // Handle unexpected content types or empty responses if necessary
    // biome-ignore lint/suspicious/noExplicitAny: <explanation>
    return null as any;
  }
}

// TODO: Add CSRF token handling if required by Django backend
// This might involve fetching a token and including it in 'X-CSRFToken' header
// const getCsrfToken = () => { /* Implementation depends on how token is provided */ };

// --- API Functions ---

// Fetch all suppliers (consider adding pagination parameters if needed)
export async function fetchSuppliers(): Promise<Supplier[]> {
  // TODO: Add authentication headers if required
  const response = await fetch(`${API_BASE_URL}/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': `Bearer ${your_auth_token}`,
      // 'X-CSRFToken': getCsrfToken(),
    },
  });
  // Assuming the API returns a list directly, adjust if nested (e.g., response.results)
  return handleResponse<Supplier[]>(response);
}

// Fetch a single supplier by ID
export async function fetchSupplierById(id: number): Promise<Supplier> {
  const response = await fetch(`${API_BASE_URL}/${id}/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': `Bearer ${your_auth_token}`,
      // 'X-CSRFToken': getCsrfToken(),
    },
  });
  return handleResponse<Supplier>(response);
}

// Create a new supplier
export async function createSupplier(supplierData: NewSupplier): Promise<Supplier> {
  const response = await fetch(`${API_BASE_URL}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': `Bearer ${your_auth_token}`,
      // 'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(supplierData),
  });
  return handleResponse<Supplier>(response);
}

// Update an existing supplier (using PATCH for partial updates)
export async function updateSupplier(
  id: number,
  supplierData: Partial<UpdateSupplier> // Allow partial updates
): Promise<Supplier> {
  const response = await fetch(`${API_BASE_URL}/${id}/`, {
    method: 'PATCH', // Or PUT if you always send the full object
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': `Bearer ${your_auth_token}`,
      // 'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(supplierData),
  });
  return handleResponse<Supplier>(response);
}

// Delete a supplier by ID
export async function deleteSupplier(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/${id}/`, {
    method: 'DELETE',
    headers: {
      // 'Authorization': `Bearer ${your_auth_token}`,
      // 'X-CSRFToken': getCsrfToken(),
    },
  });
  // DELETE often returns 204 No Content, handleResponse handles this
  await handleResponse<void>(response);
} 