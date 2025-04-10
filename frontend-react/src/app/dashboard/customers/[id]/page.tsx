import React, { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { fetchCustomerById } from '@/lib/data'; // Assume this function exists/will be created
import CustomerHeader from '@/components/ui/dashboard/customers/CustomerHeader'; // Assume exists
import CustomerGeneralInfoCard from '@/components/ui/dashboard/customers/CustomerGeneralInfoCard'; // Assume exists
import CustomerContactPersonsCard from '@/components/ui/dashboard/customers/CustomerContactPersonsCard';
import CustomerContactInfosCard from '@/components/ui/dashboard/customers/CustomerContactInfosCard';
import CustomerNotesCard from '@/components/ui/dashboard/customers/CustomerNotesCard';
import { Skeleton } from '@/components/ui/skeleton'; // For loading states
import CustomerDocumentsCard from '@/components/ui/dashboard/customers/CustomerDocumentsCard'; // Import the new component

// Placeholders for other tabs
// const CustomerNotesCard = () => <div>Notes Tab Content (Placeholder)</div>; // Remove placeholder
// const CustomerDocumentsCard = () => <div>Documents Tab Content (Placeholder)</div>; // Remove placeholder

export default async function CustomerDetailPage({ params }: { params: { id: string } }) {
  const customerId = params.id;

  // Fetch customer data using the (currently mock) data function
  const customer = await fetchCustomerById(customerId);

  if (!customer) {
    notFound(); // Render 404 if customer not found
  }

  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      {/* Pass the fetched customer data to the header */}
      <CustomerHeader customer={customer} />

      <Tabs defaultValue="general" className="mt-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="contacts">Contacts</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        {/* General Tab */}
        <TabsContent value="general" className="mt-4">
          <Suspense fallback={<Skeleton className="h-40 w-full" />}>
            {/* Assume this component takes the customer object */}
            <CustomerGeneralInfoCard customer={customer} />
          </Suspense>
        </TabsContent>

        {/* Contacts Tab */}
        <TabsContent value="contacts" className="mt-4 space-y-4">
          <Suspense fallback={<Skeleton className="h-40 w-full" />}>
            <CustomerContactPersonsCard contactPersons={customer.contact_persons || []} />
          </Suspense>
          <Suspense fallback={<Skeleton className="h-40 w-full" />}>
            <CustomerContactInfosCard contactInfos={customer.contact_infos || []} />
          </Suspense>
        </TabsContent>

        {/* Notes Tab */}
        <TabsContent value="notes" className="mt-4">
          <Suspense fallback={<Skeleton className="h-40 w-full" />}>
             {/* Use the actual component and pass notes data */}
             <CustomerNotesCard activity_notes={customer.activity_notes || []} />
           </Suspense>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents" className="mt-4">
          <Suspense fallback={<Skeleton className="h-60 w-full" />}> {/* Adjusted skeleton height */}
            {/* Use the actual component and pass documents data */}
            <CustomerDocumentsCard documents={customer.documents || []} />
          </Suspense>
        </TabsContent>
      </Tabs>
    </div>
  );
} 