"use client";
import { TableCell, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  MoreHorizontal,
  Pencil,
  Trash,
  Save,
  X,
  Check,
  Minus,
  AlertTriangle,
} from "lucide-react";
import type { Article, ArticleInstance } from "@/types/mold/article";
import { ArticleStatus } from "@/types/mold/article";
import { ArticleInstanceRow } from "./article-instance-row";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props für die ArticleRow-Komponente
 */
interface ArticleRowProps {
  article: Article;
  isExpanded: boolean;
  onToggleExpand: (articleId: string) => void;
  onStartEdit: (article: Article) => void;
  onConfirmDelete: (article: Article) => void;
  onToggleInstance: (article: Article, instance: ArticleInstance) => void;
  onUpdateStatus: (articleId: string, status: ArticleStatus) => void;
  editingArticle: Article | null;
  editValues: {
    oldArticleNumber: string;
    newArticleNumber: string;
    description: string;
    frequency: number;
    status: ArticleStatus;
  };
  onEditChange: (values: {
    oldArticleNumber: string;
    newArticleNumber: string;
    description: string;
    frequency: number;
    status: ArticleStatus;
  }) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
}

/**
 * Komponente zur Darstellung einer Artikelzeile mit optionalen Instanzen
 */
export function ArticleRow({
  article,
  isExpanded,
  onToggleExpand,
  onStartEdit,
  onConfirmDelete,
  onToggleInstance,
  onUpdateStatus,
  editingArticle,
  editValues,
  onEditChange,
  onSaveEdit,
  onCancelEdit,
}: ArticleRowProps) {
  /**
   * Rendert das Statussymbol basierend auf dem Artikelstatus
   */
  const { t } = useAppTranslation("mold");

  const renderStatusIcon = (status: ArticleStatus) => {
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
   * Rendert den Statustext basierend auf dem Artikelstatus
   */
  const renderStatusText = (status: ArticleStatus) => {
    switch (status) {
      case ArticleStatus.ACTIVE:
        return "Active";
      case ArticleStatus.INACTIVE:
        return "Inactive";
      case ArticleStatus.DISCONTINUED:
        return "Discontinued";
      case ArticleStatus.MIXED:
        return "Mixed";
    }
  };

  /**
   * Rendert die Statusfarbe basierend auf dem Artikelstatus
   */
  const getStatusColor = (status: ArticleStatus) => {
    switch (status) {
      case ArticleStatus.ACTIVE:
        return "text-green-500";
      case ArticleStatus.INACTIVE:
        return "text-amber-500";
      case ArticleStatus.DISCONTINUED:
        return "text-red-500";
      case ArticleStatus.MIXED:
        return "text-blue-500";
    }
  };

  /**
   * Behandelt die Änderung des Artikelstatus
   */
  const handleStatusChange = (status: ArticleStatus) => {
    if (editingArticle?.id === article.id) {
      // Wenn im Bearbeitungsmodus, nur den Formularwert ändern
      onEditChange({ ...editValues, status });
    } else {
      // Sonst den Status direkt aktualisieren
      onUpdateStatus(article.id, status);
    }
  };

  return (
    <>
      <TableRow
        key={`article-${article.id}`}
        className={isExpanded ? "bg-muted/50" : ""}
      >
        <TableCell>
          {editingArticle?.id === article.id ? (
            <div className="bg-muted p-2 rounded">
              {editValues.oldArticleNumber}
            </div>
          ) : (
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 mr-2"
                onClick={() => onToggleExpand(article.id)}
              >
                {isExpanded ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="lucide lucide-chevron-down"
                  >
                    <path d="m6 9 6 6 6-6" />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="lucide lucide-chevron-right"
                  >
                    <path d="m9 18 6-6-6-6" />
                  </svg>
                )}
              </Button>
              {article.oldArticleNumber}
            </div>
          )}
        </TableCell>
        <TableCell>
          {editingArticle?.id === article.id ? (
            <div className="bg-muted p-2 rounded">
              {editValues.newArticleNumber}
            </div>
          ) : (
            article.newArticleNumber
          )}
        </TableCell>
        <TableCell>
          {editingArticle?.id === article.id ? (
            <div className="bg-muted p-2 rounded">{editValues.description}</div>
          ) : (
            article.description
          )}
        </TableCell>
        <TableCell>
          {editingArticle?.id === article.id ? (
            <Input
              type="number"
              min="1"
              value={editValues.frequency}
              onChange={(e) =>
                onEditChange({
                  ...editValues,
                  frequency: Number.parseInt(e.target.value) || 1,
                })
              }
            />
          ) : (
            article.frequency
          )}
        </TableCell>
        <TableCell>
          {editingArticle?.id === article.id ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full flex justify-between items-center"
                >
                  <span className="flex items-center gap-2">
                    {renderStatusIcon(editValues.status)}
                    {renderStatusText(editValues.status)}
                  </span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>{t("status")}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuRadioGroup
                  value={editValues.status}
                  onValueChange={(value) =>
                    handleStatusChange(value as ArticleStatus)
                  }
                >
                  <DropdownMenuRadioItem value={ArticleStatus.ACTIVE}>
                    <Check className="h-4 w-4 text-green-500 mr-2" /> {t("status_active")}
                  </DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value={ArticleStatus.INACTIVE}>
                    <Minus className="h-4 w-4 text-amber-500 mr-2" /> {t("status_inactive")}
                  </DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className={`flex items-center gap-2 ${getStatusColor(
                    article.status
                  )}`}
                >
                  {renderStatusIcon(article.status)}
                  {renderStatusText(article.status)}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>{t("change_status")}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuRadioGroup
                  value={article.status}
                  onValueChange={(value) =>
                    handleStatusChange(value as ArticleStatus)
                  }
                >
                  <DropdownMenuRadioItem value={ArticleStatus.ACTIVE}>
                    <Check className="h-4 w-4 text-green-500 mr-2" /> {t("activity_status_active")}
                  </DropdownMenuRadioItem>
                  <DropdownMenuRadioItem value={ArticleStatus.INACTIVE}>
                    <Minus className="h-4 w-4 text-amber-500 mr-2" /> {t("activity_status_inactive")}
                  </DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </TableCell>
        <TableCell>
          {editingArticle?.id === article.id ? (
            <div className="flex justify-end gap-2">
              <Button
                size="sm"
                variant="ghost"
                onClick={onCancelEdit}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
                <span className="sr-only">{t("cancel_button")}</span>
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={onSaveEdit}
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
                onClick={() => onStartEdit(article)}
                className="h-8 w-8 p-0"
              >
                <Pencil className="h-4 w-4" />
                <span className="sr-only">{t("edit_button")}</span>
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onConfirmDelete(article)}
                className="h-8 w-8 p-0 text-destructive"
              >
                <Trash className="h-4 w-4" />
                <span className="sr-only">{t("delete_button")}</span>
              </Button>
            </div>
          )}
        </TableCell>
      </TableRow>

      {/* Render instances if article is expanded */}
      {isExpanded &&
        article.instances &&
        article.instances.map((instance) => (
          <ArticleInstanceRow
            key={`instance-${instance.id}`}
            article={article}
            instance={instance}
            onToggleInstance={onToggleInstance}
          />
        ))}
    </>
  );
}
