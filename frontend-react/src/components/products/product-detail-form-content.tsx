// components/products/ProductDetailFormContent.tsx
import React from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Product, Supplier } from "@/components/types/product";
import { ProductFormData } from "@/components/products/types";
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

interface ProductDetailFormContentProps {
  productData: ProductFormData;
  isEditing: boolean;
  handleFormChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  handleCheckboxChange: (
    field: keyof ProductFormData,
    checked: boolean | "indeterminate"
  ) => void;
  handleSupplierChange: (supplierIdString: string) => void;
  isMutating: boolean;
  fetchedProduct?: Product | null;
  suppliers?: Supplier[];
  router: AppRouterInstance;
}

export function ProductDetailFormContent({
  productData,
  isEditing,
  handleFormChange,
  handleCheckboxChange,
  handleSupplierChange,
  isMutating,
  fetchedProduct,
  suppliers = [],
  router,
}: ProductDetailFormContentProps) {
  const selectValue = productData.supplier?.id?.toString() ?? "none";

  return (
    <form onSubmit={(e) => e.preventDefault()} className="space-y-6">
      {!isEditing && fetchedProduct?.primary_image && (
        <div className="mb-4">
          <img
            src={
              fetchedProduct.primary_image.thumbnail_url ||
              fetchedProduct.primary_image.image_url
            }
            alt={fetchedProduct.name}
            className="max-w-xs max-h-48 object-contain rounded-md border"
          />
        </div>
      )}

      <div className="space-y-1">
        <Label
          htmlFor="product-name"
          className={isEditing ? "" : "text-muted-foreground"}
        >
          Product Name <span className="text-red-500">*</span>
        </Label>
        {isEditing ? (
          <Input
            id="product-name"
            name="name"
            placeholder="e.g., Basic Widget"
            value={productData.name ?? ""}
            onChange={handleFormChange}
            required
            disabled={isMutating}
          />
        ) : (
          <h2 className="text-2xl font-bold text-primary">
            {fetchedProduct?.name || "-"}
          </h2>
        )}
      </div>

      <h3 className="text-lg font-semibold border-b pb-1 mb-3">Core Details</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-x-4 gap-y-4 text-sm">
        <div className="space-y-1">
          <Label
            htmlFor="product-sku"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            SKU <span className="text-red-500">*</span>
          </Label>
          {isEditing ? (
            <Input
              id="product-sku"
              name="sku"
              placeholder="e.g., WID-001"
              value={productData.sku ?? ""}
              onChange={handleFormChange}
              required
              disabled={isMutating}
            />
          ) : (
            <p>{fetchedProduct?.sku || "-"}</p>
          )}
        </div>

        <div className="space-y-1">
          <Label
            htmlFor="product-legacy-sku"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Legacy SKU
          </Label>
          {isEditing ? (
            <Input
              id="product-legacy-sku"
              name="legacy_base_sku"
              placeholder="Optional legacy SKU"
              value={productData.legacy_base_sku ?? ""}
              onChange={handleFormChange}
              disabled={isMutating}
            />
          ) : (
            <p>{fetchedProduct?.legacy_base_sku || "N/A"}</p>
          )}
        </div>

        <div className="space-y-1">
          <Label
            htmlFor="product-category"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Category
          </Label>
          {isEditing ? (
            <Input
              id="product-category"
              name="category"
              placeholder="e.g., Widgets"
              value={productData.category ?? ""}
              onChange={handleFormChange}
              disabled={isMutating}
            />
          ) : (
            <p>{fetchedProduct?.category || "N/A"}</p>
          )}
        </div>

        <div className="space-y-1">
          {isEditing ? (
            <Select
              value={selectValue}
              onValueChange={handleSupplierChange}
              disabled={isMutating}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select Supplier" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">-- None --</SelectItem>
                {suppliers.map((supplier) => (
                  <SelectItem key={supplier.id} value={supplier.id.toString()}>
                    {supplier.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : fetchedProduct?.supplier ? (
            <Button
              variant="outline"
              size="sm"
              className="p-1 h-auto justify-start"
              onClick={() =>
                router.push(
                  `/business/suppliers?supplierId=${fetchedProduct.supplier?.id}`
                )
              }
              title={`View details for ${fetchedProduct.supplier.name}`}
            >
              {fetchedProduct.supplier.name}
            </Button>
          ) : (
            <p>N/A</p>
          )}
        </div>

        <div className="space-y-1">
          <Label
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Status
          </Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox
                id="product-active"
                checked={productData.is_active ?? false}
                onCheckedChange={(checked) =>
                  handleCheckboxChange("is_active", checked)
                }
                disabled={isMutating}
              />
              <Label htmlFor="product-active" className="text-sm font-medium">
                Active
              </Label>
            </div>
          ) : (
            <Badge
              variant={fetchedProduct?.is_active ? "default" : "secondary"}
            >
              {fetchedProduct?.is_active ? "Active" : "Inactive"}
            </Badge>
          )}
        </div>

        <div className="space-y-1">
          <Label
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Lifecycle
          </Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox
                id="product-discontinued"
                checked={productData.is_discontinued ?? false}
                onCheckedChange={(checked) =>
                  handleCheckboxChange("is_discontinued", checked)
                }
                disabled={isMutating}
              />
              <Label
                htmlFor="product-discontinued"
                className="text-sm font-medium"
              >
                Discontinued
              </Label>
            </div>
          ) : (
            <Badge
              variant={
                fetchedProduct?.is_discontinued ? "destructive" : "secondary"
              }
            >
              {fetchedProduct?.is_discontinued
                ? "Discontinued"
                : "Active Lifecycle"}
            </Badge>
          )}
        </div>

        <div className="space-y-1">
          <Label
            htmlFor="product-release-date"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Release Date
          </Label>
          {isEditing ? (
            <Input
              id="product-release-date"
              name="release_date"
              type="date"
              value={productData.release_date ?? ""}
              onChange={handleFormChange}
              disabled={isMutating}
            />
          ) : (
            <p>
              {fetchedProduct?.release_date
                ? new Date(fetchedProduct.release_date).toLocaleDateString()
                : "N/A"}
            </p>
          )}
        </div>

        <div className="space-y-1">
          <Label className="font-medium text-muted-foreground">Variants</Label>
          <p>{fetchedProduct?.variants_count ?? 0}</p>
        </div>
      </div>

      <h3 className="text-lg font-semibold border-b pb-1 mb-3 pt-4">
        Dimensions & Weight
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-x-4 gap-y-4 text-sm">
        <div className="space-y-1">
          <Label
            htmlFor="product-height"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Height (mm)
          </Label>
          {isEditing ? (
            <Input
              id="product-height"
              name="height_mm"
              type="number"
              placeholder="e.g., 100"
              value={productData.height_mm ?? ""}
              onChange={handleFormChange}
              disabled={isMutating}
            />
          ) : (
            <p>{fetchedProduct?.height_mm ?? "N/A"}</p>
          )}
        </div>
        <div className="space-y-1">
          <Label
            htmlFor="product-length"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Length (mm)
          </Label>
          {isEditing ? (
            <Input
              id="product-length"
              name="length_mm"
              type="number"
              placeholder="e.g., 150"
              value={productData.length_mm ?? ""}
              onChange={handleFormChange}
              disabled={isMutating}
            />
          ) : (
            <p>{fetchedProduct?.length_mm ?? "N/A"}</p>
          )}
        </div>
        <div className="space-y-1">
          <Label
            htmlFor="product-width"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Width (mm)
          </Label>
          {isEditing ? (
            <Input
              id="product-width"
              name="width_mm"
              type="number"
              placeholder="e.g., 50"
              value={productData.width_mm ?? ""}
              onChange={handleFormChange}
              disabled={isMutating}
            />
          ) : (
            <p>{fetchedProduct?.width_mm ?? "N/A"}</p>
          )}
        </div>
        <div className="space-y-1">
          <Label
            htmlFor="product-weight"
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Weight (g)
          </Label>
          {isEditing ? (
            <Input
              id="product-weight"
              name="weight"
              type="number"
              placeholder="e.g., 250"
              value={productData.weight ?? ""}
              onChange={handleFormChange}
              disabled={isMutating}
            />
          ) : (
            <p>{fetchedProduct?.weight ?? "N/A"}</p>
          )}
        </div>
      </div>

      <h3 className="text-lg font-semibold border-b pb-1 mb-3 pt-4">Flags</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-x-4 gap-y-4 text-sm">
        <div className="space-y-1">
          <Label
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Packaging
          </Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox
                id="product-hanging"
                checked={productData.is_hanging ?? false}
                onCheckedChange={(checked) =>
                  handleCheckboxChange("is_hanging", checked)
                }
                disabled={isMutating}
              />
              <Label htmlFor="product-hanging" className="text-sm font-medium">
                Hanging
              </Label>
            </div>
          ) : (
            <Badge
              variant={fetchedProduct?.is_hanging ? "default" : "secondary"}
            >
              {fetchedProduct?.is_hanging ? "Hanging" : "Not Hanging"}
            </Badge>
          )}
        </div>
        <div className="space-y-1">
          <Label
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Design
          </Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox
                id="product-one-sided"
                checked={productData.is_one_sided ?? false}
                onCheckedChange={(checked) =>
                  handleCheckboxChange("is_one_sided", checked)
                }
                disabled={isMutating}
              />
              <Label
                htmlFor="product-one-sided"
                className="text-sm font-medium"
              >
                One-Sided
              </Label>
            </div>
          ) : (
            <Badge
              variant={fetchedProduct?.is_one_sided ? "default" : "secondary"}
            >
              {fetchedProduct?.is_one_sided ? "One-Sided" : "Multi-Sided"}
            </Badge>
          )}
        </div>
        <div className="space-y-1">
          <Label
            className={isEditing ? "" : "text-muted-foreground font-medium"}
          >
            Release Status
          </Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox
                id="product-new"
                checked={productData.is_new ?? false}
                onCheckedChange={(checked) =>
                  handleCheckboxChange("is_new", checked)
                }
                disabled={isMutating}
              />
              <Label htmlFor="product-new" className="text-sm font-medium">
                Novelty
              </Label>
            </div>
          ) : (
            <Badge variant={fetchedProduct?.is_new ? "default" : "secondary"}>
              {fetchedProduct?.is_new ? "Novelty" : "Established"}
            </Badge>
          )}
        </div>
      </div>

      <h3 className="text-lg font-semibold border-b pb-1 mb-3 pt-4">
        Description
      </h3>
      <div className="space-y-1">
        {isEditing ? (
          <Textarea
            id="product-description"
            name="description"
            placeholder="Detailed description..."
            value={productData.description ?? ""}
            onChange={handleFormChange}
            disabled={isMutating}
            className="min-h-[100px]"
            rows={4}
          />
        ) : (
          <p className="text-sm text-muted-foreground min-h-[20px]">
            {fetchedProduct?.description || "No description provided."}
          </p>
        )}
      </div>

      {(isEditing ||
        (Array.isArray(fetchedProduct?.tags) &&
          fetchedProduct.tags.length > 0) ||
        fetchedProduct?.keywords) && (
        <div className="pt-4">
          <h3 className="text-lg font-semibold border-b pb-1 mb-3">
            Tags & Keywords
          </h3>
          {isEditing ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label htmlFor="product-tags">Tags (comma-separated)</Label>
                <Input
                  id="product-tags"
                  name="tags"
                  placeholder="e.g., tag1, tag2"
                  value={
                    Array.isArray(productData.tags)
                      ? productData.tags.join(", ")
                      : ""
                  }
                  onChange={(e) =>
                    handleFormChange({
                      target: {
                        name: "tags",
                        value: e.target.value
                          .split(",")
                          .map((t) => t.trim())
                          .filter(Boolean),
                      },
                    } as any)
                  }
                  disabled={isMutating}
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="product-keywords">
                  Keywords (comma-separated)
                </Label>
                <Input
                  id="product-keywords"
                  name="keywords"
                  placeholder="e.g., keyword1, keyword2"
                  value={productData.keywords ?? ""}
                  onChange={handleFormChange}
                  disabled={isMutating}
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-wrap gap-1">
              {Array.isArray(fetchedProduct?.tags) &&
                fetchedProduct.tags.map((tag) => (
                  <Badge key={tag} variant="outline">
                    {tag}
                  </Badge>
                ))}
              {typeof fetchedProduct?.keywords === "string" &&
                fetchedProduct.keywords.split(/[,; ]+/).map(
                  (keyword) =>
                    keyword && (
                      <Badge key={keyword} variant="secondary">
                        {keyword}
                      </Badge>
                    )
                )}
            </div>
          )}
        </div>
      )}

      {!isEditing && fetchedProduct && (
        <div className="text-xs text-muted-foreground mt-6 pt-4 border-t">
          <p>
            Created:{" "}
            {fetchedProduct.created_at
              ? new Date(fetchedProduct.created_at).toLocaleString()
              : "N/A"}
          </p>
          <p>
            Last Updated:{" "}
            {fetchedProduct.updated_at
              ? new Date(fetchedProduct.updated_at).toLocaleString()
              : "N/A"}
          </p>
        </div>
      )}
    </form>
  );
}
