"use client";

import { useState, useEffect } from "react";
import { useTechnologies } from "@/hooks/mold/use-technologies";
import { useMoldSizes } from "@/hooks/mold/use-mold-sizes";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { X, Check, Minus, AlertTriangle } from "lucide-react";
import {
  moldFormSchema,
  type MoldFormValues,
} from "@/components/mold/form/mold-form-schema";
import type { Mold } from "@/types/mold/mold";
import { MoldActivityStatus } from "@/types/mold/mold";
import type { Technology } from "@/types/mold/technology";
import type { Alloy } from "@/types/mold/alloy";
import type { Tag } from "@/types/mold/tag";
import type { MoldSize } from "@/types/mold/mold-size";
import { useArticles } from "@/hooks/mold/use-articles";
import { useWarehouseLocations } from "@/hooks/mold/use-warehouse-locations";
import { generateMoldNumber } from "@/lib/mold/utils";
import { ArticleStatus } from "@/types/mold/article";
import { GeneralTab } from "./mold-form/general-tab";
import { ArticlesTab } from "./mold-form/articles-tab";
import { WarehouseLocationDialog } from "./mold-form/warehouse-location-dialog";
import { BarcodeScannerDialog } from "./mold-form/barcode-scanner-dialog";
import {
  ArticleFormDialog,
  type ArticleFormValues,
} from "./mold-form/article-form-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props for the MoldFormDialog component
 */
interface MoldFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit" | "duplicate";
  mold: Mold | null;
  technologies: Technology[];
  alloys: Alloy[];
  tags: Tag[];
  moldSizes: MoldSize[];
  onSubmit: (data: MoldFormValues) => Promise<void>;
}

/**
 * MoldFormDialog component provides a dialog for creating, editing, or duplicating molds
 */
export default function MoldFormDialog({
  open,
  onOpenChange,
  mode,
  mold,
  technologies,
  alloys,
  tags,
  moldSizes,
  onSubmit,
}: MoldFormDialogProps) {
  // State for form submission
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { t } = useAppTranslation("mold");

  // State for active tab
  const [activeTab, setActiveTab] = useState("general");

  // State for dialogs
  const [showLocationDialog, setShowLocationDialog] = useState(false);
  const [showBarcodeDialog, setShowBarcodeDialog] = useState(false);
  const [showArticleDialog, setShowArticleDialog] = useState(false);

  // State for temporary mold ID and articles
  const [tempMoldId, setTempMoldId] = useState<string>("");
  const [tempArticles, setTempArticles] = useState<any[]>([]);

  // State für den aktuellen Mold mit aktualisierten Daten
  const [currentMold, setCurrentMold] = useState<Mold | null>(null);

  // State für neue Technologie
  const [showTechnologyDialog, setShowTechnologyDialog] = useState(false);
  const [newTechnologyName, setNewTechnologyName] = useState("");

  // State für neue Mold Size
  const [showMoldSizeDialog, setShowMoldSizeDialog] = useState(false);
  const [newMoldSize, setNewMoldSize] = useState({
    name: "",
    description: "",
  });

  // Hole die Technologie- und MoldSize-Funktionen
  const { createTechnology, deleteTechnology } = useTechnologies();
  const { createMoldSize, deleteMoldSize } = useMoldSizes();

  // Initialize form with react-hook-form and zod validation
  const form = useForm<MoldFormValues>({
    resolver: zodResolver(moldFormSchema),
    defaultValues: {
      legacyMoldNumber: "",
      moldNumber: "",
      technology: "",
      alloy: "",
      warehouseLocation: "",
      numberOfArticles: 0,
      isActive: true,
      tags: [],
      startDate: "",
      endDate: "",
      imageUrl: "",
      moldSize: "",
    },
  });

  // Fetch articles and warehouse locations
  const { data: articles } = useArticles(
    mode === "edit" || mode === "duplicate" ? mold?.id : tempMoldId
  );
  const { data: warehouseLocations } = useWarehouseLocations();

  // Funktion zur Berechnung des Aktivitätsstatus basierend auf Artikeln
  const determineActivityStatus = (
    moldId: string | null,
    articles: any[] | undefined
  ) => {
    if (!moldId || !articles || articles.length === 0) {
      return MoldActivityStatus.INACTIVE;
    }

    const moldArticles = articles.filter(
      (article) => article.moldId === moldId
    );

    if (moldArticles.length === 0) {
      return MoldActivityStatus.INACTIVE;
    }

    const activeCount = moldArticles.filter(
      (a) =>
        a.status === ArticleStatus.ACTIVE || a.status === ArticleStatus.MIXED
    ).length;

    if (activeCount === 0) {
      return MoldActivityStatus.INACTIVE;
    } else if (activeCount === moldArticles.length) {
      // Prüfen, ob alle Artikel vollständig aktiv sind
      const fullyActiveCount = moldArticles.filter(
        (a) => a.status === ArticleStatus.ACTIVE
      ).length;
      if (fullyActiveCount === moldArticles.length) {
        return MoldActivityStatus.ACTIVE;
      } else {
        return MoldActivityStatus.MIXED;
      }
    } else {
      return MoldActivityStatus.MIXED;
    }
  };

  // Aktualisiere den Status basierend auf den Artikeln, wenn sich der Tab ändert
  useEffect(() => {
    if (mode === "edit" && mold && articles) {
      const status = determineActivityStatus(mold.id, articles);

      // Aktualisiere den currentMold mit dem berechneten Status
      setCurrentMold({
        ...mold,
        activityStatus: status,
        isActive: status !== MoldActivityStatus.INACTIVE,
      });

      // Aktualisiere das Formular mit dem berechneten Status
      form.setValue("isActive", status !== MoldActivityStatus.INACTIVE);
    }
  }, [activeTab, articles, mold, mode, form]);

  // Reset form when dialog opens/closes or mode changes
  useEffect(() => {
    if (open) {
      // Generate a temporary ID for new molds
      if (mode === "create") {
        setTempMoldId(`temp-${Math.random().toString(36).substring(2, 9)}`);
        setTempArticles([]);
      }

      if (mode === "create") {
        // Automatically generate a mold number for new molds
        const newMoldNumber = generateMoldNumber();

        form.reset({
          legacyMoldNumber: "",
          moldNumber: newMoldNumber,
          technology: "",
          alloy: "",
          warehouseLocation: "",
          numberOfArticles: 0,
          isActive: true,
          tags: [],
          startDate: "",
          endDate: "",
          imageUrl: "",
          moldSize: "",
        });
      } else if (mold) {
        // Berechne den Status basierend auf den Artikeln
        if (articles) {
          const status = determineActivityStatus(mold.id, articles);

          // Setze den aktuellen Mold mit dem berechneten Status
          setCurrentMold({
            ...mold,
            activityStatus: status,
            isActive: status !== MoldActivityStatus.INACTIVE,
          });

          // For edit mode, use the existing mold data with updated status
          // For duplicate mode, use the existing mold data but generate a new mold number
          form.reset({
            ...mold,
            moldNumber:
              mode === "duplicate" ? generateMoldNumber() : mold.moldNumber,
            tags: mold.tags || [],
            isActive: status !== MoldActivityStatus.INACTIVE,
          });
        } else {
          // Wenn noch keine Artikel geladen sind, verwende die vorhandenen Daten
          setCurrentMold(mold);

          // For edit mode, use the existing mold data
          // For duplicate mode, use the existing mold data but generate a new mold number
          form.reset({
            ...mold,
            moldNumber:
              mode === "duplicate" ? generateMoldNumber() : mold.moldNumber,
            tags: mold.tags || [],
          });
        }
      }
    }
  }, [open, mode, mold, form, articles]);

  // Update numberOfArticles when articles or tempArticles change
  useEffect(() => {
    if (mode === "create") {
      form.setValue("numberOfArticles", tempArticles.length);
    } else if (articles && articles.length > 0) {
      // Count unique article numbers
      const uniqueArticles = new Set(
        articles.map((article) => article.newArticleNumber)
      );
      form.setValue("numberOfArticles", uniqueArticles.size);
    }
  }, [articles, tempArticles, form, mode]);

  /**
   * Handle form submission
   */
  const handleSubmit = async (data: MoldFormValues) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);

      // If creating a new mold and there are temporary articles, create them
      if (mode === "create" && tempArticles.length > 0) {
        // In a real application, this would be handled by the backend
        console.log(
          "Articles will be created after mold is saved:",
          tempArticles
        );
      }
    } catch (error) {
      console.error("Error submitting form:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle article form submission
   */
  const handleArticleSubmit = (data: ArticleFormValues) => {
    // Add the article to temporary articles for new molds
    if (mode === "create") {
      setTempArticles([
        ...tempArticles,
        {
          ...data,
          id: `temp-${Math.random().toString(36).substring(2, 9)}`,
          moldId: tempMoldId,
        },
      ]);
    }
    setShowArticleDialog(false);
  };

  /**
   * Handle barcode validation and selection
   */
  const handleBarcodeSubmit = (scannedBarcode: string) => {
    // Check if the barcode exists in our warehouse locations
    const matchingLocation = warehouseLocations?.find(
      (loc) => loc.laNumber.toLowerCase() === scannedBarcode.toLowerCase()
    );

    if (matchingLocation) {
      // If found, set the warehouse location
      form.setValue(
        "warehouseLocation",
        `${matchingLocation.laNumber} - ${matchingLocation.location}`
      );
    } else {
      // If not found, set the raw barcode
      form.setValue("warehouseLocation", scannedBarcode);
    }
    setShowBarcodeDialog(false);
  };

  /**
   * Render the status icon for an article
   */
  const renderArticleStatusIcon = (status: ArticleStatus) => {
    switch (status) {
      case ArticleStatus.ACTIVE:
        return <Check className="h-4 w-4 text-green-500" />;
      case ArticleStatus.INACTIVE:
        return <Minus className="h-4 w-4 text-amber-500" />;
      case ArticleStatus.DISCONTINUED:
        return <X className="h-4 w-4 text-red-500" />;
      case ArticleStatus.MIXED:
        return <AlertTriangle className="h-4 w-4 text-blue-500" />;
    }
  };

  /**
   * Get the dialog title based on the mode
   */
  const getDialogTitle = () => {
    switch (mode) {
      case "create":
        return t("dialog_title_create");
      case "edit":
        return t("dialog_title_edit");
      case "duplicate":
        return t("dialog_title_duplicate");
      default:
        return t("dialog_title_default");
    }
  };

  // Funktion zum Hinzufügen einer neuen Technologie
  const handleAddTechnology = () => {
    setShowTechnologyDialog(true);
  };

  // Funktion zum Speichern einer neuen Technologie
  const handleSaveTechnology = async () => {
    if (newTechnologyName.trim() === "") return;

    try {
      await createTechnology({ name: newTechnologyName });
      setNewTechnologyName("");
      setShowTechnologyDialog(false);
      // Aktualisiere die Technologien
      //queryClient.invalidateQueries({ queryKey: ["technologies"] })
    } catch (error) {
      console.error("Failed to create technology:", error);
    }
  };

  // Funktion zum Löschen einer Technologie
  const handleDeleteTechnology = async (name: string) => {
    try {
      // Finde die Technologie anhand des Namens
      const tech = technologies.find((t) => t.name === name);
      if (tech) {
        await deleteTechnology(tech.id);
        // Aktualisiere die Technologien
        //queryClient.invalidateQueries({ queryKey: ["technologies"] })
      }
    } catch (error) {
      console.error("Failed to delete technology:", error);
    }
  };

  // Funktion zum Hinzufügen einer neuen Mold Size
  const handleAddMoldSize = () => {
    setShowMoldSizeDialog(true);
  };

  // Funktion zum Speichern einer neuen Mold Size
  const handleSaveMoldSize = async () => {
    if (newMoldSize.name.trim() === "") return;

    try {
      await createMoldSize(newMoldSize);
      setNewMoldSize({ name: "", description: "" });
      setShowMoldSizeDialog(false);
      // Aktualisiere die Mold Sizes
      //queryClient.invalidateQueries({ queryKey: ["moldSizes"] })
    } catch (error) {
      console.error("Failed to create mold size:", error);
    }
  };

  // Funktion zum Löschen einer Mold Size
  const handleDeleteMoldSize = async (name: string) => {
    try {
      // Finde die Mold Size anhand des Namens
      const size = moldSizes.find((s) => s.name === name);
      if (size) {
        await deleteMoldSize(size.id);
        // Aktualisiere die Mold Sizes
        //queryClient.invalidateQueries({ queryKey: ["moldSizes"] })
      }
    } catch (error) {
      console.error("Failed to delete mold size:", error);
    }
  };

  // If the dialog is not open, don't render anything
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm">
      <div className="fixed inset-0 z-50 flex items-start justify-center">
        <div className="flex flex-col w-full h-full bg-background">
          {/* Header */}
          <div className="flex items-center justify-between border-b p-4 md:p-6">
            <div>
              <h2 className="text-xl md:text-2xl font-bold">
                {getDialogTitle()}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                {mode === "create"
                  ? t("dialog_description_create")
                  : mode === "edit"
                  ? t("dialog_description_edit")
                  : t("dialog_description_duplicate")}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onOpenChange(false)}
              className="h-8 w-8 rounded-full"
              type="button"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-auto p-4 md:p-6">
            <div className="container max-w-6xl mx-auto">
              <Tabs
                value={activeTab}
                onValueChange={setActiveTab}
                className="w-full"
              >
                <TabsList className="w-full max-w-md mb-6">
                  <TabsTrigger value="general" className="flex-1">
                  {t("tab_general_information")}
                  </TabsTrigger>
                  <TabsTrigger value="articles" className="flex-1">
                  {t("tab_articles")}
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="general" className="space-y-6">
                  <GeneralTab
                    form={form}
                    mode={mode}
                    mold={currentMold || mold}
                    technologies={technologies}
                    alloys={alloys}
                    tags={tags}
                    moldSizes={moldSizes}
                    onSubmit={handleSubmit}
                    onScanBarcode={() => setShowBarcodeDialog(true)}
                    onOpenLocationDialog={() => setShowLocationDialog(true)}
                    onAddTechnology={handleAddTechnology}
                    onDeleteTechnology={handleDeleteTechnology}
                    onAddMoldSize={handleAddMoldSize}
                    onDeleteMoldSize={handleDeleteMoldSize}
                  />
                </TabsContent>

                <TabsContent value="articles" className="py-4">
                  <ArticlesTab
                    mode={mode}
                    moldId={mold?.id || null}
                    tempArticles={tempArticles}
                    onAddArticle={() => setShowArticleDialog(true)}
                    renderArticleStatusIcon={renderArticleStatusIcon}
                  />
                </TabsContent>
              </Tabs>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t p-4 md:p-6 flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
              type="button"
            >
              Cancel
            </Button>
            <Button type="submit" form="mold-form" disabled={isSubmitting}>
              {isSubmitting
                ? t("saving")
                : mode === "create"
                ? t("dialog_submit_create")
                : mode === "edit"
                ? t("dialog_submit_edit")
                : t("dialog_submit_duplicate")}
            </Button>
          </div>
        </div>
      </div>

      {/* Dialogs */}
      <WarehouseLocationDialog
        open={showLocationDialog}
        onOpenChange={setShowLocationDialog}
        locations={warehouseLocations || []}
        onSelect={(location) => {
          form.setValue("warehouseLocation", location);
          setShowLocationDialog(false);
        }}
      />

      <BarcodeScannerDialog
        open={showBarcodeDialog}
        onOpenChange={setShowBarcodeDialog}
        onSubmit={handleBarcodeSubmit}
      />

      <ArticleFormDialog
        open={showArticleDialog}
        onOpenChange={setShowArticleDialog}
        onSubmit={handleArticleSubmit}
      />

      {/* Dialog zum Hinzufügen einer neuen Technologie */}
      <Dialog
        open={showTechnologyDialog}
        onOpenChange={setShowTechnologyDialog}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{t("new_purpose")}</DialogTitle>
            <DialogDescription>
              {t("enter_name")}
            </DialogDescription>
          </DialogHeader>
          <div className="flex items-center space-x-2 py-4">
            <Input
              placeholder="Name des Zwecks"
              value={newTechnologyName}
              onChange={(e) => setNewTechnologyName(e.target.value)}
              className="flex-1"
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowTechnologyDialog(false)}
            >
              {t("cancel_button")}
            </Button>
            <Button onClick={handleSaveTechnology}>Hinzufügen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog zum Hinzufügen einer neuen Mold Size */}
      <Dialog open={showMoldSizeDialog} onOpenChange={setShowMoldSizeDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{t("add_size")}</DialogTitle>
            <DialogDescription>
              {t("enter_optional_name")}
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col space-y-4 py-4">
            <Input
              placeholder="Name der Größe"
              value={newMoldSize.name}
              onChange={(e) =>
                setNewMoldSize({ ...newMoldSize, name: e.target.value })
              }
              className="flex-1"
            />
            <Textarea
              placeholder={t("new_mold_size_description_placeholder")}
              value={newMoldSize.description}
              onChange={(e) =>
                setNewMoldSize({ ...newMoldSize, description: e.target.value })
              }
              className="flex-1 min-h-[100px]"
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowMoldSizeDialog(false)}
            >
              {t("cancel_button")}
            </Button>
            <Button onClick={handleSaveMoldSize}>{t("add_button")}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
