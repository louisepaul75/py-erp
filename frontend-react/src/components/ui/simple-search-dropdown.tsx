"use client";

import React from "react";
import { SearchResult } from "@/hooks/useGlobalSearch";

interface SimpleSearchDropdownProps {
  results: SearchResult[];
  isLoading: boolean;
  open: boolean;
  onSelect: (result: SearchResult) => void;
  className?: string;
}

// Empty version that doesn't do any DOM manipulation
export function SimpleSearchDropdown({
  results = [],
  isLoading = false,
  open = false,
  onSelect,
  className = "",
}: SimpleSearchDropdownProps) {
  // Return null to prevent any rendering
  return null;
}
