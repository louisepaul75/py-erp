"use client";
import React, { useState, useCallback } from "react";
import { Product } from "../types/product";
import { productApi } from "@/lib/products/api"; // Adjust path if needed
import {
  Button,
  Input,
  Label,
  RadioGroup,
  RadioGroupItem,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui"; // Assuming shared UI components are here
import { Loader2 } from "lucide-react";

// Define the shape of the form data
interface ProductFormData {
  name: string;
  parent_id: number | string | null;
  is_active: boolean;
}

interface ProductCreateFormProps {
  createType: "parent" | "variant";
  setCreateType: (type: "parent" | "variant") => void;
  onProductCreated: (newProduct: Product) => void;
  onCancel: () => void;
  searchParentProducts: (term: string) => Promise<Product[]>;
  createProduct: (
    productData: Omit<Product, "id"> & { parent_id?: number | string }
  ) => Promise<Product>;
}

const ProductCreateForm: React.FC<ProductCreateFormProps> = ({
  createType,
  setCreateType,
  onProductCreated,
  onCancel,
  searchParentProducts,
  createProduct,
}) => {
  const [formData, setFormData] = useState<ProductFormData>({
    name: "",
    parent_id: null,
    is_active: true, // Default to active
  });
  const [parentSearchTerm, setParentSearchTerm] = useState("");
  const [parentOptions, setParentOptions] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearchingParents, setIsSearchingParents] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedSku, setGeneratedSku] = useState<string | null>(null); // State for generated SKU

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleParentSelect = (value: string) => {
    setFormData((prev) => ({ ...prev, parent_id: value }));
    // Clear search term and options after selection
    setParentSearchTerm("");
    setParentOptions([]);
  };

  // Debounced search for parent products
  const debouncedSearch = useCallback(
    debounce(async (term: string) => {
      if (term.length < 2) {
        setParentOptions([]);
        setIsSearchingParents(false);
        return;
      }
      setIsSearchingParents(true);
      try {
        const results = await searchParentProducts(term);
        setParentOptions(results);
      } catch (err) {
        console.error("Error searching parents:", err);
        setError("Failed to search for parent products.");
      } finally {
        setIsSearchingParents(false);
      }
    }, 300), // 300ms debounce delay
    [searchParentProducts] // Dependency
  );

  const handleParentSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setParentSearchTerm(term);
    debouncedSearch(term);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const payload: Omit<Product, "id"> & { parent_id?: number | string } = {
      ...formData,
      // Add any other required fields from Product type with defaults if needed
      name_en: formData.name, // Example: default English name to German name
      parent_id: createType === 'variant' ? (formData.parent_id ?? undefined) : undefined,
    };

    // Basic Validation
    if (!formData.name) {
      setError("Name is required.");
      setIsLoading(false);
      return;
    }
    if (createType === 'variant' && !formData.parent_id) {
        setError("A parent product must be selected for variants.");
        setIsLoading(false);
        return;
    }

    try {
      console.log("Submitting payload:", payload);
      const newProduct = await createProduct(payload);
      console.log("Product created:", newProduct);
      setGeneratedSku(newProduct.sku); // Store the generated SKU
      
      // Wait for 2 seconds before calling the parent handler
      await new Promise(resolve => setTimeout(resolve, 2000)); 
      
      onProductCreated(newProduct); // Call parent handler (which will close the form)
    } catch (err: any) {
      console.error("Error creating product:", err);
      setError(
        `Failed to create product: ${err.message || "Unknown error"}`
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Simple debounce utility function
  function debounce<F extends (...args: any[]) => any>(
    func: F,
    waitFor: number
  ) {
    let timeoutId: NodeJS.Timeout | null = null;

    return (...args: Parameters<F>): Promise<ReturnType<F>> =>
      new Promise((resolve) => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }

        timeoutId = setTimeout(() => resolve(func(...args)), waitFor);
      });
  }

  return (
    <Card className="h-full overflow-auto">
      <CardHeader>
        <CardTitle>Create New Product</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Type Selector */}
          <div>
            <Label>Product Type</Label>
            <RadioGroup
              value={createType}
              onValueChange={(value) => setCreateType(value as "parent" | "variant")}
              className="flex space-x-4 mt-1"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="parent" id="r1" />
                <Label htmlFor="r1">Parent Product</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="variant" id="r2" />
                <Label htmlFor="r2">Variant Product</Label>
              </div>
            </RadioGroup>
          </div>

          {/* Parent Selector (Conditional) */}
          {createType === "variant" && (
            <div className="space-y-2">
              <Label htmlFor="parent_id">Parent Product</Label>
              <Select
                onValueChange={handleParentSelect}
                value={formData.parent_id ? String(formData.parent_id) : undefined}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Search and select parent..." />
                </SelectTrigger>
                <SelectContent>
                  <div className="p-2">
                    <Input
                      placeholder="Search by name or SKU..."
                      value={parentSearchTerm}
                      onChange={handleParentSearchChange}
                      className="mb-2"
                    />
                  </div>
                  {isSearchingParents && <SelectItem value="searching" disabled>Searching...</SelectItem>}
                  {!isSearchingParents && parentOptions.length === 0 && parentSearchTerm && (
                      <SelectItem value="no-results" disabled>No matching parents found.</SelectItem>
                  )}
                  {parentOptions.map((parent) => (
                    <SelectItem key={parent.id} value={String(parent.id)}>
                      {parent.name} ({parent.sku})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Basic Fields */}
          <div>
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              className="mt-1"
            />
          </div>

          {/* Display Generated SKU (Conditional) */}
          {generatedSku && (
            <div>
              <Label htmlFor="generatedSku">Generated SKU</Label>
              <Input
                id="generatedSku"
                name="generatedSku"
                value={generatedSku}
                readOnly
                className="mt-1 bg-slate-100 dark:bg-slate-800"
              />
            </div>
          )}

          {/* Add other fields as needed based on Product type */}

          {/* Error Display */}
          {error && (
            <p className="text-sm font-medium text-red-600 dark:text-red-500">{error}</p>
          )}
        </form>
      </CardContent>
      <CardFooter className="flex justify-end space-x-2">
        <Button
          variant="outline"
          onClick={onCancel}
          disabled={isLoading || !!generatedSku} // Disable cancel if SKU is shown?
        >
          Cancel
        </Button>
        <Button
          type="submit"
          onClick={handleSubmit}
          disabled={isLoading || !!generatedSku} // Disable create if loading or SKU shown
        >
          {isLoading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : null}
          {generatedSku ? "Created!" : "Create Product"} {/* Change button text after creation */}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ProductCreateForm; 