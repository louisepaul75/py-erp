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
import { useTags } from "@/hooks/mold/use-tags";
import type { Tag } from "@/types/mold/tag";
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
 * TagManager component for managing tags
 */
export default function TagManager() {
  // State for new tag name
  const [newTagName, setNewTagName] = useState("");

  // State for editing tag
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [editName, setEditName] = useState("");

  // State for delete confirmation
  const [tagToDelete, setTagToDelete] = useState<Tag | null>(null);

  const queryClient = useQueryClient();

  const { t } = useAppTranslation("mold");

  // Fetch tags data using TanStack Query
  const {
    data: tags,
    isLoading,
    error,
    createTag,
    updateTag,
    deleteTag,
  } = useTags();

  /**
   * Handles adding a new tag
   */
  const handleAddTag = async () => {
    if (newTagName.trim() === "") return;

    try {
      await createTag({ name: newTagName });
      setNewTagName("");
      // Aktualisieren der Daten
      queryClient.invalidateQueries({ queryKey: ["tags"] });
    } catch (error) {
      console.error(t("error_create_tag"), error);
    }
  };

  /**
   * Handles editing a tag
   */
  const handleStartEdit = (tag: Tag) => {
    setEditingTag(tag);
    setEditName(tag.name);
  };

  /**
   * Saves the edited tag
   */
  const handleSaveEdit = async () => {
    if (!editingTag || editName.trim() === "") return;

    try {
      await updateTag({
        ...editingTag,
        name: editName,
      });
      setEditingTag(null);
      // Aktualisieren der Daten
      queryClient.invalidateQueries({ queryKey: ["tags"] });
      queryClient.invalidateQueries({ queryKey: ["molds"] });
    } catch (error) {
      console.error(t("error_update_tag"), error);
    }
  };

  /**
   * Cancels the editing process
   */
  const handleCancelEdit = () => {
    setEditingTag(null);
  };

  /**
   * Opens the delete confirmation dialog
   */
  const handleConfirmDelete = (tag: Tag) => {
    setTagToDelete(tag);
  };

  /**
   * Deletes the tag after confirmation
   */
  const handleDelete = async () => {
    if (!tagToDelete) return;

    try {
      await deleteTag(tagToDelete.id);
      setTagToDelete(null);

      // Explizit den Cache für Molds und Tags invalidieren
      queryClient.invalidateQueries({ queryKey: ["tags"] });
      queryClient.invalidateQueries({ queryKey: ["molds"] });

      // Verzögertes erneutes Invalidieren, um sicherzustellen, dass alle Änderungen übernommen wurden
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ["molds"] });
      }, 100);
    } catch (error) {
      console.error(t("error_delete_tag"), error);
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
            {t("error_loading_tags")}
          </TableCell>
        </TableRow>
      );
    }

    if (!tags?.length) {
      return (
        <TableRow>
          <TableCell
            colSpan={2}
            className="text-center py-8 text-muted-foreground"
          >
            {t("no_data_tags")}
          </TableCell>
        </TableRow>
      );
    }

    return tags.map((tag) => (
      <TableRow key={tag.id}>
        <TableCell>
          {editingTag?.id === tag.id ? (
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="max-w-sm"
            />
          ) : (
            tag.name
          )}
        </TableCell>
        <TableCell className="text-right">
          {editingTag?.id === tag.id ? (
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
                onClick={() => handleStartEdit(tag)}
                className="h-8 w-8 p-0"
              >
                <Pencil className="h-4 w-4" />
                <span className="sr-only">{t("edit_button")}</span>
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleConfirmDelete(tag)}
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
        <CardTitle>{t("card_title_tags")}</CardTitle>
        <CardDescription>{t("card_description_tags")}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-6">
          <Input
            placeholder="New tag name"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            className="max-w-sm"
          />
          <Button onClick={handleAddTag} className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> {t("add_button")}
          </Button>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tag Name</TableHead>
                <TableHead className="w-[100px] text-right">
                  {t("actions")}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>

        <AlertDialog
          open={!!tagToDelete}
          onOpenChange={(open) => !open && setTagToDelete(null)}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>{t("delete_dialog_title")}</AlertDialogTitle>
              <AlertDialogDescription>
                {t("delete_tag_description_part1")} "{tagToDelete?.name}"{" "}
                {t("delete_tag_description_part2")}
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
