import React, { Suspense } from 'react';
import Link from 'next/link';
// import { fetchCustomers } from '@/lib/data'; // Remove mock function import
import { fetchCustomersAPI } from '@/lib/api'; // Import API function
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { PlusIcon, EyeIcon } from 'lucide-react'; // Icons for buttons
import { Skeleton } from '@/components/ui/skeleton'; // For loading state
// import { Breadcrumbs } from '@/components/ui/dashboard/breadcrumbs'; // Assuming breadcrumbs exist

// Helper function to format address for display in the table
const formatAddressLine = (address: any): string => {
  if (!address) return 'N/A';
  return [
    address.street,
    address.city,
    address.postal_code,
    address.country,
  ].filter(Boolean).join(', ');
};

// --- Customer Table Component (or include directly in page) ---
async function CustomersTable() {
  // const customers = await fetchCustomers(); // Remove mock call
  const customers = await fetchCustomersAPI(); // Use API call

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead className="hidden md:table-cell">Email</TableHead>
          <TableHead className="hidden lg:table-cell">Phone</TableHead>
          <TableHead className="hidden xl:table-cell">Billing Address</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {customers.length === 0 ? (
          <TableRow>
            <TableCell colSpan={5} className="h-24 text-center">
              No customers found.
            </TableCell>
          </TableRow>
        ) : (
          customers.map((customer) => (
            <TableRow key={customer.id}>
              <TableCell className="font-medium">{customer.name}</TableCell>
              <TableCell className="hidden md:table-cell">{customer.email || 'N/A'}</TableCell>
              <TableCell className="hidden lg:table-cell">{customer.phone || 'N/A'}</TableCell>
              <TableCell className="hidden xl:table-cell">{formatAddressLine(customer.billing_address)}</TableCell>
              <TableCell className="text-right">
                <Button asChild variant="ghost" size="sm">
                  <Link href={`/dashboard/customers/${customer.id}`}>
                    <EyeIcon className="mr-2 h-4 w-4" /> View
                  </Link>
                </Button>
                {/* TODO: Add Edit/Delete actions later */}
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
}

// --- Main Page Component ---
export default function CustomersPage() {
  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      {/* <Breadcrumbs
        breadcrumbs={[
          { label: 'Customers', href: '/dashboard/customers', active: true },
        ]}
      /> */}

      <div className="flex justify-between items-center mt-4 mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Customers</h1>
        <Button asChild>
          <Link href="/dashboard/customers/new">
            <PlusIcon className="mr-2 h-4 w-4" /> Create Customer
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Customer List</CardTitle>
          <CardDescription>Manage your customer accounts.</CardDescription>
        </CardHeader>
        <CardContent>
          <Suspense fallback={<CustomersTableSkeleton />}>
            <CustomersTable />
          </Suspense>
        </CardContent>
      </Card>
    </div>
  );
}

// --- Skeleton Loading Component ---
function CustomersTableSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-8 w-3/5" />
      <Skeleton className="h-8 w-4/5" />
      <Skeleton className="h-8 w-2/5" />
      <Skeleton className="h-8 w-full" />
      <Skeleton className="h-8 w-3/4" />
    </div>
  );
} 