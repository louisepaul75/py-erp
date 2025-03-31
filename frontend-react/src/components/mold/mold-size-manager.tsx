"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Pencil, Trash, Save, X } from "lucide-react";
import { useMoldSizes } from "@/hooks/mold/use-mold-sizes";
import type { MoldSize } from "@/types/mold/mold-size";
import { Skeleton } from "@/components/ui/skeleton";
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
import { useQueryClient } from "@tanstack/react-query";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * MoldSizeManager component for managing mold sizes
 */
export default function MoldSizeManager() {
  // State for new mold size
  const [newMoldSize, setNewMoldSize] = useState({
    name: "",
    description: "",
  });

  // State for editing mold size
  const [editingMoldSize, setEditingMoldSize] = useState<MoldSize | null>(null);
  const [editValues, setEditValues] = useState({
    name: "",
    description: "",
  });

  const { t } = useAppTranslation("mold");

  // State for delete confirmation
  const [sizeToDelete, setSizeToDelete] = useState<MoldSize | null>(null);

  const queryClient = useQueryClient();

  // Fetch mold sizes data using TanStack Query
  const {
    data: moldSizes,
    isLoading,
    error,
    createMoldSize,
    updateMoldSize,
    deleteMoldSize,
  } = useMoldSizes();

  /**
   * Handles adding a new mold size
   */
  const handleAddMoldSize = async () => {
    if (newMoldSize.name.trim() === "") return;

    try {
      await createMoldSize(newMoldSize);
      setNewMoldSize({
        name: "",
        description: "",
      });
      // Aktualisieren der Daten
      queryClient.invalidateQueries({ queryKey: ["moldSizes"] });
    } catch (error) {
      console.error(t("error_create_mold_size"), error);
    }
  };

  /**
   * Handles editing a mold size
   */
  const handleStartEdit = (size: MoldSize) => {
    setEditingMoldSize(size);
    setEditValues({
      name: size.name,
      description: size.description || "",
    });
  };

  /**
   * Saves the edited mold size
   */
  const handleSaveEdit = async () => {
    if (!editingMoldSize || editValues.name.trim() === "") return;

    try {
      await updateMoldSize({
        ...editingMoldSize,
        name: editValues.name,
        description: editValues.description,
      });
      setEditingMoldSize(null);
      // Aktualisieren der Daten
      queryClient.invalidateQueries({ queryKey: ["moldSizes"] });
      queryClient.invalidateQueries({ queryKey: ["molds"] });
    } catch (error) {
      console.error(t("error_update_mold_size"), error);
    }
  };

  /**
   * Cancels the editing process
   */
  const handleCancelEdit = () => {
    setEditingMoldSize(null);
  };

  /**
   * Opens the delete confirmation dialog
   */
  const handleConfirmDelete = (size: MoldSize) => {
    setSizeToDelete(size);
  };

  /**
   * Deletes the mold size after confirmation
   */
  const handleDelete = async () => {
    if (!sizeToDelete) return;

    try {
      await deleteMoldSize(sizeToDelete.id);
      setSizeToDelete(null);

      // Explizit den Cache für Molds und MoldSizes invalidieren
      queryClient.invalidateQueries({ queryKey: ["moldSizes"] });
      queryClient.invalidateQueries({ queryKey: ["molds"] });
    } catch (error) {
      console.error(t("error_delete_mold_size"), error);
    }
  };

  /**
   * Renders the table content based on loading state
   */
  const renderTableContent = () => {
    if (isLoading) {
      return Array(3)
        .fill(0)
        .map((_, index) => (
          <TableRow key={`skeleton-${index}`}>
            <TableCell>
              <Skeleton className="h-6 w-full" />
            </TableCell>
            <TableCell>
              <Skeleton className="h-6 w-full" />
            </TableCell>
            <TableCell>
              <Skeleton className="h-6 w-24" />
            </TableCell>
          </TableRow>
        ));
    }

    if (error) {
      return (
        <TableRow>
          <TableCell colSpan={3} className="text-center py-8 text-red-500">
            {t("error_loading_mold_sizes")}
          </TableCell>
        </TableRow>
      );
    }

    if (!moldSizes?.length) {
      return (
        <TableRow>
          <TableCell
            colSpan={3}
            className="text-center py-8 text-muted-foreground"
          >
            {t("no_data_mold_sizes")}
          </TableCell>
        </TableRow>
      );
    }

    return moldSizes.map((size) => (
      <TableRow key={size.id}>
        <TableCell>
          {editingMoldSize?.id === size.id ? (
            <Input
              value={editValues.name}
              onChange={(e) =>
                setEditValues({ ...editValues, name: e.target.value })
              }
              className="max-w-sm"
            />
          ) : (
            size.name
          )}
        </TableCell>
        <TableCell>
          {editingMoldSize?.id === size.id ? (
            <Textarea
              value={editValues.description}
              onChange={(e) =>
                setEditValues({ ...editValues, description: e.target.value })
              }
              className="max-w-sm h-20"
            />
          ) : (
            size.description || "-"
          )}
        </TableCell>
        <TableCell className="text-right">
          {editingMoldSize?.id === size.id ? (
            <div className="flex justify-end gap-2">
              <Button
                size="sm"
                variant="ghost"
                onClick={handleCancelEdit}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
                <span className="sr-only">{t("cancel_button")}</span>
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={handleSaveEdit}
                className="h-8 w-8 p-0"
              >
                <Save className="h-4 w-4" />
                <span className="sr-only">{t("save_button")}</span>
              </Button>
            </div>
          ) : (
            <div className="flex justify-end gap-2">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleStartEdit(size)}
                className="h-8 w-8 p-0"
              >
                <Pencil className="h-4 w-4" />
                <span className="sr-only">{t("edit_button")}</span>
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleConfirmDelete(size)}
                className="h-8 w-8 p-0 text-destructive"
              >
                <Trash className="h-4 w-4" />
                <span className="sr-only">{t("delete_button")}</span>
              </Button>
            </div>
          )}
        </TableCell>
      </TableRow>
    ));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("card_title_mold_sizes")}</CardTitle>
        <CardDescription>{t("card_description_mold_sizes")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <Input
              placeholder={t("new_mold_size_placeholder")}
              value={newMoldSize.name}
              onChange={(e) =>
                setNewMoldSize({ ...newMoldSize, name: e.target.value })
              }
              className="mb-2"
            />
            <Textarea
              placeholder={t("new_mold_size_description_placeholder")}
              value={newMoldSize.description}
              onChange={(e) =>
                setNewMoldSize({ ...newMoldSize, description: e.target.value })
              }
              className="h-20"
            />
          </div>
          <div className="flex items-end">
            <Button
              onClick={handleAddMoldSize}
              className="flex items-center gap-2 mt-auto"
            >
              <Plus className="h-4 w-4" /> {t("add_mold_size_button")}
            </Button>
          </div>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("save_name")}</TableHead>
                <TableHead>{t("description_name")}</TableHead>
                <TableHead className="w-[100px] text-right">
                  {t("actions")}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>

        <AlertDialog
          open={!!sizeToDelete}
          onOpenChange={(open) => !open && setSizeToDelete(null)}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>{t("delete_dialog_title")}</AlertDialogTitle>
              <AlertDialogDescription>
                {t("delete_mold_manager_description_part1")} "
                {sizeToDelete?.name}"{" "}
                {t("delete_mold_manager_description_part2")}
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
      </CardContent>
    </Card>
  );
}
