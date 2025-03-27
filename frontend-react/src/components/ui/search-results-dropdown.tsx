"use client";

import React from "react";
import { SearchResult } from "@/hooks/useGlobalSearch";
import { cn } from "@/lib/utils";

interface SearchResultsDropdownProps {
  results: SearchResult[];
  isLoading: boolean;
  open: boolean;
  onSelect: (result: SearchResult) => void;
  className?: string;
}

export function SearchResultsDropdown({
  results,
  isLoading,
  open,
  onSelect,
  className
}: SearchResultsDropdownProps) {
  if (!open) {
    return <div data-testid="search-dropdown-hidden" className="hidden" />;
  }

  // Filter out invalid results
  const validResults = results?.filter((result): result is SearchResult => {
    return result && typeof result === 'object' && 
           'id' in result && typeof result.id === 'number' &&
           'type' in result && typeof result.type === 'string';
  }) ?? [];

  return (
    <div
      className={cn(
        "absolute z-50 w-full mt-1 bg-white rounded-md shadow-lg dark:bg-gray-800",
        className
      )}
      data-testid="search-dropdown"
    >
      {isLoading ? (
        <div className="p-4 text-center text-gray-500 dark:text-gray-400" data-testid="loading-state">
          Suchen...
        </div>
      ) : validResults.length === 0 ? (
        <div className="p-4 text-center text-gray-500 dark:text-gray-400" data-testid="no-results">
          Keine Ergebnisse gefunden
        </div>
      ) : (
        <div className="py-2">
          {validResults.map((result) => {
            const displayName = result.name || result.customer || "Unbekannt";
            let subtitle = "";
            
            switch (result.type) {
              case "customer":
                subtitle = `Kunde #${result.customer_number || ""}`;
                break;
              case "sales_record":
                subtitle = `Verkauf #${result.record_number || ""}`;
                break;
              case "variant_product":
              case "product":
                subtitle = `Artikel #${result.sku || ""}${result.legacy_sku ? ` (${result.legacy_sku})` : ""}`;
                break;
              case "box_slot":
                subtitle = `Box #${result.box_code || ""} - Slot ${result.slot_code || ""}`;
                break;
              case "storage_location":
                subtitle = `Lagerort ${result.location_code || ""}`;
                break;
              default:
                subtitle = result.type;
            }
            
            return (
              <button
                key={`${result.type}-${result.id}`}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => onSelect(result)}
                data-testid={`result-${result.id}`}
              >
                <div className="font-medium" data-testid={`result-name-${result.id}`}>
                  {displayName}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400" data-testid={`result-subtitle-${result.id}`}>
                  {subtitle}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
