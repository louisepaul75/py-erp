"use client";

import React from "react";
import { SearchResult } from "@/hooks/useGlobalSearch";
import { BadgeCheck, Box, FileText, Inbox, Package, User } from "lucide-react";
import { Card, CardContent } from "./card";
import { cn } from "@/lib/utils";

// Debug logger function with component identification
const logDebug = (message: string, data?: any) => {
  const timestamp = new Date().toISOString();
  console.log(`[SearchResultsDropdown][${timestamp}] ${message}`, data || '');
};

// Error logger with component identification
const logError = (message: string, error?: any) => {
  const timestamp = new Date().toISOString();
  console.error(`[SearchResultsDropdown][${timestamp}] ERROR: ${message}`, error || '');
  
  // Log stack trace if available
  if (error?.stack) {
    console.error(`[SearchResultsDropdown][${timestamp}] Stack:`, error.stack);
  }
};

// Custom error boundary component
class SearchErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode; fallback?: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logError("Error caught by boundary:", error);
    console.error("Error info:", errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // Render fallback UI or default error message
      return this.props.fallback || (
        <div className="p-4 text-red-500 border border-red-300 rounded bg-red-50">
          <p className="font-semibold">Something went wrong with the search results.</p>
          <p className="text-sm mt-2">Please try again later.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

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

// The inner component implementation
function SearchResultsDropdownInner({
  results,
  isLoading,
  open,
  onSelect,
  className,
}: SearchResultsDropdownProps) {
  // Add componentId to track specific component instances
  const componentId = React.useRef(`search-dropdown-${Math.random().toString(36).substring(2, 9)}`);
  
  // Ref to track if component is mounted
  const isMounted = React.useRef(true);
  
  // Log component mount
  React.useEffect(() => {
    logDebug(`Component mounted. ID: ${componentId.current}`, { 
      isOpen: open, 
      resultsCount: Array.isArray(results) ? results.length : 0,
      isLoading 
    });
    
    return () => {
      // Log before unmounting
      logDebug(`Component unmounting. ID: ${componentId.current}`);
      isMounted.current = false;
    };
  }, []);
  
  // Log prop changes
  React.useEffect(() => {
    logDebug(`Props updated. ID: ${componentId.current}`, { 
      isOpen: open, 
      resultsCount: Array.isArray(results) ? results.length : 0,
      isLoading 
    });
  }, [results, isLoading, open]);
  
  // Return empty div instead of null to avoid DOM reconciliation issues
  if (!open) {
    logDebug(`Component is closed (not rendering results). ID: ${componentId.current}`);
    return <div style={{ display: 'none' }} data-testid="search-dropdown-hidden" />;
  }

  // Ensure we have valid results and filter out any invalid entries
  const safeResults = Array.isArray(results) 
    ? results.filter((result): result is SearchResult => (
        result !== null && 
        result !== undefined && 
        typeof result === 'object' &&
        'id' in result &&
        typeof result.id === 'number' &&
        'type' in result &&
        typeof result.type === 'string'
      ))
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
              
              // Safely determine the icon component with proper type checking
              const resultType = result?.type as keyof typeof TypeIcons | undefined;
              const IconComponent = resultType && TypeIcons[resultType] 
                ? TypeIcons[resultType] 
                : Package;
              
              // Ensure we have a valid result and safely extract the display name
              const displayName = (() => {
                if (!result) return "Unbekannt";
                
                // Type-safe property access
                const getValue = (key: keyof SearchResult): string | undefined => {
                  const value = result[key];
                  return typeof value === 'string' ? value.trim() : undefined;
                };
                
                // Try each field in order of preference
                return getValue('name') ||
                       getValue('customer_number') ||
                       getValue('record_number') ||
                       getValue('sku') ||
                       getValue('barcode') ||
                       getValue('legacy_id') ||
                       "Unbekannt";
              })();
              
              // Generate a stable key that won't be undefined
              const itemKey = result.id 
                ? `${result.type || 'unknown'}-${result.id}` 
                : `unknown-${Math.random()}`;
              
              return (
                <li
                  key={itemKey}
                  onClick={(e) => {
                    try {
                      logDebug(`Item clicked. ID: ${componentId.current}, ItemKey: ${itemKey}`, {
                        resultId: result.id,
                        resultType: result.type
                      });
                      
                      e.preventDefault();
                      
                      // Validate DOM element exists and is valid
                      if (!e.currentTarget) {
                        logError(`Click target is null/undefined. ID: ${componentId.current}`);
                        return;
                      }
                      
                      // Double check for null/undefined before accessing textContent
                      const elementsWithText = e.currentTarget.querySelectorAll('*');
                      for (let i = 0; i < elementsWithText.length; i++) {
                        const el = elementsWithText[i];
                        if (el && el.textContent === null) {
                          logError(`Found element with null textContent. ID: ${componentId.current}`, {
                            elementTagName: el.tagName,
                            elementClassName: el.className
                          });
                        }
                      }
                      
                      // Check if component is still mounted before executing the callback
                      if (isMounted.current && typeof onSelect === 'function') {
                        logDebug(`Calling onSelect callback. ID: ${componentId.current}`);
                        onSelect(result);
                      } else {
                        logError(`Cannot call onSelect - component unmounted or callback invalid. ID: ${componentId.current}`);
                      }
                    } catch (error) {
                      logError(`Error handling click event. ID: ${componentId.current}`, error);
                    }
                  }}
                  className="flex cursor-pointer items-center gap-3 p-3 hover:bg-muted"
                  data-item-id={result.id}
                  data-item-type={result.type}
                >
                  {/* Ensure icon is always rendered */}
                  <div className="flex-shrink-0">
                    <IconComponent className="h-4 w-4 text-muted-foreground" />
                  </div>
                  
                  <div className="flex-1 overflow-hidden">
                    <div className="font-medium">
                      {/* Always render a string, never null/undefined */}
                      {String(displayName || "Unbekannt")}
                    </div>
                    
                    <div className="truncate text-xs text-muted-foreground">
                      {/* Ensure we always render a string */}
                      {String(getResultSubtitle(result) || "")}
                    </div>
                  </div>
                  
                  <span className="text-xs text-muted-foreground capitalize">
                    {/* Ensure we always render a string */}
                    {String(getResultTypeName(result?.type) || "")}
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

// Wrap the implementation in the error boundary
export function SearchResultsDropdown(props: SearchResultsDropdownProps) {
  return (
    <SearchErrorBoundary>
      <SearchResultsDropdownInner {...props} />
    </SearchErrorBoundary>
  );
}

// Safely convert any value to a string, returning empty string if null/undefined
const safeString = (value: any): string => {
  if (value === null || value === undefined) return '';
  return String(value).trim();
};

function getResultTypeName(type: string | null | undefined): string {
  const typeMap: Record<string, string> = {
    customer: "Kunde",
    sales_record: "Verkaufsbeleg",
    parent_product: "Produktgruppe",
    variant_product: "Produkt",
    box_slot: "Box",
    storage_location: "Lager"
  };
  
  const safeType = safeString(type);
  return safeType ? (typeMap[safeType as keyof typeof typeMap] || safeType) : "";
}

function getResultSubtitle(result: SearchResult | null | undefined): string {
  if (!result?.type) return "";

  try {
    switch (result.type) {
      case "customer":
        return `Kunde #${safeString(result.customer_number)}`;
      
      case "sales_record":
        return [
          safeString(result.record_type),
          `#${safeString(result.record_number)}`,
          result.customer ? `- ${safeString(result.customer)}` : ""
        ].filter(Boolean).join(" ");
      
      case "parent_product":
        return `Gruppe #${safeString(result.sku)}`;
      
      case "variant_product":
        return [
          `Artikel #${safeString(result.sku)}`,
          result.legacy_sku ? `(${safeString(result.legacy_sku)})` : ""
        ].filter(Boolean).join(" ");
      
      case "box_slot":
        return [
          safeString(result.box_code),
          "-",
          safeString(result.slot_code)
        ].filter(Boolean).join(" ");
      
      case "storage_location":
        return [
          "Lager",
          `#${safeString(result.legacy_id)}`,
          "-",
          safeString(result.location_code)
        ].filter(Boolean).join(" ");
      
      default:
        return "";
    }
  } catch (error) {
    console.error('Error generating subtitle:', error);
    return "";
  }
}
