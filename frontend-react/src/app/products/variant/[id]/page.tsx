"use client";

import { InventoryManagement } from "@/components/ui/products";

export default function ProductVariantPage({ params }: { params: { id: string } }) {
  return <InventoryManagement initialVariantId={params.id} />;
} 