// Placeholder for data fetching functions

import { Customer, FullCustomerProfile } from './definitions';

// Example structure - replace with actual API calls
export async function fetchCustomerById(id: string): Promise<FullCustomerProfile | null> {
  console.log(`Fetching customer data for id: ${id}`);
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));

  // Return mock data matching the structure used in the page for now
  // In a real app, this would fetch from your backend API
  if (id) { // Simulate finding a customer
    const mockCustomer: FullCustomerProfile = {
        id: id,
        name: `Customer ${id.substring(0, 4)} Fetched Name`,
        contact_persons: [{ id: 'cp1', customer_id: id, name: 'John Fetched', email: 'john.fetched@example.com', position: 'Manager' }],
        contact_infos: [
          { id: 'ci1', customer_id: id, type: 'email' as const, value: 'fetched@example.com', description: 'Fetched Office' },
          { id: 'ci2', customer_id: id, type: 'phone' as const, value: '555-FETCH', description: 'Fetched Support' },
        ],
        billing_address: {
          street: '123 Fetched St',
          city: 'FetchedTown',
          postal_code: '54321',
          country: 'FCH',
        },
        tax_id: 'FETCH-TAX-ID',
        website: 'https://fetched.example.com',
        email: 'customer.fetched@example.com',
        phone: '555-CUST-FET',
        // Add other fields based on FullCustomerProfile
        activity_notes: [
          { id: 'note1', customer_id: id, content: 'Called customer on 2024-03-10 regarding invoice #123.', created_at: '2024-03-10T10:30:00Z', created_by: 'Admin User' },
          { id: 'note2', customer_id: id, content: 'Met with CEO, discussed expansion plans.', created_at: '2024-03-15T14:00:00Z', created_by: 'Sales Rep' },
        ],
        documents: [ // Added mock documents
          { id: 'doc1', customer_id: id, filename: 'Contract_Agreement.pdf', file_type: 'pdf', size: 1024 * 500, upload_date: '2024-01-15T09:00:00Z', created_by: 'Legal Team', url: '/documents/contract_agreement.pdf' },
          { id: 'doc2', customer_id: id, filename: 'Project_Proposal_v2.docx', file_type: 'docx', size: 1024 * 1200, upload_date: '2024-02-20T11:30:00Z', created_by: 'Sales Rep', url: '/documents/proposal_v2.docx' },
          { id: 'doc3', customer_id: id, filename: 'Initial_Invoice.pdf', file_type: 'pdf', size: 1024 * 150, upload_date: '2024-03-01T16:45:00Z', created_by: 'Accounting', url: '/documents/invoice_initial.pdf' },
        ]
      };
      return mockCustomer;
  } else {
      return null; // Simulate not found
  }

}

// Add other data fetching functions as needed (e.g., fetchCustomers, fetchContacts, etc.)

// Add a function to fetch multiple customers (mock)
export async function fetchCustomers(): Promise<Customer[]> { // Using base Customer for list view
  console.log('Fetching list of customers...');
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 300));

  // Return a list of basic customer data
  const mockCustomers: Customer[] = [
    {
      id: 'cus_1',
      name: 'Mock Customer Alpha',
      email: 'alpha@example.com',
      phone: '555-1111',
      billing_address: { street: '1 Alpha St', city: 'Alphaville', postal_code: '11111', country: 'ALP' },
    },
    {
      id: 'cus_2',
      name: 'Mock Industries Beta',
      email: 'contact@beta.inc',
      phone: '555-2222',
      tax_id: 'BETA-TAX',
      billing_address: { street: '2 Beta Blvd', city: 'Betatown', postal_code: '22222', country: 'BTA' },
    },
    {
      id: 'cus_3',
      name: 'Gamma Services Ltd.',
      email: 'info@gamma.ltd',
      phone: '555-3333',
      website: 'https://gamma.ltd',
      billing_address: { street: '3 Gamma Grv', city: 'Gammapolis', postal_code: '33333', country: 'GAM' },
    },
     {
      id: 'cus_4',
      name: 'Delta Supplies',
      email: 'sales@delta.supplies',
      phone: '555-4444',
      billing_address: { street: '4 Delta Dr', city: 'Deltaport', postal_code: '44444', country: 'DEL' },
    },
  ];
  return mockCustomers;
}
