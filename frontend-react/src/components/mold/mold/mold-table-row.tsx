"use client";

import { TableCell, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  MoreHorizontal,
  TagIcon,
  Check,
  Minus,
  AlertTriangle,
} from "lucide-react";
import type { Mold } from "@/types/mold/mold";
import { MoldActivityStatus } from "@/types/mold/mold";
import { formatDate } from "@/lib/mold/utils";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props für die MoldTableRow Komponente
 */
interface MoldTableRowProps {
  mold: Mold;
  onEdit: (mold: Mold) => void;
  onDuplicate: (mold: Mold) => void;
  onDelete: (mold: Mold) => void;
  onRowClick: (mold: Mold) => void;
}

/**
 * Komponente zur Darstellung einer Zeile in der Mold-Tabelle
 */
export function MoldTableRow({
  mold,
  onEdit,
  onDuplicate,
  onDelete,
  onRowClick,
}: MoldTableRowProps) {
  /**
   * Rendert das Statussymbol basierend auf dem Formstatus
   */
  const { t } = useAppTranslation("mold");

  const renderStatusBadge = (mold: Mold) => {
    if (!mold.activityStatus) {
      return (
        <Badge variant={mold.isActive ? "default" : "outline"}>
          {mold.isActive ? t("status_active") : t("status_inactive")}
        </Badge>
      );
    }

    switch (mold.activityStatus) {
      case MoldActivityStatus.ACTIVE:
        return (
          <Badge variant="default" className="bg-green-500">
            <Check className="h-3 w-3 mr-1" />{" "}
            <Minus className="h-3 w-3 mr-1" /> {t("status_active")}
          </Badge>
        );
      case MoldActivityStatus.INACTIVE:
        return (
          <Badge variant="outline" className="text-amber-500 border-amber-500">
            <Minus className="h-3 w-3 mr-1" /> {t("status_inactive")}
          </Badge>
        );
      case MoldActivityStatus.MIXED:
        return (
          <Badge variant="outline" className="text-blue-500 border-blue-500">
            <AlertTriangle className="h-3 w-3 mr-1" /> {t("status_mixed")}
          </Badge>
        );
    }
  };

  return (
    <TableRow
      className="cursor-pointer hover:bg-muted/50"
      onClick={() => onRowClick(mold)}
    >
      <TableCell>{mold.legacyMoldNumber}</TableCell>
      <TableCell>{mold.moldNumber}</TableCell>
      <TableCell>{mold.technology}</TableCell>
      <TableCell>{mold.alloy}</TableCell>
      <TableCell>{mold.warehouseLocation}</TableCell>
      <TableCell>{mold.moldSize || "-"}</TableCell>
      <TableCell className="text-center">{mold.numberOfArticles}</TableCell>
      <TableCell>{renderStatusBadge(mold)}</TableCell>
      <TableCell>
        <div className="flex flex-wrap gap-1">
          {mold.tags && mold.tags.length > 0 ? (
            mold.tags.map((tag) => (
              <Badge
                key={`${mold.id}-${tag}`}
                variant="secondary"
                className="flex items-center gap-1"
              >
                <TagIcon className="h-3 w-3" />
                {tag}
              </Badge>
            ))
          ) : (
            <span className="text-muted-foreground text-sm">
              {t("no_tags")}
            </span>
          )}
        </div>
      </TableCell>
      <TableCell>{formatDate(mold.createdDate)}</TableCell>
      <TableCell onClick={(e) => e.stopPropagation()}>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
              <span className="sr-only">{t("open_menu")}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(mold)}>
              {t("edit_button")}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onDuplicate(mold)}>
              {t("duplicate")}
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete(mold)}
              className="text-destructive focus:text-destructive"
            >
              {t("delete_button")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </TableCell>
    </TableRow>
  );
}
