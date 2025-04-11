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
  const response = await instance.get("v1/business/employees/"); // Add v1/ prefix
  return await response.json(); // Use .json() to parse the response
};

/**
 * Fetches a single employee by their ID.
 */
export const fetchEmployeeById = async (id: string | number): Promise<Employee> => {
  const response = await instance.get(`v1/business/employees/${id}/`); // Add v1/ prefix
  return await response.json(); // Use .json() to parse the response
};

// Add functions for creating, updating, deleting employees as needed 