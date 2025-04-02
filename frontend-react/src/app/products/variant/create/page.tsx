"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Product } from "@/components/types/product";
import { productApi } from "@/lib/products/api";
import VariantProductForm from "@/components/products/variant-product-form";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui";

export default function CreateVariantProductPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [parentProduct, setParentProduct] = useState<Product | null>(null);
  const [parentLoading, setParentLoading] = useState(false);
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const parentId = searchParams.get('parent');
  
  useEffect(() => {
    const fetchParentProduct = async () => {
      if (!parentId) {
        setError("Parent product ID is required");
        return;
      }
      
      setParentLoading(true);
      try {
        const product = await productApi.getProduct(parentId);
        setParentProduct(product);
      } catch (err: any) {
        console.error("Error fetching parent product:", err);
        setError(`Failed to load parent product: ${err.message || "Unknown error"}`);
      } finally {
        setParentLoading(false);
      }
    };
    
    fetchParentProduct();
  }, [parentId]);
  
  const handleCreateVariant = async (productData: Omit<Product, "id">) => {
    if (!parentId) {
      setError("Parent product ID is required");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Add parent_id to the variant data
      const variantData = {
        ...productData,
        parent_id: parentId,
      };
      
      const newVariant = await productApi.createProduct(variantData);
      router.push(`/products/variant/${newVariant.id}`);
    } catch (err: any) {
      console.error("Error creating variant:", err);
      setError(`Failed to create variant: ${err.message || "Unknown error"}`);
      setIsLoading(false);
    }
  };
  
  const handleCancel = () => {
    if (parentId) {
      router.push(`/products/parent/${parentId}`);
    } else {
      router.push('/products');
    }
  };
  
  if (parentLoading) {
    return (
      <div className="container mx-auto py-4 px-4 md:px-6">
        <Card>
          <CardContent className="p-4 flex justify-center items-center h-64">
            <p>Loading parent product...</p>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  if (!parentId || error) {
    return (
      <div className="container mx-auto py-4 px-4 md:px-6">
        <Card>
          <CardContent className="p-4 flex justify-center items-center h-64">
            <p className="text-red-500">{error || "Parent product ID is required"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-4 px-4 md:px-6">
      <div className="max-w-full mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>
              Create New Variant for {parentProduct?.name || `Product #${parentId}`}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <VariantProductForm 
              parentProduct={parentProduct}
              onSubmit={handleCreateVariant}
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