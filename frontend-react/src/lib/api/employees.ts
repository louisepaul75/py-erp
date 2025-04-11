import { instance } from "@/lib/api"; // Correct import for the ky instance
import { User } from "@/lib/types"; // Import User type instead of UserSummary

// Define the Employee type based on the Django serializer
export interface Employee {
  id: number;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string | null;
  phone_number: string | null;
  department: string | null; // Or a more specific type if applicable
  job_title: string | null;
  date_hired: string; // ISO date string
  date_of_birth: string | null; // ISO date string
  address: string | null; // Consider a structured address type later if needed
  user: User | null; // Use the imported User type
}

/**
 * Fetches a list of employees from the API.
 * Supports pagination, filtering, and searching if implemented in the backend.
 */
export const fetchEmployees = async (): Promise<Employee[]> => {
  // TODO: Add parameters for pagination, filtering, sorting, searching
  const response = await instance.get("v1/business/employees/");
  const data = await response.json();

  // Check if the response looks like a paginated DRF response
  if (data && typeof data === 'object' && Array.isArray(data.results)) {
    return data.results; // Return only the results array
  }
  
  // If it's not the expected paginated structure, maybe it's already an array?
  if (Array.isArray(data)) {
    return data;
  }

  // Log an error or throw if the structure is unexpected
  console.error("Unexpected API response structure for fetchEmployees:", data);
  throw new Error('Failed to fetch employees: Invalid API response format');
};

/**
 * Fetches a single employee by their ID.
 */
export const fetchEmployeeById = async (id: string | number): Promise<Employee> => {
  const response = await instance.get(`v1/business/employees/${id}/`); // Add v1/ prefix
  return await response.json(); // Use .json() to parse the response
};

// Add functions for creating, updating, deleting employees as needed 