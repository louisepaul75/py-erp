// components/products/ProductVariantContent.tsx
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { PlusCircle } from "lucide-react";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import Image from "next/image";
import {
  UseQueryResult,
  useQueryClient,
  useMutation,
} from "@tanstack/react-query";
import { Variant } from "@/components/types/product";
import { productApi } from "@/lib/products/api";

interface ProductVariantContentProps {
  selectedItemId: number | null;
  variantsQuery: UseQueryResult<Variant[], Error>;
}

export function ProductVariantContent({
  selectedItemId,
  variantsQuery,
}: ProductVariantContentProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newVariantData, setNewVariantData] = useState<{
    variant_code: string;
    name: string;
    is_active: boolean;
  }>({
    variant_code: "",
    name: "",
    is_active: true,
  });
  const [createError, setCreateError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const createVariantMutation = useMutation<
    Variant,
    Error,
    Partial<Variant> & { parent_id: number }
  >({
    mutationFn: async (data) => {
      if (!selectedItemId) throw new Error("Parent product ID is missing");
      // Add required Product fields for creating a variant
      return productApi.createProduct({
        ...data,
        parent_id: selectedItemId,
        // Add required fields from Product type
        is_discontinued: false,
        variants_count: 0,
        // Ensure required fields are provided
        sku: data.sku || `${data.variant_code}`,
        is_active: data.is_active !== undefined ? data.is_active : true,
        name: data.name || `Variant ${data.variant_code}`,
      }) as Promise<Variant>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["productVariants", selectedItemId],
      });
      setShowCreateForm(false);
      setNewVariantData({ variant_code: "", name: "", is_active: true });
      setCreateError(null);
    },
    onError: (error) => {
      setCreateError(`Failed to create variant: ${error.message}`);
    },
  });

  const handleCreateVariantSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newVariantData.variant_code || !newVariantData.name) {
      setCreateError("Variant Code and Name are required.");
      return;
    }
    if (!selectedItemId) {
      setCreateError("Cannot create variant: Parent Product ID is missing.");
      return;
    }
    setCreateError(null);
    createVariantMutation.mutate({
      ...newVariantData,
      parent_id: selectedItemId,
    });
  };

  const handleVariantFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewVariantData((prev) => ({ ...prev, [name]: value }));
  };

  const variants = variantsQuery.data ?? [];
  const totalVariants = variants.length;

  if (variantsQuery.isLoading) {
    return <p>Loading variants...</p>;
  }

  if (variantsQuery.isError) {
    return (
      <p className="text-red-500">
        Error loading variants: {variantsQuery.error.message}
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">
          Product Variants ({totalVariants})
        </h3>
        <Button
          size="sm"
          onClick={() => setShowCreateForm(!showCreateForm)}
          variant="outline"
        >
          <PlusCircle className="mr-2 h-4 w-4" />
          {showCreateForm ? "Cancel" : "New Variant"}
        </Button>
      </div>

      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Variant</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateVariantSubmit} className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="variant_code">
                  Variant Code <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="variant_code"
                  name="variant_code"
                  value={newVariantData.variant_code}
                  onChange={handleVariantFormChange}
                  required
                  disabled={createVariantMutation.isPending}
                  placeholder="e.g., RED, XL"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="variant_name">
                  Variant Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="variant_name"
                  name="name"
                  value={newVariantData.name}
                  onChange={handleVariantFormChange}
                  required
                  disabled={createVariantMutation.isPending}
                  placeholder="e.g., Product Name - Red"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="variant_is_active"
                  checked={newVariantData.is_active}
                  onCheckedChange={(checked) =>
                    setNewVariantData((prev) => ({
                      ...prev,
                      is_active: checked === true,
                    }))
                  }
                  disabled={createVariantMutation.isPending}
                />
                <Label htmlFor="variant_is_active">Active</Label>
              </div>
              {createError && (
                <p className="text-sm text-red-500">{createError}</p>
              )}
              <div>
                <Button
                  type="submit"
                  size="sm"
                  disabled={createVariantMutation.isPending}
                >
                  {createVariantMutation.isPending
                    ? "Creating..."
                    : "Create Variant"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {variants.length > 0 ? (
        <Table>
          <TableCaption>
            List of variants for product ID {selectedItemId}
          </TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Image</TableHead>
              <TableHead>SKU</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Variant Code</TableHead>
              <TableHead>Active</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {variants.map((variant: Variant) => (
              <TableRow key={variant.id}>
                <TableCell>
                  {variant.images && variant.images.length > 0 ? (
                    <Image
                      src={
                        variant.images[0].thumbnail_url ||
                        variant.images[0].image_url
                      }
                      alt={variant.name || variant.sku}
                      width={40}
                      height={40}
                      className="rounded object-cover"
                    />
                  ) : (
                    <></>
                  )}
                </TableCell>
                <TableCell>{variant.sku}</TableCell>
                <TableCell>{variant.name}</TableCell>
                <TableCell>{variant.variant_code}</TableCell>
                <TableCell>{variant.is_active ? "Yes" : "No"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p className="text-muted-foreground text-center p-4">
          No variants found for this product.
        </p>
      )}
    </div>
  );
}
