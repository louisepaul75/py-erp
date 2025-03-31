"use client";

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
import ArticleTable from "@/components/mold/article-table";
import type { ArticleStatus } from "@/types/mold/article";
import type { JSX } from "react";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props for the ArticlesTab component
 */
interface ArticlesTabProps {
  mode: "create" | "edit" | "duplicate";
  moldId: string | null;
  tempArticles: any[];
  onAddArticle: () => void;
  renderArticleStatusIcon: (status: ArticleStatus) => JSX.Element;
}

/**
 * Articles tab for the mold form
 */
export function ArticlesTab({
  mode,
  moldId,
  tempArticles,
  onAddArticle,
  renderArticleStatusIcon,
}: ArticlesTabProps) {
  const { t } = useAppTranslation("mold");
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Articles on this Mold</h3>
        <Button onClick={onAddArticle} className="flex items-center gap-2">
          <Plus className="h-4 w-4" /> {t("Old Article Number")}
        </Button>
      </div>

      {mode === "create" ? (
        tempArticles.length > 0 ? (
          <div className="rounded-md border overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("old_article_number")}</TableHead>
                  <TableHead>{t("new_article_number")}</TableHead>
                  <TableHead>{t("article_description")}</TableHead>
                  <TableHead>{t("frequency")}</TableHead>
                  <TableHead>{t("status")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tempArticles.map((article, index) => (
                  <TableRow key={`temp-article-${index}`}>
                    <TableCell>{article.oldArticleNumber}</TableCell>
                    <TableCell>{article.newArticleNumber}</TableCell>
                    <TableCell>{article.description}</TableCell>
                    <TableCell>{article.frequency}</TableCell>
                    <TableCell className="flex items-center gap-2">
                      {renderArticleStatusIcon(article.status)}
                      {article.status}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-center p-8 border rounded-md bg-muted/20">
            <h3 className="text-lg font-medium mb-2">
              {t("no_articles_heading")}
            </h3>
            <p className="text-muted-foreground mb-4">
              {t("no_articles_message")}
            </p>
            <p className="text-sm text-muted-foreground">
              {t("articles_note")}
            </p>
          </div>
        )
      ) : (
        moldId && (
          <ArticleTable
            moldId={moldId}
            showHeader={false}
            onAddArticle={onAddArticle}
          />
        )
      )}
    </div>
  );
}
