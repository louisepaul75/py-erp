import type { Group } from "../types"

// Mock data
export let groups: Group[] = [
  {
    id: "1",
    name: "Administrators",
    description: "Full access to all features",
    permissions: [
      { id: "1", name: "View User", code: "user:view", description: "Can view users", module: "users" },
      { id: "2", name: "Create User", code: "user:create", description: "Can create new users", module: "users" },
      { id: "3", name: "Edit User", code: "user:edit", description: "Can edit existing users", module: "users" },
      { id: "4", name: "Delete User", code: "user:delete", description: "Can delete users", module: "users" },
      { id: "5", name: "View Group", code: "group:view", description: "Can view groups", module: "users" },
      { id: "6", name: "Create Group", code: "group:create", description: "Can create new groups", module: "users" },
      { id: "7", name: "Edit Group", code: "group:edit", description: "Can edit existing groups", module: "users" },
      { id: "8", name: "Delete Group", code: "group:delete", description: "Can delete groups", module: "users" },
    ],
  },
  {
    id: "2",
    name: "Content Editors",
    description: "Can edit content but not users or groups",
    permissions: [
      { id: "15", name: "View Order", code: "order:view", description: "Can view orders", module: "sales" },
      { id: "16", name: "Create Order", code: "order:create", description: "Can create new orders", module: "sales" },
      { id: "17", name: "Edit Order", code: "order:edit", description: "Can edit existing orders", module: "sales" },
    ],
  },
  {
    id: "3",
    name: "Viewers",
    description: "Read-only access",
    permissions: [
      { id: "1", name: "View User", code: "user:view", description: "Can view users", module: "users" },
      {
        id: "9",
        name: "View Inventory",
        code: "inventory:view",
        description: "Can view inventory levels",
        module: "warehouse",
      },
      { id: "15", name: "View Order", code: "order:view", description: "Can view orders", module: "sales" },
    ],
  },
]

// Simulate API calls with delays
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function fetchGroups(): Promise<Group[]> {
  await delay(500)
  return groups
}

export async function createGroup(groupData: Omit<Group, "id" | "permissions">): Promise<Group> {
  await delay(500)
  const newGroup: Group = {
    id: Math.random().toString(36).substring(2, 9),
    ...groupData,
    permissions: [],
  }
  groups = [...groups, newGroup]
  return newGroup
}

export async function updateGroup(groupData: Partial<Group> & { id: string }): Promise<Group> {
  await delay(500)
  const { id, ...rest } = groupData
  groups = groups.map((group) => (group.id === id ? { ...group, ...rest } : group))
  return groups.find((group) => group.id === id)!
}

export async function deleteGroup(id: string): Promise<void> {
  await delay(500)
  groups = groups.filter((group) => group.id !== id)
}

export async function updateGroupPermissions(groupId: string, permissionIds: string[]): Promise<Group> {
  await delay(500)

  // Import permissions dynamically to avoid circular dependencies
  const { permissions } = await import("./permissions")

  const selectedPermissions = permissions.filter((permission) => permissionIds.includes(permission.id))

  groups = groups.map((group) => (group.id === groupId ? { ...group, permissions: selectedPermissions } : group))

  return groups.find((group) => group.id === groupId)!
}

