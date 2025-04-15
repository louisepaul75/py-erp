export type Customer = {
  id: string; // Assuming UUID
  name: string;
  tax_id?: string | null;
  phone?: string | null;
  email?: string | null;
  website?: string | null;
  notes?: string | null; // General notes, specific notes might be separate
  billing_address?: Address | null;
  // Add other fields as needed based on your CustomerForm
  payment_terms?: string | null; // e.g., "Net 30", "Due on Receipt"
  bank_iban?: string | null;
  bank_bic?: string | null;
  // e.g., payment_terms, currency, etc.
};

export type Address = {
  id?: string; // Optional if part of customer, required if standalone
  street: string;
  city: string;
  state?: string | null;
  postal_code: string;
  country: string; // Consider using a specific country code type if needed
  is_primary?: boolean; // Useful for multiple shipping addresses
};

export type ContactPerson = {
  id: string; // Assuming UUID
  customer_id: string; // Foreign key to Customer
  name: string;
  email?: string | null;
  phone?: string | null;
  position?: string | null;
  is_primary?: boolean; // Is this the main contact?
};

export type ContactInfo = {
  id: string; // Assuming UUID
  customer_id: string; // Foreign key to Customer
  type: 'phone' | 'email' | 'mobile' | 'fax' | 'website'; // Example types
  value: string;
  description?: string | null; // e.g., "Sales Department Phone"
  is_primary?: boolean;
};

// You might want to consolidate Address under a general structure
// if used elsewhere, or keep it specific to Customer if not.

// Placeholder for fetched customer data including contacts
// Adjust based on how your API will return data (nested or separate calls)
export type FullCustomerProfile = Customer & {
  contact_persons?: ContactPerson[];
  contact_infos?: ContactInfo[];
  shipping_addresses?: Address[];
  // Add other related data like notes, documents, etc.
  activity_notes?: CustomerNote[]; // Renamed from notes
  documents?: CustomerDocument[]; // Added documents
};

// Define a simple User summary type for notes
export type UserSummary = {
  id: string;
  name: string;
  avatar?: string | null; // Optional avatar URL
};

// Define the NoteType enum based on usage in customer-notes-block.tsx
export enum NoteType {
  INTERNAL = 'INTERNAL',
  SHIPPING = 'SHIPPING',
  PRINTABLE = 'PRINTABLE',
}

export type CustomerNote = {
  id: string; // Assuming UUID
  customer_id: string; // Foreign key to Customer
  content: string;
  timestamp: string; // Renamed from created_at, assuming ISO string format
  user: UserSummary; // Replaced created_by with user object
  noteType: NoteType; // Add the type field here
};

// Enum for Customer Inactivation Reasons
export enum InactiveReason {
  NoOrders = 'NO_ORDERS',
  BadPayment = 'BAD_PAYMENT',
  CustomerRequest = 'CUSTOMER_REQUEST',
  Competitor = 'COMPETITOR',
  OutOfBusiness = 'OUT_OF_BUSINESS',
  Other = 'OTHER',
}

// Type for Customer Documents
export type CustomerDocument = {
  id: string; // Assuming UUID
  customer_id: string; // Foreign key to Customer
  filename: string;
  file_type: string; // e.g., 'pdf', 'docx', 'jpg'
  size: number; // Size in bytes
  upload_date: string; // Or Date object
  url?: string | null; // Link to view/download (optional)
  created_by?: string | null;
}; 