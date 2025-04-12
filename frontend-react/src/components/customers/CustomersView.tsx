"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { TwoPaneLayout } from '@/components/ui/TwoPaneLayout';
import CustomerList from '@/components/customers/customer-list'; // Assuming this path is correct
import CustomerDetailPanel from '@/components/customers/CustomerDetailPanel'; // We will create this next

export function CustomersView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Get initial customer ID from URL
  const initialCustomerIdParam = searchParams.get('customerId');
  const initialCustomerId = initialCustomerIdParam || null; // Use null if not present

  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(initialCustomerId);

  // Update URL when customer ID changes
  useEffect(() => {
    const currentParams = new URLSearchParams(searchParams);
    if (selectedCustomerId) {
      currentParams.set('customerId', selectedCustomerId);
    } else {
      currentParams.delete('customerId');
    }
    // Use replace to avoid adding history entries for selection changes
    router.replace(`${pathname}?${currentParams.toString()}`);

    // Optional: Add to last visited context if implemented
    // if (selectedCustomerId && customerDetailData) { addVisitedItem(...) }

  }, [selectedCustomerId, pathname, router, searchParams]);

  // Handle customer selection from the list
  const handleSelectCustomer = (id: string | number) => {
    const customerIdString = String(id); // Ensure it's a string for state/URL
    setSelectedCustomerId(customerIdString);
  };

  return (
    <TwoPaneLayout
      leftPaneContent={
        <CustomerList
          onSelectCustomer={handleSelectCustomer}
          selectedCustomerId={selectedCustomerId} // Pass selected ID for highlighting
        />
      }
      rightPaneContent={
        <CustomerDetailPanel customerId={selectedCustomerId} />
      }
      // leftPaneClassName="your-left-pane-classes" // Optional custom classes
      // rightPaneClassName="your-right-pane-classes" // Optional custom classes
    />
  );
} 