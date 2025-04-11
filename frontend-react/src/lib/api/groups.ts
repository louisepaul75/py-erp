import { instance } from "../api"; // Corrected import for ky instance

// Define interfaces for permissions
export interface Permission {
  id: number;
  name: string;
  codename: string;
}

export interface PermissionCategory {
  name: string;
  permissions: Permission[];
}

// Define a basic Group type here since it wasn't found elsewhere
// Adjust properties based on actual API response if needed
export interface Group {
  id: number;
  name: string;
  description?: string;
  permissions: number[];
}

interface GroupsResponse {
  results: Group[];
}

// Removed mock data array
// Removed delay function

// Fetch all groups from the backend
export const fetchGroups = async () => {
  const response = await instance.get("v1/users/groups/").json<GroupsResponse>();
  return response.results;
};

// Create a new group
export const createGroup = (data: { name: string; description?: string }) =>
  instance.post("v1/users/groups/", { json: data }).json<Group>();

// Update an existing group
export const updateGroup = (id: string | number, data: { name: string; description?: string }) =>
  instance.put(`v1/users/groups/${id}/`, { json: data }).json<Group>();

// Delete a group
export const deleteGroup = (id: string | number) =>
  instance.delete(`v1/users/groups/${id}/`).json();

// Fetch all available permissions
export const fetchPermissions = () =>
  instance.get("v1/permissions/").json<Permission[]>();

// Fetch permission categories structure
export const fetchPermissionCategories = () =>
  instance.get("v1/permission-categories/").json<PermissionCategory[]>();

// Fetch permissions for a specific group
export const fetchGroupPermissions = (groupId: string | number) =>
  instance.get(`v1/groups/${groupId}/permissions/`).json<Permission[]>();

// Update permissions for a specific group
export const updateGroupPermissions = (groupId: string | number, permissions: number[]) =>
  instance.put(`v1/groups/${groupId}/permissions/`, { json: { permissions } }).json<Permission[]>();

