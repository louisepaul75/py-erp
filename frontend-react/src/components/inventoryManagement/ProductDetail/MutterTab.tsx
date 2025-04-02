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
import { Minus, Zap, Plus } from "lucide-react";
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

// Define the interface based on the schema

export default function MutterTab({
  selectedItem,
  selectedProduct,
}: ProductDetailProps) {
  // Initialize selectedProduct with static data

  const { t } = useAppTranslation("mutterTab"); // Use the mutterTab namespace

  // Separate state for categories
  const [categories, setCategories] = useState<string[][]>([
    ["Home", "", "", "All Products"],
    ["", "", "", ""],
    ["", "", "", ""],
  ]);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Handlers to update selectedProductData
  const handleInputChange = (
    field: keyof Product,
    value: string | boolean
  ) => {};

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

  // Placeholder logic for save and delete
  const handleSave = () => {
    console.log("Save clicked:", selectedProduct);
    // TODO: Implement API call to save selectedProduct
    alert("Product saved! (Placeholder)");
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

      // Optionally, you can add further logic here, such as:
      // - Showing a success message
      // - Redirecting the user
      // - Refreshing the product list
      alert("Product deleted successfully!");
    } catch (error) {
      console.error("Error deleting product:", error);
      alert("Failed to delete the product. Please try again.");
    }
  };

  return (
    <div className="p-4 lg:p-6">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header with Product Info */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex flex-col flex-wrap md:flex-row md:items-center gap-4 md:gap-6 ">
            <div className="h-16 w-16 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xl">
              AL
            </div>
            <div className="flex-1">
              <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4">
                <h1 className="text-2xl font-bold">{selectedProduct?.name}</h1>
                <StatusBadge status={selectedProduct?.is_active ? "active" : "inactive"}>
                  {selectedProduct?.is_active ? t("active") : t("inactive")}
                </StatusBadge>
              </div>
              <p className="text-slate-500 dark:text-slate-400 mt-1">
                {t("articleNumber")}: {selectedItem || "N/A"}
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-2 md:justify-end ">
              <AlertDialog
                open={isDeleteDialogOpen}
                onOpenChange={setIsDeleteDialogOpen}
              >
                <AlertDialogTrigger asChild>
                  <Button
                    onClick={confirmDeleteProduct}
                    variant="outline"
                    className="rounded-full"
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
                    <AlertDialogCancel variant="destructive" className="rounded-full px-5 py-2">
                      {t("cancel")}
                    </AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDelete}
                      variant="default"
                      className="rounded-full px-5 py-2"
                    >
                      {t("ok")}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              <Button
                variant="default"
                className="rounded-full"
                onClick={handleSave}
              >
                <Zap className="h-4 w-4 mr-2" />
                {t("save")}
              </Button>
            </div>
          </div>
        </div>

        {/* Bezeichnung & Beschreibung */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-semibold mb-4">{t("productDetails")}</h2>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                {t("designation")}
              </label>
              <div className="md:col-span-3 ml-3">
                <Input
                  value={selectedProduct?.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  className="w-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                {t("description")}
              </label>
              <div className="md:col-span-3 ml-3">
                <Textarea
                  value={selectedProduct?.description}
                  onChange={(e) =>
                    handleInputChange("description", e.target.value)
                  }
                  className="w-full border border-slate-200 dark:border-slate-700 rounded-lg p-3 text-sm min-h-[150px] resize-none bg-slate-50 dark:bg-slate-800"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Maße */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">{t("dimensions")}</h2>
            <Badge
              variant="outline"
              className="text-xs font-normal px-2 py-0.5 h-5 border-slate-200 dark:border-slate-700"
            >
              {t("unit")}
            </Badge>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                {t("height")}
              </label>
              <Input
                value={selectedProduct?.height_mm ?? ""}
                onChange={(e) => handleInputChange("height_mm", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                {t("length")}
              </label>
              <Input
                value={selectedProduct?.length_mm ?? ""}
                onChange={(e) => handleInputChange("length_mm", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                {t("width")}
              </label>
              <Input
                value={selectedProduct?.width_mm ?? ""}
                onChange={(e) => handleInputChange("width_mm", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                {t("weight")}
              </label>
              <Input
                value={selectedProduct?.weight ?? ""}
                onChange={(e) => handleInputChange("weight", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
            <div className="flex items-center gap-2">
              <Checkbox
                id="hangend"
                checked={selectedProduct?.is_hanging ?? false}
                onCheckedChange={(checked) =>
                  handleInputChange("is_hanging", !!checked)
                }
                className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
              />
              <label htmlFor="hangend" className="text-sm">
                {t("hanging")}
              </label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="einseitig"
                checked={selectedProduct?.is_one_sided ?? false}
                onCheckedChange={(checked) =>
                  handleInputChange("is_one_sided", !!checked)
                }
                className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
              />
              <label htmlFor="einseitig" className="text-sm">
                {t("oneSided")}
              </label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="neuheit"
                checked={selectedProduct?.is_new ?? false}
                onCheckedChange={(checked) => handleInputChange("is_new", !!checked)}
                className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
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
              {/* <Input
                value={selectedProduct.packaging_id}
                onChange={(e) =>
                  handleInputChange("packaging_id", e.target.value)
                }
                className="w-32 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              /> */}
            </div>
          </div>
        </div>

        {/* Kategorien */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Kategorien</h2>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                className="h-8 rounded-full"
                onClick={handleAddCategory}
              >
                <Plus className="h-3.5 w-3.5 mr-1" />
                <span className="text-xs">{t("add")}</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 rounded-full "
                onClick={handleDelete}
              >
                <Minus className="h-3.5 w-3.5 mr-1 " />
                <span className="text-xs">{t("remove")}</span>
              </Button>
            </div>
          </div>
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
                        />
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </div>
  );
}
