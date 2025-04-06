// components/ProductDetail/VariantenTab.tsx
import { useState, useEffect } from "react";
// import VariantenHeader from "@/components/ProductDetail/VariantenHeader";
// import VariantenTable from "@/components/ProductDetail/VariantenTable";
// import VariantenTabs from "@/components/ProductDetail/VariantenTabs";
// import DetailsTab from "@/components/ProductDetail/DetailsTab";

import VariantenHeader from "../variants/VariantenHeader";
import VariantenTable from "../variants/VariantenTable";
import VariantenTabs from "../variants/VariantenTabs";
import DetailsTab from "../variants/DetailsTab";
import { SelectedItem } from "@/components/types/product";
import { Button } from "@/components/ui/button";
import { Edit, X, Zap } from "lucide-react";
import useAppTranslation from "@/hooks/useTranslationWrapper";

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

interface VariantenTabProps extends SelectedItem {
  canEdit?: boolean;
}

export default function VariantenTab({ selectedItem, canEdit = false }: VariantenTabProps) {
  const [variantenActiveTab, setVariantenActiveTab] = useState("details");
  const [searchTerm, setSearchTerm] = useState("");
  const [variants, setVariants] = useState<Variant[]>([]);
  const [selectedVariantDetails, setSelectedVariantDetails] = useState<VariantDetails | null>(null);
  const [initialVariantDetails, setInitialVariantDetails] = useState<VariantDetails | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { t } = useAppTranslation("varianteTab");

  useEffect(() => {
    if (selectedItem) {
      const fetchedDetails: VariantDetails = {
        tags: ["Zinnfigur", "Eisenbahn", "Sammler"],
        priceChanges: "Placeholder price change info",
        malgruppe: "Placeholder Malgruppe",
        malkostenEur: "1.23€",
        malkostenCzk: "30 CZK",
        selbstkosten: "0.99€",
      };
      setSelectedVariantDetails(fetchedDetails);
      setInitialVariantDetails(JSON.parse(JSON.stringify(fetchedDetails)));
      setIsEditing(false);
    } else {
      setSelectedVariantDetails(null);
      setInitialVariantDetails(null);
      setIsEditing(false);
    }
  }, [selectedItem]);

  useEffect(() => {
    if (isEditing && selectedVariantDetails) {
        setInitialVariantDetails(JSON.parse(JSON.stringify(selectedVariantDetails)));
    }
  }, [isEditing]);

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

  const handleAddVariant = (newVariant: Variant) => {
    setVariants([...variants, newVariant]);
  };

  const handleRemoveVariants = () => {
    setVariants(variants.filter((v) => !v.selected));
  };

  const handleToggleSelect = (id: string) => {
    setVariants(
      variants.map((v) => (v.id === id ? { ...v, selected: !v.selected } : v))
    );
    console.log("Variant selected: ", id);
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

  const handleEdit = () => {
    if (selectedVariantDetails) {
      setInitialVariantDetails(JSON.parse(JSON.stringify(selectedVariantDetails)));
      setIsEditing(true);
      setError(null);
    }
  };

  const handleCancel = () => {
    if (initialVariantDetails) {
       setSelectedVariantDetails(JSON.parse(JSON.stringify(initialVariantDetails)));
    }
    setIsEditing(false);
    setError(null);
  };

  const handleSaveDetails = async () => {
    if (!selectedVariantDetails || !selectedItem) {
      setError("No variant selected or details available to save.");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      console.log("Saving variant details for ID:", selectedItem, selectedVariantDetails);
      await new Promise(resolve => setTimeout(resolve, 1000));

      alert("Variant details saved successfully!");
      setIsEditing(false);
      setInitialVariantDetails(JSON.parse(JSON.stringify(selectedVariantDetails)));
    } catch (err: any) {
      console.error("Error saving variant details:", err);
      setError(`Failed to save variant details: ${err.message || "Unknown error"}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddTag = () => {
    if (!isEditing) return;
    const newTag = prompt("Enter new tag:");
    if (newTag && selectedVariantDetails) {
        setSelectedVariantDetails(prev => prev ? {...prev, tags: [...prev.tags, newTag]} : null);
    }
  };

  const handleRemoveTag = (tag: string) => {
    if (!isEditing) return;
    if (selectedVariantDetails) {
        setSelectedVariantDetails(prev => prev ? {...prev, tags: prev.tags.filter(t => t !== tag)} : null);
    }
  };

  const handleDetailChange = (field: keyof VariantDetails, value: string) => {
    if (!isEditing) return;
    setSelectedVariantDetails(prev => prev ? {...prev, [field]: value} : null);
  };

  return (
    <div>
      <div className="max-w-5xl mx-auto space-y-8 ">
        <VariantenHeader
          onAddVariant={handleAddVariant}
          onRemoveVariants={handleRemoveVariants}
          variants={variants}
        />
        <VariantenTable
          variants={variants}
          setVariants={setVariants}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          onExport={(filteredVariants: Variant[]) => handleExport(filteredVariants)}
          onToggleSelect={handleToggleSelect}
          onToggleCheckbox={handleToggleCheckbox}
          onMoreAction={handleMoreAction}
          onEditVariant={handleEditVariant}
          onDeleteVariant={handleDeleteVariant}
        />

        {selectedVariantDetails && (
          <>
            <div className="flex justify-end gap-2 mb-4">
              {!isEditing && canEdit && (
                <Button
                  onClick={handleEdit}
                  variant="outline"
                  className="rounded-full"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  {t("editVariantDetails", "Edit Details")}
                </Button>
              )}
              {isEditing && (
                <>
                  <Button
                    variant="outline"
                    className="rounded-full"
                    onClick={handleCancel}
                    disabled={isSaving}
                  >
                    <X className="h-4 w-4 mr-2" />
                    {t("cancel", "Cancel")}
                  </Button>
                  <Button
                    variant="default"
                    className="rounded-full"
                    onClick={handleSaveDetails}
                    disabled={isSaving}
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    {isSaving ? t("saving", "Saving...") : t("saveVariantDetails", "Save Details")}
                  </Button>
                </>
              )}
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                {error}
              </div>
            )}

            <VariantenTabs
              activeTab={variantenActiveTab}
              onTabChange={setVariantenActiveTab}
              detailsTab={
                <DetailsTab
                  variantDetails={selectedVariantDetails}
                  onDetailChange={handleDetailChange}
                  onAddTag={handleAddTag}
                  onRemoveTag={handleRemoveTag}
                  isEditing={isEditing}
                />
              }
            />
          </>
        )}
        {!selectedVariantDetails && (
            <div className="text-center py-10 text-slate-500">
                Select a variant from the table above to view details.
            </div>
        )}
      </div>
    </div>
  );
}
