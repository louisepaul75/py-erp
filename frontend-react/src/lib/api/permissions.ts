import type { Permission, PermissionModule } from "../types"

// Mock data grouped by modules
export const permissions: Permission[] = [
  // Users module
  { id: "1", name: "View User", code: "user:view", description: "Can view users", module: "users" },
  { id: "2", name: "Create User", code: "user:create", description: "Can create new users", module: "users" },
  { id: "3", name: "Edit User", code: "user:edit", description: "Can edit existing users", module: "users" },
  { id: "4", name: "Delete User", code: "user:delete", description: "Can delete users", module: "users" },

  { id: "5", name: "View Group", code: "group:view", description: "Can view groups", module: "users" },
  { id: "6", name: "Create Group", code: "group:create", description: "Can create new groups", module: "users" },
  { id: "7", name: "Edit Group", code: "group:edit", description: "Can edit existing groups", module: "users" },
  { id: "8", name: "Delete Group", code: "group:delete", description: "Can delete groups", module: "users" },

  // Warehouse module
  {
    id: "9",
    name: "View Inventory",
    code: "inventory:view",
    description: "Can view inventory levels",
    module: "warehouse",
  },
  {
    id: "10",
    name: "Adjust Inventory",
    code: "inventory:adjust",
    description: "Can adjust inventory quantities",
    module: "warehouse",
  },

  { id: "11", name: "View Product", code: "product:view", description: "Can view products", module: "warehouse" },
  {
    id: "12",
    name: "Create Product",
    code: "product:create",
    description: "Can create new products",
    module: "warehouse",
  },
  {
    id: "13",
    name: "Edit Product",
    code: "product:edit",
    description: "Can edit product details",
    module: "warehouse",
  },
  { id: "14", name: "Delete Product", code: "product:delete", description: "Can delete products", module: "warehouse" },

  // Sales module
  { id: "15", name: "View Order", code: "order:view", description: "Can view orders", module: "sales" },
  { id: "16", name: "Create Order", code: "order:create", description: "Can create new orders", module: "sales" },
  { id: "17", name: "Edit Order", code: "order:edit", description: "Can edit existing orders", module: "sales" },
  { id: "18", name: "Cancel Order", code: "order:cancel", description: "Can cancel orders", module: "sales" },

  {
    id: "19",
    name: "View Customer",
    code: "customer:view",
    description: "Can view customer information",
    module: "sales",
  },
  {
    id: "20",
    name: "Create Customer",
    code: "customer:create",
    description: "Can create new customers",
    module: "sales",
  },
  {
    id: "21",
    name: "Edit Customer",
    code: "customer:edit",
    description: "Can edit customer information",
    module: "sales",
  },
  { id: "22", name: "Delete Customer", code: "customer:delete", description: "Can delete customers", module: "sales" },

  // Production module
  {
    id: "23",
    name: "View Production",
    code: "production:view",
    description: "Can view production orders",
    module: "production",
  },
  {
    id: "24",
    name: "Create Production Order",
    code: "production:create",
    description: "Can create production orders",
    module: "production",
  },
  {
    id: "25",
    name: "Edit Production Order",
    code: "production:edit",
    description: "Can edit production orders",
    module: "production",
  },
  {
    id: "26",
    name: "Complete Production",
    code: "production:complete",
    description: "Can mark production as complete",
    module: "production",
  },

  // Finance module
  { id: "27", name: "View Invoice", code: "invoice:view", description: "Can view invoices", module: "finance" },
  { id: "28", name: "Create Invoice", code: "invoice:create", description: "Can create invoices", module: "finance" },
  { id: "29", name: "Edit Invoice", code: "invoice:edit", description: "Can edit invoices", module: "finance" },
  { id: "30", name: "Delete Invoice", code: "invoice:delete", description: "Can delete invoices", module: "finance" },

  // Reporting module
  {
    id: "31",
    name: "View Sales Reports",
    code: "report:sales",
    description: "Can view sales reports",
    module: "reporting",
  },
  {
    id: "32",
    name: "View Inventory Reports",
    code: "report:inventory",
    description: "Can view inventory reports",
    module: "reporting",
  },
  {
    id: "33",
    name: "View Production Reports",
    code: "report:production",
    description: "Can view production reports",
    module: "reporting",
  },
  { id: "34", name: "Export Reports", code: "report:export", description: "Can export reports", module: "reporting" },
]

// Simulate API calls with delays
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function fetchPermissions(): Promise<Permission[]> {
  await delay(500)
  return permissions
}

export async function fetchPermissionsByModule(module: PermissionModule): Promise<Permission[]> {
  await delay(300)
  return permissions.filter((permission) => permission.module === module)
}

export async function createPermission(permissionData: Omit<Permission, "id">): Promise<Permission> {
  await delay(500)
  const newPermission: Permission = {
    id: Math.random().toString(36).substring(2, 9),
    ...permissionData,
  }
  return newPermission
}

export async function updatePermission(permissionData: Partial<Permission> & { id: string }): Promise<Permission> {
  await delay(500)
  const { id } = permissionData
  return { ...permissions.find((p) => p.id === id)!, ...permissionData }
}

export async function deletePermission(id: string): Promise<void> {
  await delay(500)
  // In a real app, you would remove the permission from the database
}

