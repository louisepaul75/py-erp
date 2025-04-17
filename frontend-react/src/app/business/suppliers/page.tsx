'use client';

import React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { SupplierDashboard } from '@/components/suppliers/SupplierDashboard';
// Import Tabs components
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Simple placeholder component for future dashboards
const PlaceholderDashboard = ({ title }: { title: string }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      <CardDescription>This section is under construction.</CardDescription>
    </CardHeader>
    <CardContent>
      <p>Content for {title.toLowerCase()} will be displayed here.</p>
    </CardContent>
  </Card>
);

export default function SuppliersPage() {
  // TODO: Add authentication checks if necessary at the page level,
  // or rely on layout/middleware configurations.

  return (
    <div className="space-y-6 h-full overflow-auto">
      {/* You might want a page header here similar to the draft's PageHeader */}
      {/* <PageHeader title="Business Management" description="Manage suppliers, purchases, and documents" /> */}
      <h1 className="text-2xl font-semibold">Suppliers</h1>

      {/* Wrap content in Tabs */}
      <Tabs defaultValue="suppliers" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-6">
          <TabsTrigger value="suppliers">Suppliers</TabsTrigger>
          <TabsTrigger value="purchases">Purchases</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        <TabsContent value="suppliers">
          <SupplierDashboard />
        </TabsContent>

        <TabsContent value="purchases">
          {/* Placeholder for Purchases Dashboard */}
          <PlaceholderDashboard title="Purchases" />
        </TabsContent>

        <TabsContent value="documents">
          {/* Placeholder for Documents Dashboard */}
          <PlaceholderDashboard title="Documents" />
        </TabsContent>
      </Tabs>
    </div>
  );
} 