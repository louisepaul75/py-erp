import { Metadata } from 'next';
import React from 'react';
import { SupplierDashboard } from '@/components/suppliers/SupplierDashboard';

// Placeholder for the actual dashboard component we will build
const SupplierDashboardPlaceholder = () => (
  <div className="p-4 border rounded-lg shadow">
    <p>Supplier Dashboard will be displayed here.</p>
    <p>It will contain a data table with add, edit, and delete functionality.</p>
  </div>
);

export const metadata: Metadata = {
  title: 'Supplier Management',
  description: 'Manage business suppliers.',
};

export default function SuppliersPage() {
  // TODO: Add authentication checks if necessary at the page level,
  // or rely on layout/middleware configurations.

  return (
    // Using common layout classes, adjust if needed
    <div className="flex-1 space-y-4 p-4 pt-6 md:p-8">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Supplier Management</h2>
        {/* Add Button will go here eventually, likely passed to or managed by SupplierDashboard */}
      </div>
      {/* Replace placeholder with the actual component later */}
      <SupplierDashboard />
    </div>
  );
} 