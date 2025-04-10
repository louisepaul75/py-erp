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
};

export type CustomerNote = {
  id: string; // Assuming UUID
  customer_id: string; // Foreign key to Customer
  content: string;
  created_at: string; // Or Date object, depending on API/preference
  created_by?: string | null; // Optional: User ID or name who created the note
}; 