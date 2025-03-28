import type {
  ApiEndpoint,
  LogEntry,
  ChangeEntry,
  Automation,
} from "@/types/settings/api";

// Mock data for API endpoints
const mockApiEndpoints: ApiEndpoint[] = [
  {
    id: "1",
    name: "Customer API",
    url: "https://api.example.com/customers",
    status: "active",
    lastSync: "2023-06-15T14:30:00Z",
  },
  {
    id: "2",
    name: "Product Catalog",
    url: "https://api.example.com/products",
    status: "active",
    lastSync: "2023-06-15T12:15:00Z",
  },
  {
    id: "3",
    name: "Order Processing",
    url: "https://api.example.com/orders",
    status: "error",
    lastSync: "2023-06-14T23:45:00Z",
  },
  {
    id: "4",
    name: "Inventory Management",
    url: "https://api.example.com/inventory",
    status: "pending",
    lastSync: "2023-06-15T08:20:00Z",
  },
  {
    id: "5",
    name: "Payment Gateway",
    url: "https://api.payment-provider.com/transactions",
    status: "active",
    lastSync: "2023-06-15T10:05:00Z",
  },
];

// Mock data for logs
const mockLogs: Record<string, LogEntry[]> = {
  "1": [
    {
      id: "log1",
      timestamp: "2023-06-15T14:30:00Z",
      level: "info",
      message: "API sync completed successfully",
      details: "Processed 245 records in 3.2 seconds",
    },
    {
      id: "log2",
      timestamp: "2023-06-15T14:29:55Z",
      level: "info",
      message: "Starting API sync",
    },
    {
      id: "log3",
      timestamp: "2023-06-15T10:15:22Z",
      level: "warning",
      message: "Rate limit approaching",
      details: "Current usage: 85% of allowed requests",
    },
    {
      id: "log4",
      timestamp: "2023-06-14T18:42:10Z",
      level: "error",
      message: "Connection timeout",
      details: "Failed to connect to API after 30 seconds",
    },
    {
      id: "log5",
      timestamp: "2023-06-14T18:40:05Z",
      level: "info",
      message: "Starting API sync",
    },
  ],
  "2": [
    {
      id: "log1",
      timestamp: "2023-06-15T12:15:00Z",
      level: "success",
      message: "Product catalog updated successfully",
      details: "Added 12 products, updated 34, removed 2",
    },
    {
      id: "log2",
      timestamp: "2023-06-15T12:14:30Z",
      level: "info",
      message: "Starting product catalog sync",
    },
  ],
  "3": [
    {
      id: "log1",
      timestamp: "2023-06-14T23:45:00Z",
      level: "error",
      message: "Authentication failed",
      details: "Invalid API credentials provided",
    },
    {
      id: "log2",
      timestamp: "2023-06-14T23:44:50Z",
      level: "info",
      message: "Starting order processing sync",
    },
  ],
  "4": [
    {
      id: "log1",
      timestamp: "2023-06-15T08:20:00Z",
      level: "info",
      message: "Inventory sync in progress",
    },
  ],
  "5": [
    {
      id: "log1",
      timestamp: "2023-06-15T10:05:00Z",
      level: "success",
      message: "Payment gateway sync completed",
      details: "Processed 56 transactions",
    },
  ],
};

// Mock data for changes
const mockChanges: Record<string, ChangeEntry[]> = {
  "1": [
    {
      id: "change1",
      timestamp: "2023-06-15T14:30:00Z",
      type: "added",
      entity: "Customer",
      description: "Added new customer record",
      details: {
        id: "cust123",
        name: "Acme Corp",
        email: "contact@acmecorp.com",
      },
    },
    {
      id: "change2",
      timestamp: "2023-06-15T14:29:45Z",
      type: "modified",
      entity: "Customer",
      description: "Updated customer contact information",
      details: {
        before: {
          id: "cust456",
          name: "XYZ Inc",
          email: "old-email@xyzinc.com",
          phone: "123-456-7890",
        },
        after: {
          id: "cust456",
          name: "XYZ Inc",
          email: "new-email@xyzinc.com",
          phone: "987-654-3210",
        },
      },
    },
    {
      id: "change3",
      timestamp: "2023-06-15T14:28:30Z",
      type: "removed",
      entity: "Customer",
      description: "Removed inactive customer",
      details: {
        id: "cust789",
        name: "Defunct LLC",
        reason: "Account closed",
      },
    },
  ],
  "2": [
    {
      id: "change1",
      timestamp: "2023-06-15T12:15:00Z",
      type: "added",
      entity: "Product",
      description: "Added new products to catalog",
      details: {
        count: 12,
        categories: ["Electronics", "Home Goods"],
      },
    },
    {
      id: "change2",
      timestamp: "2023-06-15T12:14:30Z",
      type: "modified",
      entity: "Product",
      description: "Updated product prices",
      details: {
        before: {
          count: 34,
          averageIncrease: "2.5%",
        },
        after: {
          count: 34,
          averageIncrease: "2.5%",
        },
      },
    },
  ],
  "3": [],
  "4": [],
  "5": [
    {
      id: "change1",
      timestamp: "2023-06-15T10:05:00Z",
      type: "added",
      entity: "Transaction",
      description: "Processed new transactions",
      details: {
        count: 56,
        total: "$12,450.75",
      },
    },
  ],
};

// Add mock logs and changes for automations
// Add this after the mockChanges declaration
const mockAutomationLogs: Record<string, LogEntry[]> = {
  "1": [
    {
      id: "log1",
      timestamp: "2023-06-15T09:00:00Z",
      level: "info",
      message: "Starting daily customer sync",
    },
    {
      id: "log2",
      timestamp: "2023-06-15T09:02:30Z",
      level: "success",
      message: "Customer sync completed successfully",
      details: "Processed 128 customer records",
    },
    {
      id: "log3",
      timestamp: "2023-06-14T09:00:00Z",
      level: "info",
      message: "Starting daily customer sync",
    },
    {
      id: "log4",
      timestamp: "2023-06-14T09:01:45Z",
      level: "warning",
      message: "Some customer records could not be processed",
      details: "3 records had validation errors",
    },
  ],
  "2": [
    {
      id: "log1",
      timestamp: "2023-06-12T08:00:00Z",
      level: "info",
      message: "Starting weekly inventory report generation",
    },
    {
      id: "log2",
      timestamp: "2023-06-12T08:05:20Z",
      level: "success",
      message: "Inventory report generated successfully",
      details: "Report sent to 5 recipients",
    },
  ],
  "3": [
    {
      id: "log1",
      timestamp: "2023-06-01T00:00:00Z",
      level: "info",
      message: "Starting monthly financial reconciliation",
    },
    {
      id: "log2",
      timestamp: "2023-06-01T00:45:10Z",
      level: "success",
      message: "Financial reconciliation completed",
      details: "All accounts balanced successfully",
    },
  ],
  "4": [
    {
      id: "log1",
      timestamp: "2023-06-15T14:45:00Z",
      level: "info",
      message: "Updating order statuses",
    },
    {
      id: "log2",
      timestamp: "2023-06-15T14:45:30Z",
      level: "success",
      message: "Order statuses updated",
      details: "Updated 17 orders",
    },
  ],
  "5": [
    {
      id: "log1",
      timestamp: "2023-06-14T23:00:00Z",
      level: "info",
      message: "Starting data backup",
    },
    {
      id: "log2",
      timestamp: "2023-06-14T23:15:45Z",
      level: "error",
      message: "Backup failed",
      details: "Insufficient storage space on backup drive",
    },
  ],
};

const mockAutomationChanges: Record<string, ChangeEntry[]> = {
  "1": [
    {
      id: "change1",
      timestamp: "2023-06-15T09:02:30Z",
      type: "added",
      entity: "Customer",
      description: "Added new customers from CRM",
      details: {
        count: 15,
        source: "CRM System",
      },
    },
    {
      id: "change2",
      timestamp: "2023-06-15T09:01:45Z",
      type: "modified",
      entity: "Customer",
      description: "Updated customer information",
      details: {
        before: {
          count: 113,
          fields: ["email", "phone", "address"],
        },
        after: {
          count: 113,
          fields: ["email", "phone", "address"],
        },
      },
    },
  ],
  "2": [
    {
      id: "change1",
      timestamp: "2023-06-12T08:05:20Z",
      type: "added",
      entity: "Report",
      description: "Generated weekly inventory report",
      details: {
        filename: "inventory-report-2023-06-12.pdf",
        size: "1.2MB",
      },
    },
  ],
  "3": [
    {
      id: "change1",
      timestamp: "2023-06-01T00:45:10Z",
      type: "modified",
      entity: "Accounts",
      description: "Reconciled financial accounts",
      details: {
        before: {
          status: "Pending",
          accounts: 24,
        },
        after: {
          status: "Reconciled",
          accounts: 24,
        },
      },
    },
  ],
  "4": [
    {
      id: "change1",
      timestamp: "2023-06-15T14:45:30Z",
      type: "modified",
      entity: "Orders",
      description: "Updated order statuses",
      details: {
        before: {
          pending: 10,
          shipped: 7,
        },
        after: {
          pending: 0,
          shipped: 17,
        },
      },
    },
  ],
  "5": [],
};

// Mock data for automations
const mockAutomations: Automation[] = [
  {
    id: "1",
    name: "Daily Customer Sync",
    description: "Synchronizes customer data from CRM to ERP",
    status: "running",
    schedule: "Daily at 09:00",
    lastRun: "2023-06-15T09:00:00Z",
  },
  {
    id: "2",
    name: "Weekly Inventory Report",
    description: "Generates inventory reports and sends to stakeholders",
    status: "scheduled",
    schedule: "Every Monday at 08:00",
    lastRun: "2023-06-12T08:00:00Z",
  },
  {
    id: "3",
    name: "Monthly Financial Reconciliation",
    description: "Reconciles financial data across systems",
    status: "stopped",
    schedule: "Monthly on day 1 at 00:00",
    lastRun: "2023-06-01T00:00:00Z",
  },
  {
    id: "4",
    name: "Order Status Updates",
    description: "Updates order statuses based on shipping provider data",
    status: "running",
    schedule: "Every 15 minutes",
    lastRun: "2023-06-15T14:45:00Z",
  },
  {
    id: "5",
    name: "Data Backup",
    description: "Creates backups of critical business data",
    status: "failed",
    schedule: "Daily at 23:00",
    lastRun: "2023-06-14T23:00:00Z",
  },
];

// API functions with artificial delay to simulate network requests
export async function fetchApiEndpoints(): Promise<ApiEndpoint[]> {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return [...mockApiEndpoints];
}

// Update the fetchEndpointLogs function to handle both endpoints and automations
export async function fetchEndpointLogs(
  endpointId: string
): Promise<LogEntry[]> {
  await new Promise((resolve) => setTimeout(resolve, 700));
  return mockLogs[endpointId] || mockAutomationLogs[endpointId] || [];
}

// Update the fetchEndpointChanges function to handle both endpoints and automations
export async function fetchEndpointChanges(
  endpointId: string
): Promise<ChangeEntry[]> {
  await new Promise((resolve) => setTimeout(resolve, 600));
  return mockChanges[endpointId] || mockAutomationChanges[endpointId] || [];
}

export async function fetchAutomations(): Promise<Automation[]> {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return [...mockAutomations];
}

export async function updateAutomationSchedule(data: {
  id: string;
  schedule: string;
  scheduleType: string;
  time: string;
  weekday?: string;
  dayOfMonth?: string;
}): Promise<Automation> {
  await new Promise((resolve) => setTimeout(resolve, 1000));

  const automation = mockAutomations.find((a) => a.id === data.id);
  if (!automation) {
    throw new Error("Automation not found");
  }

  const updatedAutomation = {
    ...automation,
    schedule: data.schedule,
    status: "scheduled" as const,
  };

  // In a real app, this would update the server
  const index = mockAutomations.findIndex((a) => a.id === data.id);
  if (index !== -1) {
    mockAutomations[index] = updatedAutomation;
  }

  return updatedAutomation;
}
