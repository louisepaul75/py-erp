"use client";

import React from "react";
import { SearchResult } from "@/hooks/useGlobalSearch";

interface SafeSearchResultsDropdownProps {
  results: SearchResult[];
  isLoading: boolean;
  open: boolean;
  onSelect: (result: SearchResult) => void;
  className?: string;
}

// Completely disabled version
export function SafeSearchResultsDropdown(props: SafeSearchResultsDropdownProps) {
  return null;
} 