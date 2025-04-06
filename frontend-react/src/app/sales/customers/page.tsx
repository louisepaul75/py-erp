import CustomerList from "@/components/customers/customer-list"; // Corrected path

export default function CustomersPage() {
  return (
    // Optional: Add padding or other layout wrappers if needed globally
    <main className="container mx-auto px-4 py-8">
       <CustomerList />
    </main>
  );
} 