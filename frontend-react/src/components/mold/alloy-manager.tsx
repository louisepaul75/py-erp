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
import { Plus, Pencil, Trash, Save, X } from "lucide-react";
import { useAlloys } from "@/hooks/mold/use-alloys";
import type { Alloy } from "@/types/mold/alloy";
import { Skeleton } from "@/components/ui/skeleton";
import useAppTranslation from "@/hooks/useTranslationWrapper";

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

/**
 * AlloyManager component for managing alloys
 */
export default function AlloyManager() {
  // State for new alloy name
  const [newAlloyName, setNewAlloyName] = useState("");

  // State for editing alloy
  const [editingAlloy, setEditingAlloy] = useState<Alloy | null>(null);
  const [editName, setEditName] = useState("");

  // State for delete confirmation
  const [alloyToDelete, setAlloyToDelete] = useState<Alloy | null>(null);

  // Fetch alloys data using TanStack Query
  const {
    data: alloys,
    isLoading,
    error,
    createAlloy,
    updateAlloy,
    deleteAlloy,
  } = useAlloys();
  const { t } = useAppTranslation("mold");
  /**
   * Handles adding a new alloy
   */
  const handleAddAlloy = async () => {
    if (newAlloyName.trim() === "") return;

    try {
      await createAlloy({ name: newAlloyName });
      setNewAlloyName("");
    } catch (error) {
      console.error("Failed to create alloy:", error);
    }
  };

  /**
   * Handles editing an alloy
   */
  const handleStartEdit = (alloy: Alloy) => {
    setEditingAlloy(alloy);
    setEditName(alloy.name);
  };

  /**
   * Saves the edited alloy
   */
  const handleSaveEdit = async () => {
    if (!editingAlloy || editName.trim() === "") return;

    try {
      await updateAlloy({
        ...editingAlloy,
        name: editName,
      });
      setEditingAlloy(null);
    } catch (error) {
      console.error("Failed to update alloy:", error);
    }
  };

  /**
   * Cancels the editing process
   */
  const handleCancelEdit = () => {
    setEditingAlloy(null);
  };

  /**
   * Opens the delete confirmation dialog
   */
  const handleConfirmDelete = (alloy: Alloy) => {
    setAlloyToDelete(alloy);
  };

  /**
   * Deletes the alloy after confirmation
   */
  const handleDelete = async () => {
    if (!alloyToDelete) return;

    try {
      await deleteAlloy(alloyToDelete.id);
      setAlloyToDelete(null);
    } catch (error) {
      console.error("Failed to delete alloy:", error);
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
              <Skeleton className="h-6 w-24" />
            </TableCell>
          </TableRow>
        ));
    }

    if (error) {
      return (
        <TableRow>
          <TableCell colSpan={2} className="text-center py-8 text-red-500">
            {t("error_loading_alloys")}
          </TableCell>
        </TableRow>
      );
    }

    if (!alloys?.length) {
      return (
        <TableRow>
          <TableCell
            colSpan={2}
            className="text-center py-8 text-muted-foreground"
          >
            {t("no_data_alloys")}
          </TableCell>
        </TableRow>
      );
    }

    return alloys.map((alloy) => (
      <TableRow key={alloy.id}>
        <TableCell>
          {editingAlloy?.id === alloy.id ? (
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="max-w-sm"
            />
          ) : (
            alloy.name
          )}
        </TableCell>
        <TableCell className="text-right">
          {editingAlloy?.id === alloy.id ? (
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
                onClick={() => handleStartEdit(alloy)}
                className="h-8 w-8 p-0"
              >
                <Pencil className="h-4 w-4" />
                <span className="sr-only">{t("edit_button")}</span>
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleConfirmDelete(alloy)}
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
        <CardTitle>{t("card_title_alloys")}</CardTitle>
        <CardDescription>{t("card_description_alloys")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-6">
          <Input
            placeholder="New alloy name"
            value={newAlloyName}
            onChange={(e) => setNewAlloyName(e.target.value)}
            className="max-w-sm"
          />
          <Button onClick={handleAddAlloy} className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> {t("add_button")}
          </Button>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("allow_name")}</TableHead>
                <TableHead className="w-[100px] text-right">
                  {t("actions")}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>

        <AlertDialog
          open={!!alloyToDelete}
          onOpenChange={(open) => !open && setAlloyToDelete(null)}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>{t("delete_dialog_title")}</AlertDialogTitle>
              <AlertDialogDescription>
                {t("permanent_alloy_delete")} "{alloyToDelete?.name}".
                {t("delete_warning")}
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
