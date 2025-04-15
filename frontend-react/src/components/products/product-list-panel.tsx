// components/products/ProductListPane.tsx
import React from "react";
import { Input } from "@/components/ui/input";
import {
  Search,
  PlusCircle,
  ChevronLeft,
  ChevronRight,
  Filter,
  ArrowUpDown,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import Image from "next/image";
import { Product, ApiResponse } from "@/components/types/product";
import { UseQueryResult } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";

// Type for sort direction
type SortDirection = 'asc' | 'desc';

// Type for sort configuration
interface SortConfig {
  key: keyof Product | null;
  direction: SortDirection;
}

interface ProductListPaneProps {
  productsQuery: UseQueryResult<ApiResponse<Product>, Error>;
  products: Product[];
  selectedItemId: number | null;
  isEditing: boolean;
  onSelectItem: (id: number) => void;
  onCreateNew: () => void;
  onPaginationChange: (direction: "prev" | "next") => void;
  pagination: { pageIndex: number; pageSize: number };
  searchTerm: string;
  onSearchChange: (term: string) => void;
  sortConfig: SortConfig;
  requestSort: (key: keyof Product) => void;
  onFilterToggle: () => void;
  filterActive: boolean;
}

export function ProductListPane({
  productsQuery,
  products,
  selectedItemId,
  isEditing,
  onSelectItem,
  onCreateNew,
  onPaginationChange,
  pagination,
  searchTerm,
  onSearchChange,
  sortConfig,
  requestSort,
  onFilterToggle,
  filterActive,
}: ProductListPaneProps) {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(e.target.value);
  };

  const handlePaginationChangeInternal = (direction: "prev" | "next") => {
    if (isEditing) {
      alert(
        "Please save or cancel your current changes before changing pages."
      );
      return;
    }
    onPaginationChange(direction);
  };

  // const products = productsQuery.data?.results ?? [];
  console.log ("in product list pane the products are", products)
  const totalCount = productsQuery.data?.count ?? 0;

  // Helper function to render sort indicator
  const renderSortIndicator = (key: keyof Product) => {
    if (sortConfig.key === key) {
      return (
        <ArrowUpDown
          className={`ml-2 h-3 w-3 ${
            sortConfig.direction === "asc" ? "" : "rotate-180"
          }`}
        />
      );
    }
    return <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />;
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="p-4">
        <h2 className="text-xl font-semibold">Product List</h2>
        <div className="flex items-center justify-between mt-2 space-x-2">
          <div className="relative flex-grow">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="search"
              placeholder="Search SKU or Name..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="pl-10 h-9 w-full"
              disabled={productsQuery.isFetching || isEditing}
            />
            {/* Add clear button for search */}
            {searchTerm && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full text-muted-foreground hover:text-foreground"
                onClick={() => onSearchChange("")}
                disabled={isEditing}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
          <Button
            variant={filterActive ? "default" : "outline"}
            size="icon"
            aria-label="Filter Active Products"
            onClick={onFilterToggle}
            disabled={productsQuery.isFetching || isEditing}
            title={filterActive ? "Showing active products only" : "Showing all products"}
          >
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <div className="flex-grow flex flex-col overflow-hidden min-h-0 px-4">
        {productsQuery.isLoading ? (
          <p>Loading products...</p>
        ) : productsQuery.isError ? (
          <p>Error loading products: {productsQuery.error?.message}</p>
        ) : products.length > 0 ? (
          <>
            <div className="flex-1 overflow-y-auto h-full">
              <Table>
                <TableCaption>
                  Product List - Page {pagination.pageIndex + 1}
                </TableCaption>
                <TableHeader>
                  <TableRow>
                    <TableHead>Image</TableHead>
                    {/* SKU - Sortable */}
                    <TableHead>
                      <Button
                        variant="ghost"
                        onClick={() => requestSort("sku")}
                        className="px-0 hover:bg-transparent"
                      >
                        SKU
                        {renderSortIndicator("sku")}
                      </Button>
                    </TableHead>
                    {/* Legacy SKU - Sortable */}
                    <TableHead>
                      <Button
                        variant="ghost"
                        onClick={() => requestSort("legacy_base_sku")}
                        className="px-0 hover:bg-transparent"
                      >
                        Legacy SKU
                        {renderSortIndicator("legacy_base_sku")}
                      </Button>
                    </TableHead>
                    {/* Name - Sortable */}
                    <TableHead>
                      <Button
                        variant="ghost"
                        onClick={() => requestSort("name")}
                        className="px-0 hover:bg-transparent"
                      >
                        Name
                        {renderSortIndicator("name")}
                      </Button>
                    </TableHead>
                    {/* Active - Sortable */}
                    <TableHead>
                      <Button
                        variant="ghost"
                        onClick={() => requestSort("is_active")}
                        className="px-0 hover:bg-transparent"
                      >
                        Active
                        {renderSortIndicator("is_active")}
                      </Button>
                    </TableHead>
                    {/* Variants - Sortable */}
                    <TableHead>
                      <Button
                        variant="ghost"
                        onClick={() => requestSort("variants_count")}
                        className="px-0 hover:bg-transparent"
                      >
                        Variants
                        {renderSortIndicator("variants_count")}
                      </Button>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {products.map((product) => (
                    <TableRow
                      key={product.id}
                      className={
                        selectedItemId === product.id
                          ? "bg-primary/10"
                          : undefined
                      }
                      onClick={() => onSelectItem(product.id)}
                    >
                      <TableCell>
                        {product.primary_image ? (
                          <Image
                            src={
                              product.primary_image.thumbnail_url ||
                              product.primary_image.image_url
                            }
                            alt={product.name}
                            width={40}
                            height={40}
                            className="rounded object-cover"
                          />
                        ) : (
                          <></>
                        )}
                      </TableCell>
                      <TableCell>{product.sku}</TableCell>
                      <TableCell>{product.legacy_base_sku}</TableCell>
                      <TableCell>{product.name}</TableCell>
                      <TableCell>
                        <Badge variant={product.is_active ? "default" : "secondary"}>
                          {product.is_active ? "Yes" : "No"}
                        </Badge>
                      </TableCell>
                      <TableCell>{product.variants_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {totalCount > 0 && (
              <div className="mt-4 flex justify-between items-center px-2 py-1 border-t flex-shrink-0">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePaginationChangeInternal("prev")}
                  disabled={
                    pagination.pageIndex === 0 ||
                    productsQuery.isFetching ||
                    isEditing
                  }
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {pagination.pageIndex + 1} of{" "}
                  {Math.ceil(totalCount / pagination.pageSize)}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePaginationChangeInternal("next")}
                  disabled={
                    pagination.pageIndex + 1 >=
                      Math.ceil(totalCount / pagination.pageSize) ||
                    productsQuery.isFetching ||
                    isEditing
                  }
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            )}
          </>
        ) : (
          <p className="text-muted-foreground text-center p-4">
            No products found{searchTerm ? " matching your search" : ""}.
          </p>
        )}
      </div>
      <div className="p-4 border-t flex-shrink-0">
        <Button className="w-full" onClick={onCreateNew} disabled={isEditing}>
          <PlusCircle className="mr-2 h-4 w-4" />
          New Product
        </Button>
      </div>
    </div>
  );
}
