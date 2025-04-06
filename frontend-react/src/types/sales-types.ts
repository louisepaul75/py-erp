export interface Customer {
  id: number; // Or string, depending on your API
  customer_number: string;
  name: string;
  customer_group: string;
  vat_id: string;
  // Add other relevant fields from the Customer model as needed
  // e.g., email, phone, delivery_block, created_at
}

// Add other sales-related types here if necessary 