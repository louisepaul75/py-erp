// components/products/ProductDetailPane.tsx
import React, { useState, useEffect } from "react";
import { CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Edit, Save, X, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Product, Supplier, Variant } from "@/components/types/product";
import { ProductFormData, defaultProductData } from "@/components/products/types";
import { ProductDetailFormContent } from "./product-detail-form-content";
import { ProductVariantContent } from "./product-variant-content";
import { UseQueryResult } from "@tanstack/react-query";
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

interface ProductDetailPaneProps {
  selectedItemId: number | null;
  isEditingNew: boolean;
  productDetailQuery: UseQueryResult<
    Product & { suppliers?: Supplier[] },
    Error
  >;
  variantsQuery: UseQueryResult<Variant[], Error>;
  isMutating: boolean;
  onEdit: () => void;
  onCancelEdit: () => void;
  onSave: (data: ProductFormData) => void;
  router: AppRouterInstance;
}

export function ProductDetailPane({
  selectedItemId,
  isEditingNew,
  productDetailQuery,
  variantsQuery,
  isMutating,
  onEdit,
  onCancelEdit,
  onSave,
  router,
}: ProductDetailPaneProps) {
  const [detailViewMode, setDetailViewMode] = useState<"parent" | "variants">(
    "parent"
  );
  const [isEditing, setIsEditing] = useState(false);
  const [productFormData, setProductFormData] =
    useState<ProductFormData>(defaultProductData);
  const [apiError, setApiError] = useState<string | null>(null);

  // Sync form data when product details load
  useEffect(() => {
    if (productDetailQuery.isSuccess && productDetailQuery.data && !isEditing) {
      const data = productDetailQuery.data;
      setProductFormData({
        ...defaultProductData,
        ...data,
        name: data.name ?? "",
        sku: data.sku ?? "",
      });
      setApiError(null);
    } else if (productDetailQuery.isError) {
      setApiError(`Error loading details: ${productDetailQuery.error.message}`);
    }
  }, [
    productDetailQuery.data,
    productDetailQuery.isSuccess,
    productDetailQuery.isError,
    isEditing,
  ]);

  const handleEdit = () => {
    const currentData = productDetailQuery.data;
    if (!selectedItemId || !currentData) {
      alert("Cannot edit. No product selected or details not loaded.");
      return;
    }
    setProductFormData({
      ...defaultProductData,
      ...currentData,
      name: currentData.name ?? "",
      sku: currentData.sku ?? "",
    });
    setIsEditing(true);
    setApiError(null);
    onEdit();
  };

  const handleCancelEdit = () => {
    const currentData = productDetailQuery.data;
    setIsEditing(false);
    setApiError(null);
    if (isEditingNew) {
      setProductFormData(defaultProductData);
    } else if (selectedItemId && currentData) {
      setProductFormData({
        ...defaultProductData,
        ...currentData,
        name: currentData.name ?? "",
        sku: currentData.sku ?? "",
      });
    } else {
      setProductFormData(defaultProductData);
    }
    onCancelEdit();
  };

  const handleFormChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    let processedValue: string | number | null = value;
    if (type === "number") {
      processedValue = value === "" ? null : parseFloat(value);
      if (isNaN(processedValue as number)) {
        processedValue = null;
      }
    }
    setProductFormData((prev) => ({ ...prev, [name]: processedValue }));
  };

  const handleCheckboxChange = (
    field: keyof ProductFormData,
    checked: boolean | "indeterminate"
  ) => {
    if (typeof checked === "boolean") {
      setProductFormData((prev) => ({ ...prev, [field]: checked }));
    }
  };

  const handleSupplierChange = (supplierIdString: string) => {
    let selectedSupplier: Supplier | null = null;
    const availableSuppliers = productDetailQuery.data?.suppliers;
    if (supplierIdString && supplierIdString !== "none" && availableSuppliers) {
      selectedSupplier =
        availableSuppliers.find(
          (s: Supplier) => String(s.id) === supplierIdString
        ) ?? null;
    }
    setProductFormData((prev) => ({
      ...prev,
      supplier: selectedSupplier,
    }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    if (!productFormData.name || !productFormData.sku) {
      setApiError("Product Name and SKU are required.");
      return;
    }

    if (!isEditingNew && selectedItemId === null) {
      setApiError("Cannot update: Product ID is missing.");
      return;
    }

    const dataToSave: ProductFormData = {
      ...productFormData,
      name: productFormData.name,
      sku: productFormData.sku,
      description: productFormData.description ?? "",
    };
    onSave(dataToSave);
    setIsEditing(false);
  };

  const showDetailPlaceholder = !isEditingNew && selectedItemId === null;
  const showDetailLoading = !isEditingNew && productDetailQuery.isLoading;
  const displayData =
    !isEditing && productDetailQuery.data
      ? productDetailQuery.data
      : productFormData;
  const canRenderDetails =
    !showDetailPlaceholder &&
    !showDetailLoading &&
    (displayData || isEditingNew);

  return (
    <>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>
          {isEditingNew ? "Create New Product" : "Product Details"}
        </CardTitle>
        <div className="flex gap-2">
          {!isEditing && selectedItemId && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleEdit}
              disabled={productDetailQuery.isLoading}
            >
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
          )}
          {isEditing && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancelEdit}
                disabled={isMutating}
              >
                <X className="mr-2 h-4 w-4" />
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleSave}
                disabled={
                  isMutating || !productFormData.name || !productFormData.sku
                }
              >
                {isMutating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save
                  </>
                )}
              </Button>
            </>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto">
        {showDetailPlaceholder && (
          <p className="text-muted-foreground flex items-center justify-center h-full">
            Select a product or create a new one.
          </p>
        )}
        {showDetailLoading && (
          <p className="text-muted-foreground flex items-center justify-center h-full">
            Loading details for item {selectedItemId}...
          </p>
        )}
        {apiError && (
          <Alert variant="destructive" className="my-4">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{apiError}</AlertDescription>
          </Alert>
        )}

        {canRenderDetails && (
          <>
            {!isEditingNew && selectedItemId && displayData ? (
              <Tabs
                defaultValue="parent"
                value={detailViewMode}
                onValueChange={(value) =>
                  setDetailViewMode(value as "parent" | "variants")
                }
                className="p-4 h-full flex flex-col"
              >
                <TabsList className="mb-4">
                  <TabsTrigger value="parent">Parent Details</TabsTrigger>
                  <TabsTrigger
                    value="variants"
                    disabled={!selectedItemId || variantsQuery.isLoading}
                  >
                    Variants{" "}
                    {selectedItemId && variantsQuery.isLoading
                      ? " (Loading...)"
                      : selectedItemId && variantsQuery.isError
                      ? " (Error)"
                      : selectedItemId && variantsQuery.data?.length
                      ? ` (${variantsQuery.data.length})`
                      : " (0)"}
                  </TabsTrigger>
                </TabsList>
                <TabsContent
                  value="parent"
                  className="flex-grow overflow-y-auto space-y-4"
                >
                  <ProductDetailFormContent
                    productData={productFormData}
                    isEditing={isEditing}
                    handleFormChange={handleFormChange}
                    handleCheckboxChange={handleCheckboxChange}
                    handleSupplierChange={handleSupplierChange}
                    isMutating={isMutating}
                    fetchedProduct={productDetailQuery.data}
                    suppliers={productDetailQuery.data?.suppliers ?? []}
                    router={router}
                  />
                </TabsContent>
                <TabsContent
                  value="variants"
                  className="flex-grow overflow-y-auto space-y-4"
                >
                  <ProductVariantContent
                    selectedItemId={selectedItemId}
                    variantsQuery={variantsQuery}
                  />
                </TabsContent>
              </Tabs>
            ) : (
              <div className="p-4 space-y-4 flex-grow overflow-y-auto">
                <ProductDetailFormContent
                  productData={productFormData}
                  isEditing={isEditing}
                  handleFormChange={handleFormChange}
                  handleCheckboxChange={handleCheckboxChange}
                  handleSupplierChange={handleSupplierChange}
                  isMutating={isMutating}
                  fetchedProduct={null}
                  suppliers={[]}
                  router={router}
                />
              </div>
            )}
          </>
        )}
      </CardContent>
    </>
  );
}
