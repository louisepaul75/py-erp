"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useArticles } from "@/hooks/mold/use-articles";
import type { Article, ArticleInstance } from "@/types/mold/article";
import { ArticleStatus } from "@/types/mold/article";
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
import { ArticleRow } from "./article/article-row";
import { NewArticleRow } from "./article/new-article-row";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props for the ArticleTable component
 */
interface ArticleTableProps {
  moldId: string;
  showHeader?: boolean;
  onAddArticle?: () => void;
}

/**
 * ArticleTable component displays a table of articles for a specific mold
 */
export default function ArticleTable({
  moldId,
  showHeader = false,
  onAddArticle,
}: ArticleTableProps) {
  // State for new article
  const [isAddingArticle, setIsAddingArticle] = useState(false);
  const [newArticle, setNewArticle] = useState({
    oldArticleNumber: "",
    newArticleNumber: "",
    description: "",
    frequency: 1,
    status: ArticleStatus.ACTIVE,
    moldId: moldId,
  });

  const { t } = useAppTranslation("mold");

  // State for editing an article
  const [editingArticle, setEditingArticle] = useState<Article | null>(null);
  const [editValues, setEditValues] = useState({
    oldArticleNumber: "",
    newArticleNumber: "",
    description: "",
    frequency: 1,
    status: ArticleStatus.ACTIVE,
  });

  // State for delete confirmation
  const [articleToDelete, setArticleToDelete] = useState<Article | null>(null);

  // State for expanded articles (to show instances)
  const [expandedArticles, setExpandedArticles] = useState<
    Record<string, boolean>
  >({});

  const queryClient = useQueryClient();

  // Fetch articles data using TanStack Query
  const {
    data: articles,
    isLoading,
    error,
    createArticle,
    updateArticle,
    updateArticleInstance,
    updateArticleStatus,
    deleteArticle,
  } = useArticles(moldId);

  /**
   * Toggles the expanded state of an article
   */
  const toggleArticleExpanded = (articleId: string) => {
    setExpandedArticles((prev) => ({
      ...prev,
      [articleId]: !prev[articleId],
    }));
  };

  /**
   * Handles adding a new article
   */
  const handleAddArticle = async () => {
    if (
      newArticle.oldArticleNumber.trim() === "" ||
      newArticle.newArticleNumber.trim() === ""
    )
      return;

    try {
      await createArticle(newArticle);
      setNewArticle({
        oldArticleNumber: "",
        newArticleNumber: "",
        description: "",
        frequency: 1,
        status: ArticleStatus.ACTIVE,
        moldId: moldId,
      });
      setIsAddingArticle(false);
      // Update data
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    } catch (error) {
      console.error("Failed to create article:", error);
    }
  };

  /**
   * Handles starting to edit an article
   */
  const handleStartEdit = (article: Article) => {
    setEditingArticle(article);
    setEditValues({
      oldArticleNumber: article.oldArticleNumber,
      newArticleNumber: article.newArticleNumber,
      description: article.description,
      frequency: article.frequency,
      status: article.status,
    });
  };

  /**
   * Saves the edited article
   */
  const handleSaveEdit = async () => {
    if (!editingArticle) return;

    try {
      await updateArticle({
        ...editingArticle,
        // Behalte die ursprünglichen Werte bei
        oldArticleNumber: editingArticle.oldArticleNumber,
        newArticleNumber: editingArticle.newArticleNumber,
        description: editingArticle.description,
        // Aktualisiere nur die editierbaren Felder
        frequency: editValues.frequency,
        status: editValues.status,
      });
      setEditingArticle(null);
      // Update data
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    } catch (error) {
      console.error("Failed to update article:", error);
    }
  };

  /**
   * Cancels the editing process
   */
  const handleCancelEdit = () => {
    setEditingArticle(null);
  };

  /**
   * Opens the delete confirmation dialog
   */
  const handleConfirmDelete = (article: Article) => {
    setArticleToDelete(article);
  };

  /**
   * Deletes the article after confirmation
   */
  const handleDelete = async () => {
    if (!articleToDelete) return;

    try {
      await deleteArticle(articleToDelete.id);
      setArticleToDelete(null);

      // Explicitly invalidate articles cache
      queryClient.invalidateQueries({ queryKey: ["articles"] });
    } catch (error) {
      console.error("Failed to delete article:", error);
    }
  };

  /**
   * Handles toggling the active state of an article instance
   */
  const handleToggleInstance = async (
    article: Article,
    instance: ArticleInstance
  ) => {
    try {
      await updateArticleInstance({
        articleId: article.id,
        instanceId: instance.id,
        isActive: !instance.isActive,
      });
    } catch (error) {
      console.error("Failed to update article instance:", error);
    }
  };

  /**
   * Handles updating the article status
   */
  const handleUpdateStatus = async (
    articleId: string,
    status: ArticleStatus
  ) => {
    try {
      await updateArticleStatus({
        articleId,
        status,
      });
    } catch (error) {
      console.error("Failed to update article status:", error);
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
            {Array(6)
              .fill(0)
              .map((_, cellIndex) => (
                <TableCell key={`cell-${index}-${cellIndex}`}>
                  <Skeleton className="h-6 w-full" />
                </TableCell>
              ))}
          </TableRow>
        ));
    }

    if (error) {
      return (
        <TableRow>
          <TableCell colSpan={6} className="text-center py-8 text-red-500">
            {t("error_loading_articles")}
          </TableCell>
        </TableRow>
      );
    }

    if (!articles?.length && !isAddingArticle) {
      return (
        <TableRow>
          <TableCell
            colSpan={6}
            className="text-center py-8 text-muted-foreground"
          >
            {t("no_data_articles")}
          </TableCell>
        </TableRow>
      );
    }

    return (
      <>
        {isAddingArticle && (
          <NewArticleRow
            newArticle={newArticle}
            onNewArticleChange={setNewArticle}
            onAddArticle={handleAddArticle}
            onCancel={() => setIsAddingArticle(false)}
          />
        )}

        {articles?.map((article) => (
          <ArticleRow
            key={`article-row-${article.id}`}
            article={article}
            isExpanded={!!expandedArticles[article.id]}
            onToggleExpand={toggleArticleExpanded}
            onStartEdit={handleStartEdit}
            onConfirmDelete={handleConfirmDelete}
            onToggleInstance={handleToggleInstance}
            onUpdateStatus={handleUpdateStatus}
            editingArticle={editingArticle}
            editValues={editValues}
            onEditChange={setEditValues}
            onSaveEdit={handleSaveEdit}
            onCancelEdit={handleCancelEdit}
          />
        ))}
      </>
    );
  };

  const handleAddArticleClick = () => {
    if (onAddArticle) {
      onAddArticle();
    } else {
      setIsAddingArticle(true);
    }
  };

  return (
    <div className="space-y-4">
      {showHeader && (
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium">{t("header_title_articles")}</h3>
          <Button
            onClick={handleAddArticleClick}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" /> {t("add_article_button")}
          </Button>
        </div>
      )}

      <div className="rounded-md border overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t("old_article_number")}</TableHead>
                <TableHead>{t("new_article_number")}</TableHead>
                <TableHead>{t("article_description")}</TableHead>
                <TableHead>{t("frequency")}</TableHead>
                <TableHead>{t("article_status")}</TableHead>
                <TableHead className="w-[80px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{renderTableContent()}</TableBody>
          </Table>
        </div>
      </div>

      <AlertDialog
        open={!!articleToDelete}
        onOpenChange={(open) => !open && setArticleToDelete(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t("delete_dialog_title")}</AlertDialogTitle>
            <AlertDialogDescription>
              {t("permanent_article_delete")} "{articleToDelete?.description}".{" "}
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
    </div>
  );
}
