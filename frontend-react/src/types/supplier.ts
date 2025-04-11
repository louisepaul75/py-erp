export type Supplier = {
  id: number; // Assuming Django REST Framework uses integer IDs by default
  name: string;
  contactPerson: string | null; // Assuming these can be optional
  email: string | null;
  phone: string | null;
  address: string | null;
  taxId: string | null;
  accountingId: string | null;
  creditorId: string | null;
  notes: string | null;
  createdAt: string; // ISO 8601 date string
  updatedAt: string; // ISO 8601 date string
  syncedAt: string | null; // Added field for sync status timestamp
};

// Type for creating a new supplier (omitting id, createdAt, updatedAt)
export type NewSupplier = Omit<Supplier, 'id' | 'createdAt' | 'updatedAt' | 'syncedAt'>;

// Type for updating an existing supplier (all fields optional except id)
// Using Partial<Omit<...>> makes all fields optional. We add 'id' back as required.
export type UpdateSupplier = Partial<Omit<Supplier, 'id' | 'createdAt' | 'updatedAt' | 'syncedAt'>> & {
  id: number;
};

// Optional: Define a type for the API response structure if it's nested
// export type SupplierApiResponse = {
//   results: Supplier[];
//   count?: number;
//   next?: string | null;
//   previous?: string | null;
// } 