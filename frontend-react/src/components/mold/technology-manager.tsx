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
import { useTechnologies } from "@/hooks/mold/use-technologies";
import type { Technology } from "@/types/mold/technology";
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
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * TechnologyManager component for managing technologies
 */
export default function TechnologyManager() {
  // State for new technology name
  const [newTechName, setNewTechName] = useState("");

  // State for editing technology
  const [editingTech, setEditingTech] = useState<Technology | null>(null);
  const [editName, setEditName] = useState("");

  // State for delete confirmation
  const [techToDelete, setTechToDelete] = useState<Technology | null>(null);

  const { t } = useAppTranslation("mold");

  // Fetch technologies data using TanStack Query
  const {
    data: technologies,
    isLoading,
    error,
    createTechnology,
    updateTechnology,
    deleteTechnology,
  } = useTechnologies();

  /**
   * Handles adding a new technology
   */
  const handleAddTechnology = async () => {
    if (newTechName.trim() === "") return;

    try {
      await createTechnology({ name: newTechName });
      setNewTechName("");
    } catch (error) {
      console.error(t("error_create_technology"), error);
    }
  };

  /**
   * Handles editing a technology
   */
  const handleStartEdit = (tech: Technology) => {
    setEditingTech(tech);
    setEditName(tech.name);
  };

  /**
   * Saves the edited technology
   */
  const handleSaveEdit = async () => {
    if (!editingTech || editName.trim() === "") return;

    try {
      await updateTechnology({
        ...editingTech,
        name: editName,
      });
      setEditingTech(null);
    } catch (error) {
      console.error(t("error_update_technology"), error);
    }
  };

  /**
   * Cancels the editing process
   */
  const handleCancelEdit = () => {
    setEditingTech(null);
  };

  /**
   * Opens the delete confirmation dialog
   */
  const handleConfirmDelete = (tech: Technology) => {
    setTechToDelete(tech);
  };

  /**
   * Deletes the technology after confirmation
   */
  const handleDelete = async () => {
    if (!techToDelete) return;

    try {
      await deleteTechnology(techToDelete.id);
      setTechToDelete(null);
    } catch (error) {
      console.error(t("error_delete_technology"), error);
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
            {t("error_loading_technologies")}
          </TableCell>
        </TableRow>
      );
    }

    if (!technologies?.length) {
      return (
        <TableRow>
          <TableCell
            colSpan={2}
            className="text-center py-8 text-muted-foreground"
          >
            {t("no_data_technologies")}
          </TableCell>
        </TableRow>
      );
    }

    return technologies.map((tech) => (
      <TableRow key={tech.id}>
        <TableCell>
          {editingTech?.id === tech.id ? (
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="max-w-sm"
            />
          ) : (
            tech.name
          )}
        </TableCell>
        <TableCell className="text-right">
          {editingTech?.id === tech.id ? (
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
                onClick={() => handleStartEdit(tech)}
                className="h-8 w-8 p-0"
              >
                <Pencil className="h-4 w-4" />
                <span className="sr-only">{t("delete_button")}</span>
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleConfirmDelete(tech)}
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
        <CardTitle>{t("card_title_technologies")}</CardTitle>
        <CardDescription>{t("card_description_technologies")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-6">
          <Input
            placeholder={t("new_technology_placeholder")}
            value={newTechName}
            onChange={(e) => setNewTechName(e.target.value)}
            className="max-w-sm"
          />
          <Button
            onClick={handleAddTechnology}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" /> {t("add_button")}
          </Button>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("technology_name")}</TableHead>
                <TableHead className="w-[100px] text-right">{t("actions")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>

        <AlertDialog
          open={!!techToDelete}
          onOpenChange={(open) => !open && setTechToDelete(null)}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>{t("delete_dialog_title")}</AlertDialogTitle>
              <AlertDialogDescription>
              {t("delete_manager_description")} "
                {techToDelete?.name}". {t("delete_warning")}
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
