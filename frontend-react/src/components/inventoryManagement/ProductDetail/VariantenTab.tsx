// components/ProductDetail/VariantenTab.tsx
import { useState } from "react";
// import VariantenHeader from "@/components/ProductDetail/VariantenHeader";
// import VariantenTable from "@/components/ProductDetail/VariantenTable";
// import VariantenTabs from "@/components/ProductDetail/VariantenTabs";
// import DetailsTab from "@/components/ProductDetail/DetailsTab";

import VariantenHeader from "../variants/VariantenHeader";
import VariantenTable from "../variants/VariantenTable";
import VariantenTabs from "../variants/VariantenTabs";
import DetailsTab from "../variants/DetailsTab";

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
  const [variants, setVariants] = useState<Variant[]>([]);
  const [variantDetails, setVariantDetails] = useState<VariantDetails>({
    tags: ["Zinnfigur", "Eisenbahn", "Sammler"],
    priceChanges: "",
    malgruppe: "",
    malkostenEur: "0,00€",
    malkostenCzk: "0 CZK",
    selbstkosten: "",
  });

  const handleExport = (filteredVariants: Variant[]) => {
    const headers = [
      "Nummer",
      "Bezeichnung",
      "Ausprägung",
      "Prod.",
      "Vertr.",
      "VK Artikel",
      "Releas",
    ];
    const rows = filteredVariants.map((variant) => [
      variant.nummer,
      variant.bezeichnung,
      variant.auspraegung,
      variant.prod ? "Yes" : "No",
      variant.vertr ? "Yes" : "No",
      variant.vkArtikel ? "Yes" : "No",
      variant.releas,
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

  // Add Variant
  const handleAddVariant = (newVariant: Variant) => {
    setVariants([...variants, newVariant]);
  };

  // Remove Selected Variants
  const handleRemoveVariants = () => {
    setVariants(variants.filter((v) => !v.selected));
  };

  // Toggle Select
  const handleToggleSelect = (id: string) => {
    setVariants(
      variants.map((v) => (v.id === id ? { ...v, selected: !v.selected } : v))
    );
  };

  const handleToggleCheckbox = (
    id: string,
    field: "prod" | "vertr" | "vkArtikel"
  ) => {
    // Toggle checkbox logic
  };

  const handleMoreAction = (id: string) => {
    // More action logic
  };

  const handleEditVariant = () => {
    // Edit variant logic
  };

  const handleDeleteVariant = () => {
    // Delete variant logic
  };

  const handleAddTag = () => {
    // Add tag logic
  };

  const handleRemoveTag = (tag: string) => {
    // Remove tag logic
  };

  const handleDetailChange = (field: keyof VariantDetails, value: string) => {
    // Handle detail change logic
  };

  const handleSaveDetails = () => {
    // Save details logic
  };

  return (
    <div className="p-4 lg:p-6 ">
      <div className="max-w-5xl mx-auto space-y-8 ">
        <VariantenHeader
          onAddVariant={handleAddVariant}
          onRemoveVariants={handleRemoveVariants}
          variants={variants} // Pass variants to check selection
        />
        <VariantenTable
          variants={variants}
          setVariants={setVariants}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          onExport={(filteredVariants: Variant[]) => handleExport(filteredVariants)} // Pass filteredVariants
          onToggleSelect={handleToggleSelect}
          onToggleCheckbox={handleToggleCheckbox}
          onMoreAction={handleMoreAction}
          onEditVariant={handleEditVariant}
          onDeleteVariant={handleDeleteVariant}
        />
        <VariantenTabs
          activeTab={variantenActiveTab}
          onTabChange={setVariantenActiveTab}
          detailsTab={
            <DetailsTab
              variantDetails={variantDetails}
              onDetailChange={handleDetailChange}
              onAddTag={handleAddTag}
              onRemoveTag={handleRemoveTag}
              onSaveDetails={handleSaveDetails}
            />
          }
        />
      </div>
    </div>
  );
}
