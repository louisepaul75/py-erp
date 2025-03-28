"use client";

import React from "react";
import { InventoryManagement } from "@/components/ui/products";

export default function ProductVariantPage({ params }: { params: { id: string } }) {
  const unwrappedParams = React.use(params);
  return <InventoryManagement initialVariantId={unwrappedParams.id} />;
} 