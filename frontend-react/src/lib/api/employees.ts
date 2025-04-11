import { instance as apiInstance } from "@/lib/api/instance"; // Assuming instance is exported from a central file
import { UserSummary } from "./users"; // Assuming a UserSummary type exists

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
  user: UserSummary | null; // Link to the User model (using a summary type initially)
}

/**
 * Fetches a list of employees from the API.
 * Supports pagination, filtering, and searching if implemented in the backend.
 */
export const fetchEmployees = async (): Promise<Employee[]> => {
  // TODO: Add parameters for pagination, filtering, sorting, searching
  const response = await apiInstance.get<Employee[]>("/business/employees/"); // Using relative path assuming baseURL is set in instance
  return response.data;
};

/**
 * Fetches a single employee by their ID.
 */
export const fetchEmployeeById = async (id: string | number): Promise<Employee> => {
  const response = await apiInstance.get<Employee>(`/business/employees/${id}/`);
  return response.data;
};

// Add functions for creating, updating, deleting employees as needed 