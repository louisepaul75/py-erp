import type { User } from "../types"

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

// Simulate API calls with delays
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function fetchUsers(): Promise<User[]> {
  await delay(500)
  return users
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

export async function createUser(
  userData: Omit<User, "id" | "groups" | "isActive" | "twoFactorEnabled">,
): Promise<User> {
  await delay(500)
  const newUser: User = {
    id: Math.random().toString(36).substring(2, 9),
    ...userData,
    isActive: true,
    twoFactorEnabled: false,
    groups: [],
  }
  users = [...users, newUser]
  return newUser
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

