import * as React from "react";
// import CustomerList from "@/components/customers/customer-list"; // Corrected path
import { CustomersView } from "@/components/customers/CustomersView"; // Import the new view component

export default function CustomersPage() {
  return (
    // Optional: Add padding or other layout wrappers if needed globally
    <main className="container mx-auto px-4  h-full py-1  overflow-hidden flex flex-col">
       <CustomersView /> {/* Render the new view component */}
    </main>
  );
} 