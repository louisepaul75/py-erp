"use client";

import React from "react";

// Empty type definition to maintain interfaces
export type SearchResult = {
  id: number;
  type: string;
  name?: string;
  customer_number?: string;
  record_number?: string;
  record_type?: string;
  customer?: string;
  sku?: string;
  legacy_sku?: string;
  barcode?: string;
  legacy_id?: string;
  box_code?: string;
  slot_code?: string;
  location_code?: string;
};

interface SimpleGlobalSearchProps {
  className?: string;
  onResultSelect?: (result: SearchResult) => void;
  placeholder?: string;
}

// Completely disabled version of SimpleGlobalSearch
export function SimpleGlobalSearch({
  className,
  onResultSelect,
  placeholder = "Suchen...",
}: SimpleGlobalSearchProps) {
  // Return an empty div that doesn't perform any DOM operations
  return <div className={className} aria-label="Search disabled"></div>;
}
