"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Product } from "@/components/types/product";
import { productApi } from "@/lib/products/api";
import ParentProductForm from "@/components/products/parent-product-form";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui";

export default function CreateParentProductPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  
  const handleCreateProduct = async (productData: Omit<Product, "id">) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const newProduct = await productApi.createProduct(productData);
      router.push(`/products/parent/${newProduct.id}`);
    } catch (err: any) {
      console.error("Error creating product:", err);
      setError(`Failed to create product: ${err.message || "Unknown error"}`);
      setIsLoading(false);
    }
  };
  
  const handleCancel = () => {
    router.push('/products');
  };
  
  return (
    <div className="container mx-auto py-4 px-4 md:px-6">
      <div className="max-w-full mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Create New Parent Product</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <ParentProductForm 
              onSubmit={handleCreateProduct}
              onCancel={handleCancel}
              isLoading={isLoading}
              error={error}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 