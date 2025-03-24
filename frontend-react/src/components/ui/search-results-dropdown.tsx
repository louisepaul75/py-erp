"use client";

import React from "react";
import { SearchResult } from "@/hooks/useGlobalSearch";
import { BadgeCheck, Box, FileText, Inbox, Package, User } from "lucide-react";
import { Card, CardContent } from "./card";
import { cn } from "@/lib/utils";

interface SearchResultsDropdownProps {
  results: SearchResult[];
  isLoading: boolean;
  open: boolean;
  onSelect: (result: SearchResult) => void;
  className?: string;
}

const TypeIcons = {
  customer: User,
  sales_record: FileText,
  parent_product: Package,
  variant_product: BadgeCheck,
  box_slot: Box,
  storage_location: Inbox,
};

export function SearchResultsDropdown({
  results,
  isLoading,
  open,
  onSelect,
  className,
}: SearchResultsDropdownProps) {
  if (!open) return null;

  const safeResults = Array.isArray(results) 
    ? results.filter(result => result !== null && result !== undefined) 
    : [];

  return (
    <Card
      className={cn(
        "absolute top-full left-0 right-0 z-50 mt-1 max-h-[400px] overflow-auto shadow-lg",
        className
      )}
    >
      <CardContent className="p-0">
        {isLoading ? (
          <div className="flex items-center justify-center p-4">
            <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-t-2 border-blue-600"></div>
            <span className="ml-2 text-sm text-muted-foreground">Suchen...</span>
          </div>
        ) : safeResults.length > 0 ? (
          <ul className="divide-y divide-border">
            {safeResults.map((result) => {
              if (!result) return null;
              
              const IconComponent = result?.type && TypeIcons[result.type as keyof typeof TypeIcons] 
                ? TypeIcons[result.type as keyof typeof TypeIcons] 
                : Package;
              
              const displayName = result?.name || 
                                result?.customer_number || 
                                result?.record_number || 
                                result?.sku || 
                                result?.barcode || 
                                result?.legacy_id || 
                                "Unbekannt";
              
              const itemKey = `${result.type || 'unknown'}-${result.id || Math.random()}`;
              
              return (
                <li
                  key={itemKey}
                  onClick={() => onSelect(result)}
                  className="flex cursor-pointer items-center gap-3 p-3 hover:bg-muted"
                >
                  <IconComponent className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
                  
                  <div className="flex-1 overflow-hidden">
                    <div className="font-medium">
                      {displayName}
                    </div>
                    
                    <div className="truncate text-xs text-muted-foreground">
                      {getResultSubtitle(result)}
                    </div>
                  </div>
                  
                  <span className="text-xs text-muted-foreground capitalize">
                    {getResultTypeName(result?.type || '')}
                  </span>
                </li>
              );
            })}
          </ul>
        ) : (
          <div className="p-4 text-center text-sm text-muted-foreground">
            Keine Ergebnisse gefunden
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function getResultTypeName(type: string): string {
  if (!type) return "";
  
  const typeMap: Record<string, string> = {
    customer: "Kunde",
    sales_record: "Verkaufsbeleg",
    parent_product: "Produktgruppe",
    variant_product: "Produkt",
    box_slot: "Box",
    storage_location: "Lager"
  };
  
  return typeMap[type] || type;
}

function getResultSubtitle(result: SearchResult): string {
  if (!result) return "";

  if (result.type === "customer") {
    return `Kunde #${result.customer_number || ""}`;
  } else if (result.type === "sales_record") {
    return `${result.record_type || ""} #${result.record_number || ""} ${result.customer ? `- ${result.customer}` : ""}`;
  } else if (result.type === "parent_product") {
    return `Gruppe #${result.sku || ""}`;
  } else if (result.type === "variant_product") {
    return `Artikel #${result.sku || ""} ${result.legacy_sku ? `(${result.legacy_sku})` : ""}`;
  } else if (result.type === "box_slot") {
    return `${result.box_code || ""} - ${result.slot_code || ""}`;
  } else if (result.type === "storage_location") {
    return `Lager #${result.legacy_id || ""} - ${result.location_code || ""}`;
  }
  
  return "";
} 