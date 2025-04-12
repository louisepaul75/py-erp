"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  className,
}: PaginationProps) {
  const getPageNumbers = (): (number | string)[] => {
    const pages: (number | string)[] = [];
    const maxPagesToShow = 5; // Number of page links/ellipses shown between prev/next

    if (totalPages <= 1) {
        return []; // No pages needed if 0 or 1 total pages
    }

    // Always show first page
    pages.push(1);

    if (totalPages <= maxPagesToShow + 2) { // Show all pages if total fits (1 ... 2 3 4 5 ... 6 -> max 7 buttons total)
        for (let i = 2; i < totalPages; i++) {
            pages.push(i);
        }
    } else {
        // Calculate range with ellipses
        let start = Math.max(2, currentPage - 1);
        let end = Math.min(totalPages - 1, currentPage + 1);

        // Adjust range if near beginning or end to maintain roughly maxPagesToShow links
         if (currentPage <= 3) { // Show 1, 2, 3, 4 ... last
             end = Math.min(totalPages - 1, 4);
         }
         if (currentPage >= totalPages - 2) { // Show 1 ... last-3, last-2, last-1, last
             start = Math.max(2, totalPages - 3);
         }

        // Add left ellipsis if needed
        if (start > 2) {
            pages.push("...");
        }

        // Add page numbers in the calculated range
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }

        // Add right ellipsis if needed
        if (end < totalPages - 1) {
            pages.push("...");
        }
    }

    // Always show last page if totalPages > 1
    if (totalPages > 1) {
        pages.push(totalPages);
    }

    // Remove duplicates that might arise from simple logic (e.g., totalPages=2 pushing 1, 2)
    // A Set ensures uniqueness.
    return Array.from(new Set(pages));
  };

  const pageNumbers = getPageNumbers();

  // Don't render if only one page
  if (totalPages <= 1) {
    return null;
  }

  return (
    <nav
      role="navigation"
      aria-label="pagination"
      className={cn("flex items-center justify-center space-x-1 py-4", className)}
    >
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Go to previous page"
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>

      {pageNumbers.map((page, index) =>
        typeof page === "string" ? (
           // Render ellipsis as non-interactive element
          <span
            key={`ellipsis-${index}`}
            className="flex h-9 w-9 items-center justify-center px-1 text-sm font-medium"
          >
            {page}
          </span>
        ) : (
          // Render page number button
          <Button
            key={page}
            variant={currentPage === page ? "default" : "outline"}
            size="icon"
            onClick={() => onPageChange(page)}
            aria-current={currentPage === page ? "page" : undefined}
            aria-label={`Go to page ${page}`}
          >
            {page}
          </Button>
        )
      )}

      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="Go to next page"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </nav>
  );
} 