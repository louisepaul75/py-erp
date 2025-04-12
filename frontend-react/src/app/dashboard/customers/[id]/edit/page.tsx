// import { fetchCustomerById } from '@/lib/data'; // Remove mock function import
import { fetchCustomerByIdAPI } from '@/lib/api'; // Import API function
import CustomerForm from '@/components/customers/customer-form'; // Corrected path
import Breadcrumbs from '@/components/ui/dashboard/breadcrumbs'; // Corrected path
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Edit Customer',
};

export default async function Page({ params }: { params: { id: string } }) {
  const id = params.id;
  // const customer = await fetchCustomerById(id); // Remove mock call
  const customer = await fetchCustomerByIdAPI(id); // Use API call

  if (!customer) {
    notFound(); // Handle case where customer is not found
  }

  return (
    <main>
      <Breadcrumbs
        breadcrumbs={[
          { label: 'Customers', href: '/dashboard/customers' },
          {
            label: 'Edit Customer',
            href: `/dashboard/customers/${id}/edit`,
            active: true,
          },
        ]}
      />
      <CustomerForm customer={customer} mode="edit" /> {/* Pass data and mode */}
    </main>
  );
} 