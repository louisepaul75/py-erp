"use client";

import type React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, Filter, Plus, Search } from "lucide-react";
import FilterPanel from "@/components/mold/filter-panel";
import type { Technology } from "@/types/mold/technology";
import type { Alloy } from "@/types/mold/alloy";
import type { Tag } from "@/types/mold/tag";
import type { MoldSize } from "@/types/mold/mold-size";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props für die MoldTableActions Komponente
 */
interface MoldTableActionsProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  filters: {
    technology: string[];
    alloy: string[];
    tags: string[];
    isActive: boolean | null | "mixed";
    moldSize: string[];
  };
  setFilters: React.Dispatch<
    React.SetStateAction<{
      technology: string[];
      alloy: string[];
      tags: string[];
      isActive: boolean | null | "mixed";
      moldSize: string[];
    }>
  >;
  technologies: Technology[];
  alloys: Alloy[];
  tags: Tag[];
  moldSizes: MoldSize[];
  onAddNew: () => void;
  onRefresh: () => void;
}

/**
 * Komponente für die Aktionsleiste der Mold-Tabelle
 */
export function MoldTableActions({
  searchTerm,
  setSearchTerm,
  filters,
  setFilters,
  technologies,
  alloys,
  tags,
  moldSizes,
  onAddNew,
  onRefresh,
}: MoldTableActionsProps) {
  /**
   * Clears all filters
   */
  const handleClearFilters = () => {
    setFilters({
      technology: [],
      alloy: [],
      tags: [],
      isActive: null,
      moldSize: [],
    });
  };

  const { t } = useAppTranslation("mold");

  /**
   * Gets the count of active filters
   */
  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.technology.length > 0) count++;
    if (filters.alloy.length > 0) count++;
    if (filters.tags.length > 0) count++;
    if (filters.isActive !== null) count++;
    if (filters.moldSize.length > 0) count++;
    return count;
  };

  return (
    <div className="flex flex-col md:flex-row justify-between gap-4">
      <div className="relative w-full md:w-72">
        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={t("search_molds_placeholder")}
          className="pl-8"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={onRefresh}
          title={t("refresh_data")}
          className="h-10 w-10"
        >
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
            className="lucide lucide-refresh-cw"
          >
            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
            <path d="M21 3v5h-5" />
            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
            <path d="M3 21v-5h5" />
          </svg>
          <span className="sr-only">{t("refresh_button")}</span>
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              <span>{t("filters")}</span>
              {getActiveFilterCount() > 0 && (
                <Badge
                  variant="secondary"
                  className="ml-1 rounded-full px-1 py-0 h-5 min-w-5 flex items-center justify-center"
                >
                  {getActiveFilterCount()}
                </Badge>
              )}
              <ChevronDown className="h-4 w-4 ml-1" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-80 md:w-96 p-0" align="end">
            <div className="p-4 border-b flex items-center justify-between">
              <h4 className="font-medium">{t("filters")}</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearFilters}
                className="h-8 text-xs"
              >
                {t("clear_all")}
              </Button>
            </div>
            <div className="p-4 max-h-[70vh] overflow-y-auto">
              <FilterPanel
                technologies={technologies}
                alloys={alloys}
                tags={tags}
                moldSizes={moldSizes}
                filters={filters}
                setFilters={setFilters}
              />
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
        <Button className="flex items-center gap-2" onClick={onAddNew}>
          <Plus className="h-4 w-4" /> {t("add_new")}
        </Button>
      </div>
    </div>
  );
}
