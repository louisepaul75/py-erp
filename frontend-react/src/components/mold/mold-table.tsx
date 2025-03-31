"use client";

import { useState, useEffect } from "react";
import { Table, TableBody } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { TableRow, TableCell } from "@/components/ui/table";
import { useQueryClient } from "@tanstack/react-query";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useMolds } from "@/hooks/mold/use-molds";
import { useTechnologies } from "@/hooks/mold/use-technologies";
import { useAlloys } from "@/hooks/mold/use-alloys";
import { useTags } from "@/hooks/mold/use-tags";
import { useMoldSizes } from "@/hooks/mold/use-mold-sizes";
import MoldFormDialog from "@/components/mold/mold-form-dialog";
import type { Mold } from "@/types/mold/mold";
import { MoldTableHeader } from "./mold/mold-table-header";
import { MoldTableRow } from "./mold/mold-table-row";
import { MoldTableActions } from "./mold/mold-table-actions";
import { FilterBadges } from "./mold/filter-badges";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * MoldTable component displays a table of molds with filtering and action capabilities
 */
export default function MoldTable() {
  // State for selected mold (for duplication or editing)
  const [selectedMold, setSelectedMold] = useState<Mold | null>(null);

  // State for form dialog visibility
  const [showFormDialog, setShowFormDialog] = useState(false);

  const { t } = useAppTranslation("mold");

  // State for form mode (create, edit, duplicate)
  const [formMode, setFormMode] = useState<"create" | "edit" | "duplicate">(
    "create"
  );

  // State for search term
  const [searchTerm, setSearchTerm] = useState("");

  // State for delete confirmation
  const [moldToDelete, setMoldToDelete] = useState<Mold | null>(null);

  // State for filters
  const [filters, setFilters] = useState({
    technology: [] as string[],
    alloy: [] as string[],
    tags: [] as string[],
    isActive: null as boolean | null | "mixed",
    moldSize: [] as string[],
  });

  const queryClient = useQueryClient();

  // Fetch molds data using TanStack Query
  const {
    data: molds,
    isLoading: isLoadingMolds,
    error: moldsError,
    createMold,
    updateMold,
    duplicateMold,
    deleteMold,
  } = useMolds();

  // Fetch technologies, alloys, tags, and mold sizes for filters
  const { data: technologies } = useTechnologies();
  const { data: alloys } = useAlloys();
  const { data: tags } = useTags();
  const { data: moldSizes } = useMoldSizes();

  // Periodisch den Cache für Molds invalidieren, um sicherzustellen, dass die Daten aktuell sind
  useEffect(() => {
    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ["molds"] });
    }, 2000); // Alle 2 Sekunden aktualisieren

    return () => clearInterval(interval);
  }, [queryClient]);

  /**
   * Opens the form dialog in create mode
   */
  const handleAddNew = () => {
    setSelectedMold(null);
    setFormMode("create");
    setShowFormDialog(true);
  };

  /**
   * Opens the form dialog in edit mode with the selected mold
   */
  const handleEdit = (mold: Mold) => {
    setSelectedMold(mold);
    setFormMode("edit");
    setShowFormDialog(true);
  };

  /**
   * Opens the form dialog in duplicate mode with the selected mold
   */
  const handleDuplicate = (mold: Mold) => {
    setSelectedMold(mold);
    setFormMode("duplicate");
    setShowFormDialog(true);
  };

  /**
   * Opens the delete confirmation dialog
   */
  const handleConfirmDelete = (mold: Mold) => {
    setMoldToDelete(mold);
  };

  /**
   * Deletes the mold after confirmation
   */
  const handleDelete = async () => {
    if (!moldToDelete) return;

    try {
      await deleteMold(moldToDelete.id);
      setMoldToDelete(null);
      // Aktualisieren der Daten
      queryClient.invalidateQueries({ queryKey: ["molds"] });
    } catch (error) {
      console.error(t("error_delete_mold_table"), error);
    }
  };

  /**
   * Handles row click to open the form dialog in edit mode
   */
  const handleRowClick = (mold: Mold) => {
    setSelectedMold(mold);
    setFormMode("edit");
    setShowFormDialog(true);
  };

  /**
   * Manuelles Aktualisieren der Daten
   */
  const refreshData = () => {
    queryClient.invalidateQueries({ queryKey: ["molds"] });
    queryClient.invalidateQueries({ queryKey: ["tags"] });
    queryClient.invalidateQueries({ queryKey: ["articles"] });
  };

  /**
   * Filters molds based on search term and filters
   */
  const filteredMolds = molds?.filter((mold) => {
    // Search term filter
    const searchMatch =
      searchTerm === "" ||
      mold.legacyMoldNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mold.moldNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mold.warehouseLocation.toLowerCase().includes(searchTerm.toLowerCase());

    // Technology filter - if no technologies selected, show all
    const technologyMatch =
      filters.technology.length === 0 ||
      filters.technology.includes(mold.technology);

    // Alloy filter - if no alloys selected, show all
    const alloyMatch =
      filters.alloy.length === 0 || filters.alloy.includes(mold.alloy);

    // Tags filter - if no tags selected, show all
    const tagsMatch =
      filters.tags.length === 0 ||
      (mold.tags && mold.tags.some((tag) => filters.tags.includes(tag)));

    // Active status filter
    const activeMatch =
      filters.isActive === null ||
      (filters.isActive === true && mold.isActive === true) ||
      (filters.isActive === false && mold.isActive === false) ||
      (filters.isActive === "mixed" && mold.activityStatus === "mixed");

    // Mold size filter - if no mold sizes selected, show all
    const moldSizeMatch =
      filters.moldSize.length === 0 ||
      (mold.moldSize && filters.moldSize.includes(mold.moldSize));

    return (
      searchMatch &&
      technologyMatch &&
      alloyMatch &&
      tagsMatch &&
      activeMatch &&
      moldSizeMatch
    );
  });

  /**
   * Renders the table content based on loading state
   */
  const renderTableContent = () => {
    if (isLoadingMolds) {
      return Array(5)
        .fill(0)
        .map((_, index) => (
          <TableRow key={`skeleton-${index}`}>
            {Array(10)
              .fill(0)
              .map((_, cellIndex) => (
                <TableCell key={`cell-${index}-${cellIndex}`}>
                  <Skeleton className="h-6 w-full" />
                </TableCell>
              ))}
          </TableRow>
        ));
    }

    if (moldsError) {
      return (
        <TableRow>
          <TableCell colSpan={10} className="text-center py-8 text-red-500">
            {t("error_loading_molds")}
          </TableCell>
        </TableRow>
      );
    }

    if (!filteredMolds?.length) {
      return (
        <TableRow>
          <TableCell
            colSpan={10}
            className="text-center py-8 text-muted-foreground"
          >
            {t("no_data_molds")}
          </TableCell>
        </TableRow>
      );
    }

    return filteredMolds.map((mold) => (
      <MoldTableRow
        key={mold.id}
        mold={mold}
        onEdit={handleEdit}
        onDuplicate={handleDuplicate}
        onDelete={handleConfirmDelete}
        onRowClick={handleRowClick}
      />
    ));
  };

  return (
    <div className="space-y-4">
      <MoldTableActions
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        filters={filters}
        setFilters={setFilters}
        technologies={technologies || []}
        alloys={alloys || []}
        tags={tags || []}
        moldSizes={moldSizes || []}
        onAddNew={handleAddNew}
        onRefresh={refreshData}
      />

      {/* Active Filter Pills */}
      <FilterBadges filters={filters} setFilters={setFilters} />

      <div className="rounded-md border overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <MoldTableHeader />
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>
      </div>

      {/* Form Dialog for Create/Edit/Duplicate */}
      <MoldFormDialog
        open={showFormDialog}
        onOpenChange={(open) => {
          setShowFormDialog(open);
          if (!open) {
            // Aktualisieren der Daten, wenn das Formular geschlossen wird
            queryClient.invalidateQueries({ queryKey: ["molds"] });
            queryClient.invalidateQueries({ queryKey: ["articles"] });
          }
        }}
        mode={formMode}
        mold={selectedMold}
        technologies={technologies || []}
        alloys={alloys || []}
        tags={tags || []}
        moldSizes={moldSizes || []}
        onSubmit={async (data) => {
          try {
            if (formMode === "create") {
              await createMold(data);
            } else if (formMode === "edit" && selectedMold) {
              await updateMold({ ...data, id: selectedMold.id });
            } else if (formMode === "duplicate") {
              await duplicateMold(data);
            }
            setShowFormDialog(false);
            // Explizit den Cache für Molds invalidieren
            queryClient.invalidateQueries({ queryKey: ["molds"] });
            queryClient.invalidateQueries({ queryKey: ["articles"] });
          } catch (error) {
            console.error(t("error_save_mold_table"), error);
          }
        }}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        open={!!moldToDelete}
        onOpenChange={(open) => !open && setMoldToDelete(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t("delete_dialog_title")}</AlertDialogTitle>
            <AlertDialogDescription>
              {t("delete_dialog_description_part1")} "{moldToDelete?.moldNumber}
              "{t("delete_dialog_description_part2")}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("cancel_button")}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground"
            >
              {t("delete_button")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
