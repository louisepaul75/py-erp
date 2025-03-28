import React from "react";
import { InventoryManagement } from "@/components/ui/products";

interface PageProps {
  params: {
    id: string;
  };
}

export default function ProductParentPage({ params }: PageProps) {
  return <InventoryManagement initialParentId={params.id} />;
} 