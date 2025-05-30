import type { User } from "../types"
import { API_BASE_URL } from "../config";
import { instance } from "../api"
import type { Group } from "@/types"

// Define a type for the creation payload
export type CreateUserPayload = {
  username: string;
  email: string;
  password?: string;
  profile?: {
    phone?: string | null;
  };
  // Add other expected fields if necessary
};

// Helper function to get a cookie by name
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Mock data
export let users: User[] = [
  {
    id: "1",
    name: "John Doe",
    email: "john@example.com",
    role: "Admin",
    isActive: true,
    twoFactorEnabled: true,
    passwordLastChanged: new Date(2023, 9, 15),
    phone: "+49 123 456789",
    lastLogin: new Date(2023, 11, 1),
    groups: [
      { id: "1", name: "Administrators" },
      { id: "2", name: "Content Editors" },
    ],
  },
  {
    id: "2",
    name: "Jane Smith",
    email: "jane@example.com",
    role: "Editor",
    isActive: true,
    twoFactorEnabled: false,
    passwordLastChanged: new Date(2023, 10, 5),
    phone: "+49 987 654321",
    groups: [{ id: "2", name: "Content Editors" }],
  },
  {
    id: "3",
    name: "Bob Johnson",
    email: "bob@example.com",
    role: "Viewer",
    isActive: false,
    twoFactorEnabled: false,
    requirePasswordChange: true,
    phone: "+49 555 123456",
    groups: [{ id: "3", name: "Viewers" }],
  },
]

// Mock data can be kept for testing or fallback
export let mockUsers: User[] = [
  {
    id: "1",
    name: "John Doe",
    email: "john@example.com",
    role: "Admin",
    isActive: true,
    twoFactorEnabled: true,
    passwordLastChanged: new Date(2023, 9, 15),
    phone: "+49 123 456789",
    lastLogin: new Date(2023, 11, 1),
    groups: [
      { id: "1", name: "Administrators" },
      { id: "2", name: "Content Editors" },
    ],
  },
  {
    id: "2",
    name: "Jane Smith",
    email: "jane@example.com",
    role: "Editor",
    isActive: true,
    twoFactorEnabled: false,
    passwordLastChanged: new Date(2023, 10, 5),
    phone: "+49 987 654321",
    groups: [{ id: "2", name: "Content Editors" }],
  },
  {
    id: "3",
    name: "Bob Johnson",
    email: "bob@example.com",
    role: "Viewer",
    isActive: false,
    twoFactorEnabled: false,
    requirePasswordChange: true,
    phone: "+49 555 123456",
    groups: [{ id: "3", name: "Viewers" }],
  },
]

// Simulate API calls with delays
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// Define the User type based on the Django UserSerializer
export interface UserSummary {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
}

/**
 * Fetches a list of users from the API.
 * Supports filtering/searching if implemented in the backend.
 */
export const fetchUsers = async (): Promise<UserSummary[]> => {
  const response = await instance.get("v1/business/users/"); // Correct endpoint
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
  console.error("Unexpected API response structure for fetchUsers:", data);
  throw new Error('Failed to fetch users: Invalid API response format');
};

// Füge diese Funktion zur users.ts hinzu
export async function fetchUserById(userId: string): Promise<User> {
  await delay(300)
  const user = users.find((u) => u.id === userId)

  if (!user) {
    throw new Error("User not found")
  }

  return user
}

// Replace the mock createUser with a real API call
export async function createUser(
  // Use the new payload type
  userData: CreateUserPayload,
): Promise<User> {
  try {
    const token = getCookie('access_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/users/users/`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(userData), // Send user data (including password) in the body
      credentials: 'include'
    });

    if (!response.ok) {
      // Attempt to parse error message from backend
      let errorData = { message: `HTTP error! status: ${response.status}` };
      try {
        errorData = await response.json();
      } catch (e) {
        // Ignore if response is not JSON
      }
      console.error("Error creating user:", errorData);
      // Throw an error with the backend message if available
      throw new Error(errorData.message || `Failed to create user. Status: ${response.status}`);
    }

    const createdUser = await response.json();

    // Transform backend response to frontend User type if needed
    // This is similar to fetchUsers, adapt based on your actual backend response structure
    return {
      id: createdUser.id.toString(),
      name: createdUser.username,
      email: createdUser.email,
      role: createdUser.is_superuser ? "Admin" : createdUser.is_staff ? "Editor" : "Viewer",
      isActive: createdUser.is_active,
      twoFactorEnabled: false, // Assuming default, adjust if backend provides this
      requirePasswordChange: false, // Assuming default
      lastLogin: createdUser.last_login ? new Date(createdUser.last_login) : undefined,
      passwordLastChanged: undefined,
      phone: createdUser.profile?.phone,
      groups: createdUser.groups || [],
    };

  } catch (error) {
    console.error("Error in createUser API call:", error);
    // Re-throw the error so the mutation's onError can handle it
    throw error;
  }
}

export async function updateUser(userData: Partial<User> & { id: string }): Promise<User> {
  await delay(500)
  const { id, ...rest } = userData
  users = users.map((user) => (user.id === id ? { ...user, ...rest } : user))
  return users.find((user) => user.id === id)!
}

export async function deleteUser(id: string): Promise<void> {
  try {
    const token = getCookie('access_token');
    const headers: HeadersInit = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/users/users/${id}/`, { // Append user ID to URL
      method: 'DELETE', // Use DELETE method
      headers: headers,
      credentials: 'include'
    });

    if (!response.ok) {
      // Handle specific statuses if needed (e.g., 404 Not Found)
      let errorData = { message: `HTTP error! status: ${response.status}` };
      try {
        // Check if there's a JSON body with more details, otherwise use status text
        if (response.headers.get("content-type")?.includes("application/json")) {
            errorData = await response.json();
        } else {
             errorData.message = `HTTP error! status: ${response.status} ${response.statusText}`;
        }
      } catch (e) {
         errorData.message = `HTTP error! status: ${response.status} ${response.statusText}`;
      }
      console.error("Error deleting user:", errorData);
      throw new Error(errorData.message || `Failed to delete user. Status: ${response.status}`);
    }

    // DELETE requests often return 204 No Content on success, no need to parse JSON body
    console.log(`User with id ${id} deleted successfully.`);

  } catch (error) {
    console.error("Error in deleteUser API call:", error);
    throw error; // Re-throw for react-query's onError
  }
}

export async function updateUserGroups(userId: string, groupIds: string[]): Promise<User> {
  // Correct the API endpoint URL
  const response = await instance.post(`v1/users/users/${userId}/set-groups/`, { 
    json: { group_ids: groupIds }
  });
  
  // Assuming the backend returns the updated user object or at least the group list
  // If it returns the full user object:
  // return response.json<User>(); 

  // If it returns { detail: string, groups: Group[] }, we need to fetch the user again or update locally.
  // For now, let's assume it returns enough info or we invalidate query which triggers refetch.
  // The mutation already invalidates the 'users' query, so a refetch will happen.
  // We might need to return a specific type or handle the response differently based on actual API.
  
  // Placeholder return - adjust based on actual API response structure if needed
  // Or remove return if mutation onSuccess handles everything.
  const updatedUserData = await response.json<{ detail: string, groups: Group[] }>(); 
  // For now, just return a dummy user structure or throw if error
  // A better approach is to have the backend return the full updated user object.
  const partialUser: Partial<User> = { id: userId, groups: updatedUserData.groups }; 
  return partialUser as User; // Cast needed as we don't have the full user here

  /* Old mock logic:
  await delay(500)

  // Import groups dynamically to avoid circular dependencies
  const { groups } = await import("./groups")

  const selectedGroups = groups.filter((group) => groupIds.includes(group.id))

  users = users.map((user) => (user.id === userId ? { ...user, groups: selectedGroups } : user))

  return users.find((user) => user.id === userId)!
  */
}

// Define a basic Permission type if not already defined/imported elsewhere
// You might need to adjust this based on your actual Permission structure
interface Permission {
  id: string;
  name: string;
  // Add other permission fields as needed
}

export async function getUserPermissions(userId: string): Promise<string[]> {
  await delay(500)

  // Find the user
  const user = users.find((u) => u.id === userId)
  if (!user || !user.groups) return []

  // Get all permissions from all groups the user belongs to
  const permissionIds = new Set<string>()

  // Add explicit types to group and permission
  user.groups.forEach((group: Group) => { 
    // Assuming Group type has an optional permissions array
    if (group.permissions) { 
      group.permissions.forEach((permission: Permission) => {
        permissionIds.add(permission.id)
      })
    }
  })

  return Array.from(permissionIds)
}

