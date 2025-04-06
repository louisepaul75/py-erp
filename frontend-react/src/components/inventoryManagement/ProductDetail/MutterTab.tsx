// components/Product/MutterTab.tsx
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { StatusBadge } from "@/components/ui";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Minus, Zap, Plus, Edit, X } from "lucide-react";
import { productApi } from "@/lib/products/api";
import { SelectedItem } from "@/components/types/product";
import { Product, ProductDetailProps } from "@/components/types/product";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
import useAppTranslation from "@/hooks/useTranslationWrapper";
import { cn } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

// Define an extended interface that includes the creation props
interface MutterTabProps extends ProductDetailProps {
  isCreatingParent?: boolean;
  onSave?: (data: Omit<Product, "id">) => Promise<void>;
  onCancel?: () => void;
  canEdit?: boolean;
}

export default function MutterTab({
  selectedItem,
  selectedProduct,
  isCreatingParent = false,
  onSave,
  onCancel,
  canEdit = false,
}: MutterTabProps) {
  const [isEditing, setIsEditing] = useState(isCreatingParent);
  const [initialProductData, setInitialProductData] = useState<Partial<Product> | null>(null);
  const [initialCategories, setInitialCategories] = useState<string[][]>([]);

  // Initialize with selectedProduct data or defaults if creating a new one
  const [productData, setProductData] = useState<Partial<Product>>(() => {
    if (selectedProduct) {
      return selectedProduct;
    } else {
      return {
        name: "",
        description: "",
        is_active: true,
        // Add other default fields as needed
      };
    }
  });
  
  // Update productData when selectedProduct changes AND not currently editing
  useEffect(() => {
    if (selectedProduct && !isEditing) {
      setProductData(selectedProduct);
      // Also potentially reset categories based on selectedProduct if they come from there
      // For now, assuming categories are managed independently or reset elsewhere
    }
    // Set initial state when product loads (and not creating)
    if (selectedProduct && !isCreatingParent) {
       setInitialProductData(JSON.parse(JSON.stringify(selectedProduct))); // Deep copy
    }
  }, [selectedProduct, isEditing, isCreatingParent]);

  const { t } = useAppTranslation("mutterTab"); // Use the mutterTab namespace

  // Separate state for categories
  const [categories, setCategories] = useState<string[][]>([
    ["Home", "", "", "All Products"],
    ["", "", "", ""],
    ["", "", "", ""],
  ]);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Store initial categories when editing starts
  useEffect(() => {
    if (isEditing) {
      // Store deep copy of current categories when editing starts
       setInitialCategories(JSON.parse(JSON.stringify(categories)));
      // Store deep copy of product data if not creating
      if (!isCreatingParent && selectedProduct) {
         setInitialProductData(JSON.parse(JSON.stringify(selectedProduct)));
      }
    }
  }, [isEditing, selectedProduct, isCreatingParent]); // Rerun if selectedProduct changes while editing is false

  // Handlers to update product data
  const handleInputChange = (
    field: keyof Product,
    value: string | boolean | number | null
  ) => {
    setProductData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handler to update categories
  const handleCategoryChange = (
    rowIndex: number,
    colIndex: number,
    value: string
  ) => {
    setCategories((prev) =>
      prev.map((row, i) =>
        i === rowIndex
          ? row.map((cell, j) => (j === colIndex ? value : cell))
          : row
      )
    );
  };

  // Handler to add a new category row
  const handleAddCategory = () => {
    setCategories((prev) => [...prev, ["", "", "", ""]]);
  };

  // Handler for save button (edit existing or create new)
  const handleSave = async () => {
    // Validate required fields
    if (!productData.name) {
      setError("Name is required");
      return;
    }
    
    setIsSaving(true);
    setError(null);
    
    try {
      if (isCreatingParent && onSave) {
        // Creating a new parent product
        await onSave(productData as Omit<Product, "id">);
      } else {
        // Updating an existing product
        if (selectedProduct?.id) {
          await productApi.updateProduct(selectedProduct.id.toString(), productData);
          alert("Product saved successfully!");
          setIsEditing(false); // Exit edit mode on successful save
        } else {
          console.error("No product ID found to update.");
        }
      }
    } catch (err: any) {
      console.error("Error saving product:", err);
      setError(`Failed to save product: ${err.message || "Unknown error"}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    if (isCreatingParent && onCancel) {
      onCancel(); // Use the specific cancel handler for creation flow
    } else {
      // Reset product data and categories to their initial state
      if (initialProductData) {
         setProductData(JSON.parse(JSON.stringify(initialProductData))); // Reset from deep copy
      }
       setCategories(JSON.parse(JSON.stringify(initialCategories))); // Reset from deep copy
      setIsEditing(false);
      setError(null); // Clear any validation errors
    }
  };

  const confirmDeleteProduct = () => {
    console.log("confirm to delete");
    setIsDeleteDialogOpen(true);
  };

  const handleDelete = async () => {
    if (!selectedProduct?.id) {
      console.error("No product ID found to delete.");
      return;
    }

    try {
      console.log("Deleting product with ID:", selectedProduct.id);
      await productApi.deleteProduct(selectedProduct.id.toString()); // Call the API
      console.log("Product deleted successfully!");
      setIsEditing(false); // Exit edit mode after deletion
      // Maybe navigate away or refresh list? Needs UX decision.
      alert("Product deleted successfully!");
    } catch (error) {
      console.error("Error deleting product:", error);
      alert("Failed to delete the product. Please try again.");
    }
  };

  return (
    <div>
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header Section using Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col flex-wrap md:flex-row md:items-center gap-4 md:gap-6">
              <div className="h-16 w-16 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xl">
                {isCreatingParent ? "NEW" : productData?.sku?.substring(0, 2) || "AL"}
              </div>
              <div className="flex-1">
                <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4">
                  <h1 className="text-2xl font-bold">
                    {isCreatingParent 
                      ? "Create New Parent Product" 
                      : productData.name || "Product Details"}
                  </h1>
                  {!isCreatingParent && (
                    <Badge
                      variant={productData.is_active ? "default" : "secondary"} 
                      className={cn("text-xs", productData.is_active 
                        ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-900/50" 
                        : "bg-gray-100 text-gray-800 dark:bg-gray-800/30 dark:text-gray-400 border border-gray-200 dark:border-gray-800/50")}
                    >
                      {productData.is_active ? t("active") : t("inactive")}
                    </Badge>
                  )}
                </div>
                {!isCreatingParent && (
                  <p className="text-slate-500 dark:text-slate-400 mt-1">
                    {t("articleNumber")}: {selectedItem || "N/A"}
                  </p>
                )}
              </div>
              <div className="flex flex-col sm:flex-row gap-2 md:justify-end ">
                {!isCreatingParent && !isEditing && canEdit && (
                  <Button
                    onClick={handleEdit}
                    variant="outline"
                    className="rounded-full"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    {t("edit")}
                  </Button>
                )}
                {isEditing && (
                  <>
                    {!isCreatingParent && (
                      <AlertDialog
                        open={isDeleteDialogOpen}
                        onOpenChange={setIsDeleteDialogOpen}
                      >
                        <AlertDialogTrigger asChild>
                          <Button
                            onClick={confirmDeleteProduct}
                            variant="outline"
                            className="rounded-full"
                            disabled={isSaving}
                          >
                            <Minus className="h-4 w-4 mr-2" />
                            {t("delete")}
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>
                              {t("confirmDeleteTitle")}
                            </AlertDialogTitle>
                            <AlertDialogDescription>
                              {t("confirmDeleteDescription")}
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel className="rounded-full px-5 py-2">
                              {t("cancel")}
                            </AlertDialogCancel>
                            <AlertDialogAction
                              onClick={handleDelete}
                              className="rounded-full px-5 py-2"
                            >
                              {t("ok")}
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    )}

                    <Button
                      variant="outline"
                      className="rounded-full"
                      onClick={handleCancel}
                      disabled={isSaving}
                    >
                      <X className="h-4 w-4 mr-2" />
                      {t("cancel")}
                    </Button>

                    <Button
                      variant="default"
                      className="rounded-full"
                      onClick={handleSave}
                      disabled={isSaving || !productData.name}
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      {isSaving ? t("saving") : (isCreatingParent ? t("create") : t("save"))}
                    </Button>
                  </>
                )}
              </div>
            </div>
            
            {/* Error message */}
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Bezeichnung & Beschreibung using Card */}
        <Card>
          <CardHeader>
            <CardTitle>{t("productDetails")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                {t("designation")}
              </label>
              <div className="md:col-span-3 ml-3">
                <Input
                  value={productData.name || ""}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  className="w-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                {t("description")}
              </label>
              <div className="md:col-span-3 ml-3">
                <Textarea
                  value={productData.description || ""}
                  onChange={(e) =>
                    handleInputChange("description", e.target.value)
                  }
                  className="w-full border border-slate-200 dark:border-slate-700 rounded-lg p-3 text-sm min-h-[150px] resize-none bg-slate-50 dark:bg-slate-800"
                  disabled={!isEditing}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Maße using Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{t("dimensions")}</CardTitle>
              <Badge
                variant="outline"
                className="text-xs font-normal px-2 py-0.5 h-5 border-slate-200 dark:border-slate-700"
              >
                {t("unit")}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                  {t("height")}
                </label>
                <Input
                  value={productData.height_mm ?? ""}
                  onChange={(e) => handleInputChange("height_mm", e.target.value ? parseFloat(e.target.value) : null)}
                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                  {t("length")}
                </label>
                <Input
                  value={productData.length_mm ?? ""}
                  onChange={(e) => handleInputChange("length_mm", e.target.value ? parseFloat(e.target.value) : null)}
                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                  {t("width")}
                </label>
                <Input
                  value={productData.width_mm ?? ""}
                  onChange={(e) => handleInputChange("width_mm", e.target.value ? parseFloat(e.target.value) : null)}
                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                  {t("weight")}
                </label>
                <Input
                  value={productData.weight ?? ""}
                  onChange={(e) => handleInputChange("weight", e.target.value ? parseFloat(e.target.value) : null)}
                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="hangend"
                  checked={productData.is_hanging ?? false}
                  onCheckedChange={(checked) =>
                    handleInputChange("is_hanging", !!checked)
                  }
                  className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                  disabled={!isEditing}
                />
                <label htmlFor="hangend" className="text-sm">
                  {t("hanging")}
                </label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="einseitig"
                  checked={productData.is_one_sided ?? false}
                  onCheckedChange={(checked) =>
                    handleInputChange("is_one_sided", !!checked)
                  }
                  className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                  disabled={!isEditing}
                />
                <label htmlFor="einseitig" className="text-sm">
                  {t("oneSided")}
                </label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="neuheit"
                  checked={productData.is_new ?? false}
                  onCheckedChange={(checked) => handleInputChange("is_new", !!checked)}
                  className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                  disabled={!isEditing}
                />
                <label htmlFor="neuheit" className="text-sm">
                  {t("novelty")}
                </label>
              </div>
            </div>
            <div className="mt-6">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-slate-500 dark:text-slate-400 w-24">
                  Boxgröße
                </label>
                {/* Input for Boxgröße removed, can be added back if needed */}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Kategorien using Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Kategorien</CardTitle>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 rounded-full"
                  onClick={handleAddCategory}
                  disabled={!isEditing}
                >
                  <Plus className="h-3.5 w-3.5 mr-1" />
                  <span className="text-xs">{t("add")}</span>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 rounded-full "
                  onClick={handleDelete}
                  disabled={!isEditing || categories.length <= 1}
                >
                  <Minus className="h-3.5 w-3.5 mr-1 " />
                  <span className="text-xs">{t("remove")}</span>
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableHead className="font-medium">Home</TableHead>
                    <TableHead className="font-medium">Sortiment</TableHead>
                    <TableHead className="font-medium">Tradition</TableHead>
                    <TableHead className="font-medium">Maschinerie</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {categories.map((row, rowIndex) => (
                    <TableRow key={rowIndex}>
                      {row.map((cell, colIndex) => (
                        <TableCell key={colIndex}>
                          <Input
                            value={cell}
                            onChange={(e) =>
                              handleCategoryChange(
                                rowIndex,
                                colIndex,
                                e.target.value
                              )
                            }
                            className="w-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                            disabled={!isEditing}
                          />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
