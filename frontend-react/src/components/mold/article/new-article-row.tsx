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
import { MoreHorizontal, Save, X, Check, Minus } from "lucide-react";
import { ArticleStatus } from "@/types/mold/article";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props für die NewArticleRow-Komponente
 */
interface NewArticleRowProps {
  newArticle: {
    oldArticleNumber: string;
    newArticleNumber: string;
    description: string;
    frequency: number;
    status: ArticleStatus;
    moldId: string;
  };
  onNewArticleChange: (newArticle: {
    oldArticleNumber: string;
    newArticleNumber: string;
    description: string;
    frequency: number;
    status: ArticleStatus;
    moldId: string;
  }) => void;
  onAddArticle: () => void;
  onCancel: () => void;
}

/**
 * Komponente zur Erstellung eines neuen Artikels
 */
export function NewArticleRow({
  newArticle,
  onNewArticleChange,
  onAddArticle,
  onCancel,
}: NewArticleRowProps) {
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
    }
  };

  return (
    <TableRow key="new-article-row">
      <TableCell>
        <Input
          value={newArticle.oldArticleNumber}
          onChange={(e) =>
            onNewArticleChange({
              ...newArticle,
              oldArticleNumber: e.target.value,
            })
          }
          placeholder={t("old_article_number")}
        />
      </TableCell>
      <TableCell>
        <Input
          value={newArticle.newArticleNumber}
          onChange={(e) =>
            onNewArticleChange({
              ...newArticle,
              newArticleNumber: e.target.value,
            })
          }
          placeholder={t("new_article_number")}
        />
      </TableCell>
      <TableCell>
        <Input
          value={newArticle.description}
          onChange={(e) =>
            onNewArticleChange({
              ...newArticle,
              description: e.target.value,
            })
          }
          placeholder={t("article_description")}
        />
      </TableCell>
      <TableCell>
        <Input
          type="number"
          min="1"
          value={newArticle.frequency}
          onChange={(e) =>
            onNewArticleChange({
              ...newArticle,
              frequency: Number.parseInt(e.target.value) || 1,
            })
          }
        />
      </TableCell>
      <TableCell>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              className="w-full flex justify-between items-center"
            >
              <span className="flex items-center gap-2">
                {renderStatusIcon(newArticle.status)}
                {renderStatusText(newArticle.status)}
              </span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuLabel>{t("status")}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuRadioGroup
              value={newArticle.status}
              onValueChange={(value) =>
                onNewArticleChange({
                  ...newArticle,
                  status: value as ArticleStatus,
                })
              }
            >
              <DropdownMenuRadioItem value={ArticleStatus.ACTIVE}>
                <Check className="h-4 w-4 text-green-500 mr-2" />{" "}
                {t("activity_status_active")}
              </DropdownMenuRadioItem>
              <DropdownMenuRadioItem value={ArticleStatus.INACTIVE}>
                <Minus className="h-4 w-4 text-amber-500 mr-2" />{" "}
                {t("activity_status_inactive")}
              </DropdownMenuRadioItem>
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </TableCell>
      <TableCell>
        <div className="flex justify-end gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={onCancel}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">{t("cancel_button")}</span>
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={onAddArticle}
            className="h-8 w-8 p-0"
          >
            <Save className="h-4 w-4" />
            <span className="sr-only">{t("save_button")}</span>
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}
