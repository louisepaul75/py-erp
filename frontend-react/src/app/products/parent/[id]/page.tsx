import React from "react";
import { InventoryManagement } from "@/components/ui/products";

interface PageProps {
  params: {
    id: string;
  };
}

export default async function ProductParentPage({ params }: PageProps) {
  try {
    const unwrappedParams = React.use(params);
    return <InventoryManagement initialParentId={unwrappedParams.id} />;
  } catch (error) {
    console.error("Error in ProductParentPage:", error);
    // Render a fallback UI
    return (
      <div className="p-4">
        <h2 className="text-xl font-semibold text-red-600">Failed to load product</h2>
        <p>There was an error loading the product information. Please try again later.</p>
      </div>
    );
  }
} 