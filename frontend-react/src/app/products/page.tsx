import React from 'react';
import { ProductsView } from '@/components/products/ProductsView';

export default function ProductsPage() {
  return (
    <div className="container mx-auto p-4 h-[calc(100vh-4rem)]">
      {/* We might add page-level titles or controls here later */}
      <ProductsView />
    </div>
  );
}
