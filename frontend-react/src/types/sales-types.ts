export enum ConsentStatus {
  GRANTED = 'GRANTED',
  REVOKED = 'REVOKED',
  PENDING = 'PENDING',
  UNKNOWN = 'UNKNOWN', // Added for cases where status isn't set
}

export enum VerifiedStatus {
  VERIFIED = 'VERIFIED',
  UNVERIFIED = 'UNVERIFIED',
  PENDING = 'PENDING',
}

// Basic Address structure (adjust fields as needed based on your backend)
export interface Address {
  id: number | string;
  street: string;
  houseNumber?: string; // Optional
  zipCode: string;
  city: string;
  country: string;
  isPrimary?: boolean; // Optional indicator for primary address
}

// Basic Shop Account structure
export interface ShopAccount {
  id: number | string;
  shopName: string;
  username: string;
  lastLogin?: string | Date; // Optional
}

// Basic Call History Entry structure
export interface CallHistoryEntry {
  id: number | string;
  timestamp: string | Date;
  agentName?: string; // Optional
  durationSeconds?: number; // Optional
  notes?: string; // Optional
  callType?: string; // e.g., 'INBOUND', 'OUTBOUND'
}

// Generic History Entry structure
export interface HistoryEntry {
  id: number | string;
  timestamp: string | Date;
  eventType: string; // e.g., 'ORDER_PLACED', 'PASSWORD_RESET', 'ADDRESS_CHANGED'
  details: string | Record<string, any>; // Can be simple string or structured data
  userId?: number | string; // Optional user/agent who triggered the event
}

// Basic Sales Representative structure
export interface SalesRepresentative {
  id: number | string;
  name: string;
  email?: string; // Optional
}

export interface Customer {
  id: number | string; // Allow string ID as well
  customer_number: string;
  name: string; // Keep for potential fallback/display name // Consider deprecating if firstName/lastName/companyName cover all cases
  customer_group?: string; // Make optional as it might not always be present
  vat_id?: string; // Make optional

  // --- Existing fields from draft analysis ---
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
  lastOrderDate?: string | Date | null; // Added missing field

  // --- New fields ---
  isActive?: boolean;
  inactiveReason?: string;       // Reason if isActive is false
  inactiveReasonDetails?: string; // More details for the inactive reason
  shopAccounts?: ShopAccount[];
  callHistory?: CallHistoryEntry[];
  historyEntries?: HistoryEntry[]; // General history/audit log
  shippingAddresses?: Address[]; // Array of shipping addresses
  billingStreet?: string;      // Added missing field
  billingPostalCode?: string;  // Added missing field
  billingCity?: string;        // Added missing field
  billingCountry?: string;     // Added missing field
  postalAdvertising?: ConsentStatus; // Consent for postal mail
  emailAdvertising?: ConsentStatus;  // Consent for email marketing
  salesRepresentative?: SalesRepresentative | null; // Assigned sales rep
  verifiedStatus?: VerifiedStatus; // e.g., email verified, KYC status

  // --- Payment related fields ---
  paymentTermsOverall?: string; // Added missing field
  discount?: number | null;      // Added missing field
  creditLimit?: number | null;   // Added missing field

  // --- Potential existing fields (add if relevant) ---
  // delivery_block?: boolean;
  // created_at?: string | Date;
  // updated_at?: string | Date;
  // Add other relevant fields from the Customer model as needed

  // Removed [key: string]: any; for better type safety
}

// Add other sales-related types here if necessary 