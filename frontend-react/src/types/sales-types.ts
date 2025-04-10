export interface Customer {
  id: number | string; // Allow string ID as well
  customer_number: string;
  name: string; // Keep for potential fallback/display name
  customer_group?: string; // Make optional as it might not always be present
  vat_id?: string; // Make optional

  // --- Fields added from draft analysis ---
  firstName?: string;         // Optional
  lastName?: string;          // Optional
  companyName?: string;       // Optional, relevant if isCompany is true
  isCompany?: boolean;        // Indicates if it's a company or individual
  emailMain?: string;         // Optional primary email
  phoneMain?: string;         // Optional primary phone
  orderCount?: number;        // Optional count of orders
  since?: string | Date;      // Optional date customer was added (ISO string or Date object)
  totalSpent?: number;        // Optional total amount spent
  avatar?: string | null;     // Optional URL to an avatar image

  // Add other relevant fields from the Customer model as needed
  // e.g., delivery_block, created_at, addresses, contacts

  // Allow any other properties potentially coming from the API
  [key: string]: any;
}

// Add other sales-related types here if necessary 