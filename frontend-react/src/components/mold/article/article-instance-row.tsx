"use client";

import { TableCell, TableRow } from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import type { Article, ArticleInstance } from "@/types/mold/article";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props für die ArticleInstanceRow-Komponente
 */
interface ArticleInstanceRowProps {
  article: Article;
  instance: ArticleInstance;
  onToggleInstance: (article: Article, instance: ArticleInstance) => void;
}

/**
 * Komponente zur Darstellung einer einzelnen Artikelinstanz
 */
export function ArticleInstanceRow({
  article,
  instance,
  onToggleInstance,
}: ArticleInstanceRowProps) {

  const { t } = useAppTranslation("mold");

  return (
    <TableRow key={instance.id} className="bg-muted/20">
      <TableCell className="pl-10">
        <Badge variant="outline" className="mr-2">
          {instance.position}
        </Badge>
      </TableCell>
      <TableCell colSpan={3}>
        {article.newArticleNumber} - Position {instance.position}
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <Switch
            checked={instance.isActive}
            onCheckedChange={() => onToggleInstance(article, instance)}
          />
          <span
            className={
              instance.isActive ? "text-green-500" : "text-muted-foreground"
            }
          >
            {instance.isActive ? t("activity_status_active") : t("activity_status_inactive")}
          </span>
        </div>
      </TableCell>
      <TableCell>{/* Keine Aktionen für einzelne Instanzen */}</TableCell>
    </TableRow>
  );
}
