import React from 'react';
import { Customer } from '@/lib/definitions';
import { Button } from '@/components/ui/button';
import { MailIcon, PhoneIcon, EditIcon } from 'lucide-react'; // Or your icon library

interface CustomerHeaderProps {
  customer: Customer; // Use Partial<Customer> if data might be incomplete initially
}

export default function CustomerHeader({ customer }: CustomerHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between space-y-4 md:space-y-0 border-b pb-4">
      <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
        {customer.name || 'Customer Details'}
      </h1>
      <div className="flex space-x-2">
        {/* TODO: Implement functionality for these buttons */}
        <Button variant="outline" size="sm" disabled>
          <MailIcon className="mr-2 h-4 w-4" /> Email
        </Button>
        <Button variant="outline" size="sm" disabled>
          <PhoneIcon className="mr-2 h-4 w-4" /> Call
        </Button>
        <Button variant="outline" size="sm" disabled> {/* Or link to edit page */}
          <EditIcon className="mr-2 h-4 w-4" /> Edit
        </Button>
      </div>
    </div>
  );
} 