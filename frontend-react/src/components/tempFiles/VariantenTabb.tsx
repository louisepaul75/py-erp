// components/ProductDetail/VariantenTab.tsx
import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Plus,
  Minus,
  MoreHorizontal,
  Tag,
  Search,
  Download,
  ArrowUpDown,
  Zap,
} from "lucide-react";
import BilderTab from "@/components/bilder-tab";
import GewogenTab from "@/components/gewogen-tab";
import LagerorteTab from "@/components/lagerorte-tab";
import UmsatzeTab from "@/components/umsatze-tab";
import BewegungenTab from "@/components/bewegungen-tab";
import TeileTab from "@/components/teile-tab";
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

interface Variant {
  id: string;
  nummer: string;
  bezeichnung: string;
  auspraegung: string;
  prod: boolean;
  vertr: boolean;
  vkArtikel: boolean;
  releas: string;
  // price: number;
  selected: boolean;
}

interface VariantDetails {
  tags: string[];
  priceChanges: string;
  malgruppe: string;
  malkostenEur: string;
  malkostenCzk: string;
  selbstkosten: string;
}

interface VariantenTabProps {
  selectedItem: string | null;
}

export default function VariantenTab({ selectedItem }: VariantenTabProps) {
  const [variantenActiveTab, setVariantenActiveTab] = useState("details");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // Add state variables for controlling dialogs
  const [isRemoveDialogOpen, setIsRemoveDialogOpen] = useState(false);
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false);
  const [selectedVariantId, setSelectedVariantId] = useState<string | null>(
    null
  );
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newVariant, setNewVariant] = useState<Partial<Variant>>({
    id: "",
    nummer: "",
    bezeichnung: "",
    auspraegung: "",
    prod: false,
    vertr: false,
    vkArtikel: false,
    releas: "",
    // price: 0,
    selected: false,
  });

  // State for the variants table
  const [variants, setVariants] = useState<Variant[]>([
    {
      id: "1",
      nummer: "501506",
      bezeichnung: '"Adler"-Lock',
      auspraegung: "Blank",
      prod: false,
      vertr: false,
      vkArtikel: true,
      releas: "11.02.2023",
      // price: 37.4,
      selected: false,
    },
    {
      id: "2",
      nummer: "100870",
      bezeichnung: '"Adler"-Lock',
      auspraegung: "Bemalt",
      prod: true,
      vertr: true,
      vkArtikel: true,
      releas: "01.01.2023",
      // price: 29.5,
      selected: false,
    },
    {
      id: "3",
      nummer: "904743",
      bezeichnung: '"Adler"-Lock OX',
      auspraegung: "",
      prod: false,
      vertr: false,
      vkArtikel: false,
      releas: "01.01.1999",
      // price: 17.3,
      selected: false,
    },
  ]);

  // State for the Details tab
  const [variantDetails, setVariantDetails] = useState<VariantDetails>({
    tags: ["Zinnfigur", "Eisenbahn", "Sammler"],
    priceChanges: "",
    malgruppe: "",
    malkostenEur: "0,00€",
    malkostenCzk: "0 CZK",
    selbstkosten: "",
  });

  // Reset state when selectedItem changes (placeholder for fetching data)
  useEffect(() => {
    if (selectedItem) {
      // TODO: Fetch variants and variant details based on selectedItem
      // For now, reset to default values
      console.log("Fetching variants for product:", selectedItem);
    }
  }, [selectedItem]);

  // Search functionality
  const filteredVariants = variants.filter(
    (variant) =>
      variant.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      variant.bezeichnung.toLowerCase().includes(searchTerm.toLowerCase()) ||
      variant.auspraegung.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Sort by price
  const handleSortByPrice = () => {
    const newSortOrder = sortOrder === "asc" ? "desc" : "asc";
    // setSortOrder(newSortOrder);
    // setVariants((prev) =>
    //   [...prev].sort((a, b) =>
    //     newSortOrder === "asc" ? a.price - b.price : b.price - a.price
    //   )
    // );
  };

  // Export table data as CSV
  const handleExport = () => {
    console.log("exporting csv variants");
    const headers = [
      "Nummer",
      "Bezeichnung",
      "Ausprägung",
      "Prod.",
      "Vertr.",
      "VK Artikel",
      "Releas",
      "Price",
    ];
    const rows = filteredVariants.map((variant) => [
      variant.nummer,
      variant.bezeichnung,
      variant.auspraegung,
      variant.prod ? "Yes" : "No",
      variant.vertr ? "Yes" : "No",
      variant.vkArtikel ? "Yes" : "No",
      variant.releas,
      // variant.price.toFixed(2),
    ]);
    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.join(",")),
    ].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "variants_export.csv");
    link.click();
    URL.revokeObjectURL(url);
  };

  // Add a new variant
  const handleAddVariant = () => {
    const newVariant: Variant = {
      id: (variants.length + 1).toString(),
      nummer: `NEW${Date.now()}`,
      bezeichnung: '"Adler"-Lock',
      auspraegung: "New Variant",
      prod: false,
      vertr: false,
      vkArtikel: false,
      releas: new Date().toLocaleDateString("de-DE"),
      // price: 0,
      selected: false,
    };
    setVariants((prev) => [...prev, newVariant]);
    console.log("Added new variant:", newVariant);
    // TODO: Call API to add the new variant
  };

  // Remove selected variants
  const handleRemoveVariants = () => {
    const selectedVariants = variants.filter((variant) => variant.selected);

    // If no variants are selected, show the alert dialog
    if (selectedVariants.length === 0) {
      setIsRemoveDialogOpen(true);
      return;
    }

    // If variants are selected, proceed with removal
    setVariants((prev) => prev.filter((variant) => !variant.selected));
    console.log("Removed variants:", selectedVariants);
  };

  // Toggle selection for a variant
  const handleToggleSelect = (id: string) => {
    setVariants((prev) =>
      prev.map((variant) =>
        variant.id === id
          ? { ...variant, selected: !variant.selected }
          : variant
      )
    );
  };

  // Toggle checkbox fields (prod, vertr, vkArtikel)
  const handleToggleCheckbox = (
    id: string,
    field: "prod" | "vertr" | "vkArtikel"
  ) => {
    setVariants((prev) =>
      prev.map((variant) =>
        variant.id === id ? { ...variant, [field]: !variant[field] } : variant
      )
    );
  };

  // MoreHorizontal action (placeholder)
  const handleMoreAction = (id: string) => {
    setSelectedVariantId(id);
  };

  const handleEditVariant = () => {
    console.log("Editing variant:", selectedVariantId);
    setSelectedVariantId(null);
  };

  const handleDeleteVariant = () => {
    setVariants((prev) =>
      prev.filter((variant) => variant.id !== selectedVariantId)
    );
    console.log("Deleted variant:", selectedVariantId);
    setSelectedVariantId(null);
    // TODO: Call API to delete the variant
  };

  // Details Tab Handlers
  const handleAddTag = () => {
    const newTag = prompt("Enter new tag:");
    if (newTag) {
      setVariantDetails((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag],
      }));
    }
  };

  const handleRemoveTag = (tag: string) => {
    setVariantDetails((prev) => ({
      ...prev,
      tags: prev.tags.filter((t) => t !== tag),
    }));
  };

  const handleDetailChange = (field: keyof VariantDetails, value: string) => {
    setVariantDetails((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSaveDetails = () => {
    setIsSaveDialogOpen(true);
  };

  return (
    <div className="p-4 lg:p-6">
      <AlertDialog
        open={isRemoveDialogOpen}
        onOpenChange={setIsRemoveDialogOpen}
      >
        <AlertDialogTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="h-9 rounded-full"
            onClick={handleRemoveVariants}
          >
            <Minus className="h-4 w-4 mr-1" />
            <span>Entfernen</span>
          </Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>No Variants Selected</AlertDialogTitle>
            <AlertDialogDescription>
              Please select at least one variant to remove.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => setIsRemoveDialogOpen(false)}>
              OK
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Varianten Header */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold">Varianten</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                Verwalten Sie verschiedene Ausführungen dieses Produkts
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="h-9 rounded-full"
                onClick={handleAddVariant}
              >
                <Plus className="h-4 w-4 mr-1" />
                <span>Hinzufügen</span>
              </Button>
              <AlertDialog
                open={isRemoveDialogOpen}
                onOpenChange={setIsRemoveDialogOpen}
              >
                <AlertDialogTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-9 rounded-full"
                    onClick={handleRemoveVariants}
                  >
                    <Minus className="h-4 w-4 mr-1" />
                    <span>Entfernen</span>
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>No Variants Selected</AlertDialogTitle>
                    <AlertDialogDescription>
                      Please select at least one variant to remove.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={() => setIsRemoveDialogOpen(false)}
                    >
                      OK
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              {/* <Button
                variant="outline"
                size="sm"
                className="h-9 rounded-full"
                onClick={handleRemoveVariants}
              >
                <Minus className="h-4 w-4 mr-1" />
                <span>Entfernen</span>
              </Button> */}
            </div>
          </div>
        </div>

        {/* Varianten Table with Search and Export */}
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
          <div className="p-4 border-b border-slate-200 dark:border-slate-800">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div className="relative w-full sm:w-64">
                <Input
                  className="pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-blue-500"
                  placeholder="Suchen..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <div className="absolute left-3 top-1/2 -translate-y-1/2">
                  <Search className="h-4 w-4 text-slate-400" />
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="h-9 rounded-full"
                onClick={handleExport}
              >
                <Download className="h-4 w-4 mr-1" />
                Exportieren
              </Button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
                      checked={variants.every((v) => v.selected)}
                      onChange={() =>
                        setVariants((prev) =>
                          prev.map((v) => ({
                            ...v,
                            selected: !variants.every((v) => v.selected),
                          }))
                        )
                      }
                      className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                    />
                  </TableHead>
                  <TableHead className="font-medium">Nummer</TableHead>
                  <TableHead className="font-medium">Bezeichnung</TableHead>
                  <TableHead className="font-medium">Ausprägung</TableHead>
                  <TableHead className="w-12 text-center font-medium">
                    Prod.
                  </TableHead>
                  <TableHead className="w-12 text-center font-medium">
                    Vertr.
                  </TableHead>
                  <TableHead className="w-12 text-center font-medium">
                    VK Artikel
                  </TableHead>
                  <TableHead className="font-medium">Releas</TableHead>
                  {/* <TableHead className="font-medium">
                    <div className="flex items-center gap-1">
                      Price
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6"
                        onClick={handleSortByPrice}
                      >
                        <ArrowUpDown className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableHead> */}
                  <TableHead className="w-10"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredVariants.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={10} className="text-center py-4">
                      Keine Varianten gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredVariants.map((variant) => (
                    <TableRow
                      key={variant.id}
                      className={
                        variant.selected
                          ? "bg-blue-50/50 dark:bg-blue-900/10"
                          : ""
                      }
                    >
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={variant.selected}
                          onChange={() => handleToggleSelect(variant.id)}
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                        />
                      </TableCell>
                      <TableCell className="font-medium">
                        {variant.nummer}
                      </TableCell>
                      <TableCell>{variant.bezeichnung}</TableCell>
                      <TableCell>{variant.auspraegung}</TableCell>
                      <TableCell className="text-center">
                        <input
                          type="checkbox"
                          checked={variant.prod}
                          onChange={() =>
                            handleToggleCheckbox(variant.id, "prod")
                          }
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                        />
                      </TableCell>
                      <TableCell className="text-center">
                        <input
                          type="checkbox"
                          checked={variant.vertr}
                          onChange={() =>
                            handleToggleCheckbox(variant.id, "vertr")
                          }
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                        />
                      </TableCell>
                      <TableCell className="text-center">
                        <input
                          type="checkbox"
                          checked={variant.vkArtikel}
                          onChange={() =>
                            handleToggleCheckbox(variant.id, "vkArtikel")
                          }
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                        />
                      </TableCell>
                      <TableCell>{variant.releas}</TableCell>
                      {/* <TableCell>{variant.price.toFixed(2)} €</TableCell> */}
                      <TableCell >
                        <AlertDialog
                          open={selectedVariantId === variant.id}
                          onOpenChange={(open) =>
                            !open && setSelectedVariantId(null)
                          }
                        >
                          <AlertDialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 rounded-full"
                              onClick={() => handleMoreAction(variant.id)}
                            >
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>
                                Aktionen für Variante {selectedVariantId}
                              </AlertDialogTitle>
                              <AlertDialogDescription>
                                Wählen Sie eine Aktion für diese Variante aus.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter className="flex flex-col sm:flex-row sm:justify-end gap-2">
                              <Button
                                variant="outline"
                                onClick={handleEditVariant}
                              >
                                Bearbeiten
                              </Button>
                              <Button
                                variant="destructive"
                                onClick={handleDeleteVariant}
                              >
                                Löschen
                              </Button>
                              <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Varianten Tabs */}
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
          <Tabs
            defaultValue="details"
            value={variantenActiveTab}
            onValueChange={setVariantenActiveTab}
            className="w-full"
          >
            <div className="border-b border-slate-200 dark:border-slate-800 overflow-x-auto">
              <TabsList className="bg-slate-50 dark:bg-slate-800/50 h-auto p-2 rounded-none flex-nowrap">
                <TabsTrigger
                  value="details"
                  className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                >
                  Details
                </TabsTrigger>
                <TabsTrigger
                  value="teile"
                  className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                >
                  Teile
                </TabsTrigger>
                <TabsTrigger
                  value="bilder"
                  className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                >
                  Bilder
                </TabsTrigger>
                <TabsTrigger
                  value="gewogen"
                  className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                >
                  Gewogen
                </TabsTrigger>
                <TabsTrigger
                  value="lagerorte"
                  className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                >
                  Lagerorte
                </TabsTrigger>
                <TabsTrigger
                  value="umsatze"
                  className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                >
                  Umsätze
                </TabsTrigger>
                <TabsTrigger
                  value="bewegungen"
                  className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-900 rounded-lg data-[state=active]:shadow-sm whitespace-nowrap"
                >
                  Bewegungen
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="details" className="p-0 m-0">
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                    <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                      <CardTitle className="text-sm font-medium">
                        Tags
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="p-4">
                        <div className="flex flex-wrap gap-2 mb-4">
                          {variantDetails.tags.map((tag) => (
                            <Badge
                              key={tag}
                              variant="secondary"
                              className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                            >
                              <Tag className="h-3 w-3 mr-1" />
                              {tag}
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-4 w-4 ml-1"
                                onClick={() => handleRemoveTag(tag)}
                              >
                                <Minus className="h-3 w-3" />
                              </Button>
                            </Badge>
                          ))}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full rounded-lg"
                          onClick={handleAddTag}
                        >
                          <Plus className="h-3.5 w-3.5 mr-1" />
                          Tag hinzufügen
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                    <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                      <CardTitle className="text-sm font-medium">
                        Publish
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Status</span>
                          <Badge className="bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                            Aktiv
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Sichtbarkeit</span>
                          <Badge className="bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                            Öffentlich
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Erstellt am</span>
                          <span className="text-sm">01.01.2023</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Aktualisiert am</span>
                          <span className="text-sm">22.10.2024</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                    <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                      <CardTitle className="text-sm font-medium">
                        Preise
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4">
                      <select className="w-full p-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 mb-3">
                        <option>DE - 19% Germany</option>
                      </select>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Laden</span>
                          <span className="text-sm font-medium">37,40 €</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Handel</span>
                          <span className="text-sm font-medium">17,30 €</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Empf.</span>
                          <span className="text-sm font-medium">29,50 €</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Einkauf</span>
                          <span className="text-sm font-medium">9,63 €</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card className="border border-slate-200 dark:border-slate-700 shadow-sm mb-6">
                  <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                    <CardTitle className="text-sm font-medium">
                      Preisänderungen
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <textarea
                      value={variantDetails.priceChanges}
                      onChange={(e) =>
                        handleDetailChange("priceChanges", e.target.value)
                      }
                      className="w-full border border-slate-200 dark:border-slate-700 rounded-lg p-3 h-24 resize-none bg-slate-50 dark:bg-slate-800"
                    />
                  </CardContent>
                </Card>

                <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
                  <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                    <CardTitle className="text-sm font-medium">
                      Zusätzliche Informationen
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                          Malgruppe
                        </label>
                        <div className="md:col-span-3">
                          <Input
                            value={variantDetails.malgruppe}
                            onChange={(e) =>
                              handleDetailChange("malgruppe", e.target.value)
                            }
                            className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                          Malkosten
                        </label>
                        <div className="md:col-span-3 flex gap-3">
                          <Input
                            value={variantDetails.malkostenEur}
                            onChange={(e) =>
                              handleDetailChange("malkostenEur", e.target.value)
                            }
                            className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                          />
                          <Input
                            value={variantDetails.malkostenCzk}
                            onChange={(e) =>
                              handleDetailChange("malkostenCzk", e.target.value)
                            }
                            className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                        <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                          Selbstkosten
                        </label>
                        <div className="md:col-span-3">
                          <Input
                            value={variantDetails.selbstkosten}
                            onChange={(e) =>
                              handleDetailChange("selbstkosten", e.target.value)
                            }
                            className="w-full md:w-1/3 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Save Button for Details Tab */}
                {/* <div className="mt-6 flex justify-end">
                  <Button
                    className="rounded-full bg-blue-600 hover:bg-blue-700 text-white"
                    onClick={handleSaveDetails}
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Speichern
                  </Button>
                </div> */}
                <div className="mt-6 flex justify-end">
                  <AlertDialog
                    open={isSaveDialogOpen}
                    onOpenChange={setIsSaveDialogOpen}
                  >
                    <AlertDialogTrigger asChild>
                      <Button
                        className="rounded-full bg-blue-600 hover:bg-blue-700 text-white"
                        onClick={() => {
                          console.log(
                            "Saving variant details:",
                            variantDetails
                          );
                          handleSaveDetails();
                          // TODO: Call API to save variant details
                        }}
                      >
                        <Zap className="h-4 w-4 mr-2" />
                        Speichern
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Details gespeichert</AlertDialogTitle>
                        <AlertDialogDescription>
                          Die Variantendetails wurden erfolgreich gespeichert.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Schließen</AlertDialogCancel>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </TabsContent>
            <TabsContent value="teile" className="p-0 m-0">
              <TeileTab />
            </TabsContent>
            <TabsContent value="bilder" className="p-0 m-0">
              <BilderTab />
            </TabsContent>
            <TabsContent value="gewogen" className="p-0 m-0">
              <GewogenTab />
            </TabsContent>
            <TabsContent value="lagerorte" className="p-0 m-0">
              <LagerorteTab />
            </TabsContent>
            <TabsContent value="umsatze" className="p-0 m-0">
              <UmsatzeTab />
            </TabsContent>
            <TabsContent value="bewegungen" className="p-0 m-0">
              <BewegungenTab />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
