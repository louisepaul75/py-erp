import api from './api';

// Define User type - extend with fields from our new module
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  groups: GroupSummary[];
  // Profile related fields
  profile?: UserProfile;
}

export interface UserProfile {
  id: number;
  user: number;
  department: string;
  position: string;
  phone: string;
  language_preference: string;
  profile_picture: string | null;
  status: 'active' | 'inactive' | 'pending' | 'locked';
  two_factor_enabled: boolean;
}

export interface Group {
  id: number;
  name: string;
  permissions: number[];
}

export interface GroupSummary {
  id: number;
  name: string;
}

export interface Role {
  id: number;
  group: number;
  group_name: string;
  description: string;
  is_system_role: boolean;
  priority: number;
  parent_role: number | null;
}

export interface Permission {
  id: number;
  name: string;
  codename: string;
  content_type: number;
}

// Interface for filtering users
export interface UserFilters {
  search?: string;
  department?: string;
  status?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

// Users API endpoints
const usersApi = {
  // Get all users with optional filters
  getUsers: async (filters: UserFilters = {}) => {
    return api.get('/users/users/', { params: filters });
  },

  // Get user details by ID
  getUser: async (id: number) => {
    return api.get(`/users/users/${id}/`);
  },

  // Create a new user
  createUser: async (userData: Partial<User>) => {
    return api.post('/users/users/', userData);
  },

  // Update a user
  updateUser: async (id: number, userData: Partial<User>) => {
    return api.patch(`/users/users/${id}/`, userData);
  },

  // Delete a user
  deleteUser: async (id: number) => {
    return api.delete(`/users/users/${id}/`);
  },

  // Assign user to groups
  assignGroups: async (userId: number, groupIds: number[]) => {
    return api.post(`/users/users/${userId}/assign_groups/`, {
      group_ids: groupIds
    });
  },

  // Remove user from groups
  removeGroups: async (userId: number, groupIds: number[]) => {
    return api.post(`/users/users/${userId}/remove_groups/`, {
      group_ids: groupIds
    });
  },

  // Update user status
  updateStatus: async (userId: number, status: string) => {
    return api.post(`/users/users/${userId}/update_status/`, {
      status
    });
  },

  // Get users grouped by department
  getUsersByDepartment: async () => {
    return api.get('/users/users/by_department/');
  },

  // Get users grouped by status
  getUsersByStatus: async () => {
    return api.get('/users/users/by_status/');
  },

  // Groups API
  getGroups: async () => {
    return api.get('/users/groups/');
  },

  getGroup: async (id: number) => {
    return api.get(`/users/groups/${id}/`);
  },

  createGroup: async (groupData: Partial<Group>) => {
    return api.post('/users/groups/', groupData);
  },

  updateGroup: async (id: number, groupData: Partial<Group>) => {
    return api.patch(`/users/groups/${id}/`, groupData);
  },

  deleteGroup: async (id: number) => {
    return api.delete(`/users/groups/${id}/`);
  },

  // Get users in a group
  getGroupUsers: async (groupId: number) => {
    return api.get(`/users/groups/${groupId}/users/`);
  },

  // Get permissions in a group
  getGroupPermissions: async (groupId: number) => {
    return api.get(`/users/groups/${groupId}/permissions/`);
  },

  // Add permissions to a group
  addPermissionsToGroup: async (groupId: number, permissionIds: number[]) => {
    return api.post(`/users/groups/${groupId}/add_permissions/`, {
      permission_ids: permissionIds
    });
  },

  // Remove permissions from a group
  removePermissionsFromGroup: async (groupId: number, permissionIds: number[]) => {
    return api.post(`/users/groups/${groupId}/remove_permissions/`, {
      permission_ids: permissionIds
    });
  },

  // Get all permissions
  getPermissions: async () => {
    return api.get('/users/permissions/');
  },

  // Get permissions by category
  getPermissionsByCategory: async () => {
    return api.get('/users/permissions/by_category/');
  },

  // Roles API
  getRoles: async () => {
    return api.get('/users/roles/');
  },

  getRole: async (id: number) => {
    return api.get(`/users/roles/${id}/`);
  },

  // Get users with a specific role
  getRoleUsers: async (roleId: number) => {
    return api.get(`/users/roles/${roleId}/users/`);
  },

  // Get child roles
  getChildRoles: async (roleId: number) => {
    return api.get(`/users/roles/${roleId}/child_roles/`);
  }
};

export default usersApi; 