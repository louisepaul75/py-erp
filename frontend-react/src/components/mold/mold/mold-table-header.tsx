"use client";

import { TableHead, TableHeader, TableRow } from "@/components/ui/table";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Komponente für die Tabellenüberschrift der Mold-Tabelle
 */
export function MoldTableHeader() {
  const { t } = useAppTranslation("mold");

  return (
    <TableHeader>
      <TableRow>
        <TableHead>{t("legacy_mold_number_label")}</TableHead>
        <TableHead>{t("mold_number_label")}</TableHead>
        <TableHead>{t("technology_label")}</TableHead>
        <TableHead>{t("alloy_label")}</TableHead>
        <TableHead>{t("warehouse_location_label")}</TableHead>
        <TableHead>{t("mold_size_label")}</TableHead>
        <TableHead className="text-center">{t("number_of_articles_label")}</TableHead>
        <TableHead>{t("activity_status_heading")}</TableHead>
        <TableHead>{t("tags_heading")}</TableHead>
        <TableHead>{t("created_date")}</TableHead>
        <TableHead className="w-[80px]"></TableHead>
      </TableRow>
    </TableHeader>
  );
}
