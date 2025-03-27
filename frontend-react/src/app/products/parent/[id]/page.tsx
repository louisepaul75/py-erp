"use client";

import { InventoryManagement } from "@/components/ui/products";

export default function ProductParentPage({ params }: { params: { id: string } }) {
  return <InventoryManagement initialParentId={params.id} />;
} 