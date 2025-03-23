// components/ProductDetail/MutterTab.tsx
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Minus, Zap, Plus } from "lucide-react";

// Define the interface based on the schema
interface SelectedProductData {
  id: string;
  sku: string;
  name: string;
  description: string;
  height_mm: string;
  length_mm: string;
  width_mm: string;
  weight: string;
  is_hanging: boolean;
  is_one_sided: boolean;
  packaging_id: string;
  is_active: boolean;
  is_new: boolean;
  release_date: string;
}

interface MutterTabProps {
  selectedItem: string | null; // Assuming selectedItem contains the product ID or SKU
}

export default function MutterTab({ selectedItem }: MutterTabProps) {
  // Initialize selectedProductData with static data
  const [selectedProductData, setSelectedProductData] =
    useState<SelectedProductData>({
      id: "218300",
      sku: "AL-001",
      name: '"Adler"-Lock',
      description:
        "Erleben Sie die Eleganz und den Charme vergangener Zeiten mit dieser exquisiten Zinnfigur, inspiriert von den Anfängen der Eisenbahngeschichte. Perfekt für Sammler und Liebhaber von Nostalgie, zeigt diese Figur einen klassischen Lokführer, gekleidet in traditioneller Montur, der stolz seine Maschine lenkt. Ideal für jede Vitrine oder als geschmackvolles Geschenk. Eine Hommage an die Ingenieurskunst und das kulturelle Erbe.",
      height_mm: "70",
      length_mm: "70",
      width_mm: "7",
      weight: "30",
      is_hanging: false,
      is_one_sided: false,
      packaging_id: "B5",
      is_active: true,
      is_new: false,
      release_date: "2023-01-01",
    });

  // Separate state for categories
  const [categories, setCategories] = useState<string[][]>([
    ["Home", "", "", "All Products"],
    ["", "", "", ""],
    ["", "", "", ""],
  ]);

  // Update selectedProductData when selectedItem changes (static logic for now)
  useEffect(() => {
    if (selectedItem) {
      // For now, we are using static data
      // In the future, fetch product data based on selectedItem.id
      /*
      const fetchProductData = async () => {
        try {
          const productData = await getProduct(selectedItem);
          setSelectedProductData(productData);
        } catch (error) {
          console.error('Error fetching product data:', error);
        }
      };
      fetchProductData();
      */
      setSelectedProductData((prev) => ({
        ...prev,
        name: selectedItem === "218300" ? '"Adler"-Lock' : prev.name,
      }));
    }
  }, [selectedItem]);

  // Handlers to update selectedProductData
  const handleInputChange = (
    field: keyof SelectedProductData,
    value: string | boolean
  ) => {
    setSelectedProductData((prev) => ({
      ...prev,
      [field]: value,
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

  // Placeholder logic for save and delete
  const handleSave = () => {
    console.log("Save clicked:", selectedProductData);
    // TODO: Implement API call to save selectedProductData
    alert("Product saved! (Placeholder)");
  };

  const handleDelete = () => {
    console.log("Delete clicked for item:", selectedItem);
    // TODO: Implement API call to delete the product
    alert("Product deleted! (Placeholder)");
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
                <h1 className="text-2xl font-bold">
                  {selectedProductData.name}
                </h1>
                <Badge className="w-fit bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50">
                  Aktiv
                </Badge>
              </div>
              <p className="text-slate-500 dark:text-slate-400 mt-1">
                Artikelnummer: {selectedItem || "N/A"}
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-2 md:justify-end ">
              <Button
                variant="outline"
                className="rounded-full"
                onClick={handleDelete}
              >
                <Minus className="h-4 w-4 mr-2" />
                Löschen
              </Button>
              <Button
                className="rounded-full bg-blue-600 hover:bg-blue-700 text-white"
                onClick={handleSave}
              >
                <Zap className="h-4 w-4 mr-2" />
                Speichern
              </Button>
            </div>
          </div>
        </div>

        {/* Bezeichnung & Beschreibung */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-semibold mb-4">Produktdetails</h2>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                Bezeichnung
              </label>
              <div className="md:col-span-3">
                <Input
                  value={selectedProductData.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  className="w-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400 md:pt-2.5">
                Beschreibung
              </label>
              <div className="md:col-span-3">
                <textarea
                  value={selectedProductData.description}
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
            <h2 className="text-lg font-semibold">Maße & Eigenschaften</h2>
            <Badge
              variant="outline"
              className="text-xs font-normal px-2 py-0.5 h-5 border-slate-200 dark:border-slate-700"
            >
              Einheit: mm
            </Badge>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Höhe
              </label>
              <Input
                value={selectedProductData.height_mm}
                onChange={(e) => handleInputChange("height_mm", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Länge
              </label>
              <Input
                value={selectedProductData.length_mm}
                onChange={(e) => handleInputChange("length_mm", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Breite
              </label>
              <Input
                value={selectedProductData.width_mm}
                onChange={(e) => handleInputChange("width_mm", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Gewicht (g)
              </label>
              <Input
                value={selectedProductData.weight}
                onChange={(e) => handleInputChange("weight", e.target.value)}
                className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="hangend"
                checked={selectedProductData.is_hanging}
                onChange={(e) =>
                  handleInputChange("is_hanging", e.target.checked)
                }
                className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
              />
              <label htmlFor="hangend" className="text-sm">
                Hängend
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="einseitig"
                checked={selectedProductData.is_one_sided}
                onChange={(e) =>
                  handleInputChange("is_one_sided", e.target.checked)
                }
                className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
              />
              <label htmlFor="einseitig" className="text-sm">
                Einseitig
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="neuheit"
                checked={selectedProductData.is_new}
                onChange={(e) => handleInputChange("is_new", e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
              />
              <label htmlFor="neuheit" className="text-sm">
                Neuheit
              </label>
            </div>
          </div>
          <div className="mt-6">
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400 w-24">
                Boxgröße
              </label>
              <Input
                value={selectedProductData.packaging_id}
                onChange={(e) =>
                  handleInputChange("packaging_id", e.target.value)
                }
                className="w-32 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
              />
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
                <span className="text-xs">Hinzufügen</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 rounded-full border border-red-500"
                onClick={handleDelete}
              >
                <Minus className="h-3.5 w-3.5 mr-1 " />
                <span className="text-xs">Entfernen</span>
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
