"use client";

import React from "react";
import { SearchResult } from "@/hooks/useGlobalSearch";

interface SafeSearchDropdownProps {
  results: SearchResult[];
  isLoading: boolean;
  open: boolean;
  onSelect: (result: SearchResult) => void;
  className?: string;
}

// Completely disabled version
export function NewSafeSearchResultsDropdown(props: SafeSearchDropdownProps) {
  return null;
}
