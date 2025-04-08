import type { User } from "../types"
import { API_BASE_URL } from "../config";

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

export async function fetchUsers(): Promise<User[]> {
  try {
    const token = getCookie('access_token'); // Get token from cookie
    const headers: HeadersInit = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`; // Set Authorization header
    }

    const response = await fetch(`${API_BASE_URL}/users/users/`, {
      method: 'GET', // Explicitly state method
      headers: headers, // Add headers
      credentials: 'include' // Keep this for potential CSRF or other cookies
    });
    
    if (!response.ok) {
      // Handle 401 specifically - maybe redirect to login or refresh token?
      if (response.status === 401) {
        console.error("Authorization failed. Token might be invalid or expired.");
        // Potentially trigger a token refresh mechanism here
      }
      console.error("Error fetching users:", response.statusText, response.status);
      // Fallback to mock data if API call fails
      return mockUsers;
    }
    
    const data = await response.json();
    const results = data.results || []; // Handle paginated response format
    
    // Transform backend data to match frontend User type if needed
    const users = results.map((user: any) => ({
      id: user.id.toString(),
      name: user.name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username,
      email: user.email,
      role: user.is_superuser ? "Admin" : user.is_staff ? "Editor" : "Viewer",
      isActive: user.is_active,
      twoFactorEnabled: false, // This might come from a different API or user extension
      requirePasswordChange: false, // Add this from backend if available
      lastLogin: user.last_login ? new Date(user.last_login) : undefined,
      passwordLastChanged: undefined, // Add this from backend if available
      phone: undefined, // Add this from backend if available
      groups: user.groups || [], // If groups aren't directly included, we'll need another API call
    }));
    
    return users;
  } catch (error) {
    console.error("Error fetching users:", error);
    // Fallback to mock data on error
    return mockUsers;
  }
}

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
  await delay(500)
  users = users.filter((user) => user.id !== id)
}

export async function updateUserGroups(userId: string, groupIds: string[]): Promise<User> {
  await delay(500)

  // Import groups dynamically to avoid circular dependencies
  const { groups } = await import("./groups")

  const selectedGroups = groups.filter((group) => groupIds.includes(group.id))

  users = users.map((user) => (user.id === userId ? { ...user, groups: selectedGroups } : user))

  return users.find((user) => user.id === userId)!
}

export async function getUserPermissions(userId: string): Promise<string[]> {
  await delay(500)

  // Find the user
  const user = users.find((u) => u.id === userId)
  if (!user || !user.groups) return []

  // Get all permissions from all groups the user belongs to
  const permissionIds = new Set<string>()

  user.groups.forEach((group) => {
    if (group.permissions) {
      group.permissions.forEach((permission) => {
        permissionIds.add(permission.id)
      })
    }
  })

  return Array.from(permissionIds)
}

