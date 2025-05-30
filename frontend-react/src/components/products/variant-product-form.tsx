"use client";
import React, { useState, useEffect } from "react";
import { Product } from "@/components/types/product";
import {
  Button,
  Input,
  Label,
  Checkbox,
  Textarea,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
  FormDescription,
} from "@/components/ui";
import { Loader2 } from "lucide-react";

interface VariantProductFormProps {
  parentProduct: Product | null;
  onSubmit: (data: Omit<Product, "id">) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
  error: string | null;
  initialData?: Partial<Product>;
}

interface FormValues {
  name: string;
  description: string;
  is_active: boolean;
  price: number;
  sku: string;
  [key: string]: any;
}

const VariantProductForm: React.FC<VariantProductFormProps> = ({
  parentProduct,
  onSubmit,
  onCancel,
  isLoading,
  error,
  initialData,
}) => {
  const [formValues, setFormValues] = useState<FormValues>({
    name: initialData?.name || "",
    description: initialData?.description || "",
    is_active: initialData?.is_active ?? true,
    price: initialData?.price || 0,
    sku: initialData?.sku || "",
  });
  
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSaveDisabled, setIsSaveDisabled] = useState(true);
  
  // Check if required fields are filled and enable/disable save button
  useEffect(() => {
    const hasRequiredFields = !!formValues.name.trim();
    const hasValidationErrors = Object.keys(formErrors).length > 0;
    
    setIsSaveDisabled(!hasRequiredFields || hasValidationErrors);
  }, [formValues, formErrors]);
  
  const validateField = (name: string, value: any): string => {
    switch (name) {
      case "name":
        return !value.trim() ? "Name is required" : "";
      case "price":
        return isNaN(parseFloat(value)) ? "Price must be a number" : "";
      default:
        return "";
    }
  };
  
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    const isCheckbox = type === "checkbox";
    const newValue = isCheckbox 
      ? (e.target as HTMLInputElement).checked 
      : value;
    
    // Update form values
    setFormValues((prev) => ({
      ...prev,
      [name]: newValue,
    }));
    
    // Validate field
    const error = validateField(name, newValue);
    
    // Update errors
    setFormErrors((prev) => ({
      ...prev,
      [name]: error,
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Final validation before submit
    const newErrors: Record<string, string> = {};
    
    Object.entries(formValues).forEach(([key, value]) => {
      const error = validateField(key, value);
      if (error) {
        newErrors[key] = error;
      }
    });
    
    if (Object.keys(newErrors).length > 0) {
      setFormErrors(newErrors);
      return;
    }
    
    // Transform form values to product data
    const productData: Omit<Product, "id"> = {
      ...formValues,
      name_en: formValues.name, // Assuming English name defaults to main name
      // Convert price to number if it's a string
      price: typeof formValues.price === 'string' 
        ? parseFloat(formValues.price) 
        : formValues.price,
    };
    
    await onSubmit(productData);
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded">
          {error}
        </div>
      )}
      
      {parentProduct && (
        <div className="bg-slate-50 border border-slate-200 p-3 rounded mb-4">
          <div className="text-sm font-medium">Parent Product</div>
          <div className="text-lg">{parentProduct.name}</div>
          {parentProduct.sku && <div className="text-sm text-slate-500">SKU: {parentProduct.sku}</div>}
        </div>
      )}
      
      <FormField>
        <FormItem>
          <FormLabel htmlFor="name" className="text-base">Name *</FormLabel>
          <FormControl>
            <Input
              id="name"
              name="name"
              value={formValues.name}
              onChange={handleChange}
              className={formErrors.name ? "border-red-500" : ""}
              disabled={isLoading}
            />
          </FormControl>
          {formErrors.name && <FormMessage>{formErrors.name}</FormMessage>}
          <FormDescription>
            The name of the variant.
          </FormDescription>
        </FormItem>
      </FormField>
      
      <FormField>
        <FormItem>
          <FormLabel htmlFor="description" className="text-base">Description</FormLabel>
          <FormControl>
            <Textarea
              id="description"
              name="description"
              value={formValues.description || ""}
              onChange={handleChange}
              rows={4}
              disabled={isLoading}
            />
          </FormControl>
          <FormDescription>
            A detailed description of the variant product.
          </FormDescription>
        </FormItem>
      </FormField>
      
      <FormField>
        <FormItem>
          <FormLabel htmlFor="price" className="text-base">Price</FormLabel>
          <FormControl>
            <Input
              id="price"
              name="price"
              type="number"
              step="0.01"
              value={formValues.price}
              onChange={handleChange}
              className={formErrors.price ? "border-red-500" : ""}
              disabled={isLoading}
            />
          </FormControl>
          {formErrors.price && <FormMessage>{formErrors.price}</FormMessage>}
          <FormDescription>
            The price of the variant product.
          </FormDescription>
        </FormItem>
      </FormField>
      
      <FormField>
        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
          <FormControl>
            <Checkbox
              id="is_active"
              name="is_active"
              checked={formValues.is_active}
              onCheckedChange={(checked) => {
                setFormValues((prev) => ({
                  ...prev,
                  is_active: !!checked,
                }));
              }}
              disabled={isLoading}
            />
          </FormControl>
          <div className="space-y-1 leading-none">
            <FormLabel htmlFor="is_active" className="text-base">
              Active
            </FormLabel>
            <FormDescription>
              Indicates if the variant is active and should be shown in listings.
            </FormDescription>
          </div>
        </FormItem>
      </FormField>
      
      <div className="flex justify-end space-x-3">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isSaveDisabled || isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            "Save"
          )}
        </Button>
      </div>
    </form>
  );
};

export default VariantProductForm; 