import React from 'react';
import CustomerForm from '@/components/customers/customer-form';
// import Breadcrumbs from '@/components/ui/dashboard/breadcrumbs';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Create Customer',
};

export default function Page() {
  return (
    <main>
      {/* <Breadcrumbs
        breadcrumbs={[
          { label: 'Customers', href: '/dashboard/customers' },
          {
            label: 'Create Customer',
            href: '/dashboard/customers/new',
            active: true,
          },
        ]}
      /> */}
      <CustomerForm mode="create" />
    </main>
  );
} 