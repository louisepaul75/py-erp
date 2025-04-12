'use client'; // Required for AlertDialog

import React, { useState } from 'react';
import { Customer } from '@/lib/definitions';
import { Button } from '@/components/ui/button';
import { MailIcon, PhoneIcon, EditIcon, Trash2Icon } from 'lucide-react'; // Or your icon library
import Link from 'next/link'; // Import Link
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { deleteCustomerAPI } from '@/lib/api'; // Import API function
import { useRouter } from 'next/navigation'; // To redirect after delete

interface CustomerHeaderProps {
  customer: Customer; // Use Partial<Customer> if data might be incomplete initially
}

export default function CustomerHeader({ customer }: CustomerHeaderProps) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    setIsDeleting(true);
    setError(null);
    try {
      await deleteCustomerAPI(customer.id); // Call the actual API function
      
      // Redirect to customer list page after successful deletion
      router.push('/dashboard/customers');
    } catch (err: any) {
      console.error("Delete failed:", err);
      setError(err.message || 'Failed to delete customer. Please try again.');
      setIsDeleting(false);
    }
    // No need to set isDeleting to false on success due to redirect
  };

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
        {/* Link to the edit page */}
        <Button variant="outline" size="sm" asChild> {/* Use asChild to render Link inside Button */}
          <Link href={`/dashboard/customers/${customer.id}/edit`}>
            <EditIcon className="mr-2 h-4 w-4" /> Edit
          </Link>
        </Button>
        {/* Delete Button with Confirmation Dialog */}
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="destructive" size="sm" disabled={isDeleting}>
              <Trash2Icon className="mr-2 h-4 w-4" /> 
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete the customer
                "<strong>{customer.name}</strong>" and remove their data from our servers.
              </AlertDialogDescription>
            </AlertDialogHeader>
            {error && <p className="text-sm text-red-500 mt-2">{error}</p>} 
            <AlertDialogFooter>
              <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete} disabled={isDeleting}>
                {isDeleting ? 'Deleting...' : 'Continue'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
} 