// components/ProductList.tsx
import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Product } from "@/components/types/product";
import { ProductListProps } from "@/components/types/product";
import { Spinner } from "@radix-ui/themes";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
// import {
//   Table,
//   Flex,
//   Text,
//   Select,
//   Box,
//   Badge as RadixBadge,
// } from "@radix-ui/themes";

import {
  Search,
  X,
  Filter,
  ArrowUpDown,
  Sliders,
  Inbox,
  Tag,
  Bookmark,
} from "lucide-react";

// interface Product {
//   nummer: string;
//   bezeichnung: string;
//   status: string;
// }

export default function ProductList({
  showSidebar,
  searchTerm,
  setSearchTerm,
  filteredProducts,
  selectedItem,
  setSelectedItem,
  pagination,
  setPagination,
  isLoading,
}: ProductListProps) {
  const [sortField, setSortField] = useState<keyof Product>("id");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50";
      case "inactive":
        return "bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400 border-amber-200 dark:border-amber-900/50";
      case "draft":
        return "bg-slate-50 text-slate-700 dark:bg-slate-800/50 dark:text-slate-400 border-slate-200 dark:border-slate-700";
      default:
        return "bg-slate-50 text-slate-700 dark:bg-slate-800/50 dark:text-slate-400 border-slate-200 dark:border-slate-700";
    }
  };

  console.log("filteredProducts in ProductList", filteredProducts);
  const sortedFilteredProducts = useMemo(() => {
    return [...filteredProducts].sort((a, b) => {
      const aValue = a[sortField] ?? ""; // Fallback to an empty string if null/undefined
      const bValue = b[sortField] ?? ""; // Fallback to an empty string if null/undefined

      if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [filteredProducts, sortField, sortOrder]);

  const handleSort = (field: keyof Product) => {
    setSortField(field);
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
  };

  return (
    <div className="w-full md:w-80 lg:w-96 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
      {/* Search and Filters */}
      <div className="p-4 border-b border-stalte-200 dark:border-slate-800">
        <div className="relative md:hidden mb-4">
          <Input
            className="w-full pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-blue-500"
            placeholder="Suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="absolute left-3 top-1/2 -translate-y-1/2">
            <Search className="h-4 w-4 text-slate-400" />
          </div>
          {searchTerm && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full"
              onClick={() => setSearchTerm("")}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-slate-900 dark:text-slate-100">
            Produkte
          </h2>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full"
            >
              <Filter className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full"
              onClick={() => handleSort("sku")} // Default sort by SKU
              aria-label="Sort by SKU"
            >
              <ArrowUpDown className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full"
            >
              <Sliders className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Product List */}
      <div className="flex-1 overflow-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <TableHead
                className="font-medium cursor-pointer"
                onClick={() => handleSort("sku")}
              >
                <div className="flex items-center gap-2">
                  SKU
                  {sortField === "sku" && (
                    <span>{sortOrder === "asc" ? "↑" : "↓"}</span>
                  )}
                </div>
              </TableHead>
              <TableHead
                className="font-medium cursor-pointer"
                onClick={() => handleSort("name")}
              >
                <div className="flex items-center gap-2">
                  Name
                  {sortField === "name" && (
                    <span>{sortOrder === "asc" ? "↑" : "↓"}</span>
                  )}
                </div>
              </TableHead>
              <TableHead
                className="font-medium cursor-pointer"
                onClick={() => handleSort("legacy_base_sku")}
              >
                <div className="flex items-center gap-2">
                  Legacy Base Sku
                  {sortField === "legacy_base_sku" && (
                    <span>{sortOrder === "asc" ? "↑" : "↓"}</span>
                  )}
                </div>
              </TableHead>
              <TableHead
                className="font-medium cursor-pointer"
                onClick={() => handleSort("variants_count")}
              >
                <div className="flex items-center gap-2">
                  Variants
                  {sortField === "variants_count" && (
                    <span>{sortOrder === "asc" ? "↑" : "↓"}</span>
                  )}
                </div>
              </TableHead>
            </TableRow>
          </TableHeader>

          <TableBody className="min-h-[500px]">
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={3} className="text-center py-8">
                  <div className="flex justify-center items-center gap-2 min-h-[500px]">
                    <Spinner size="3" />
                    <span>Loading products...</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : sortedFilteredProducts.length > 0 ? (
              sortedFilteredProducts.map((product) => (
                <TableRow
                  key={product.sku}
                  onClick={() => setSelectedItem(product.id)}
                  className={`cursor-pointer transition-colors ${
                    selectedItem === product.id
                      ? "bg-blue-50 dark:bg-blue-900/20"
                      : "hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <TableCell
                    className={
                      selectedItem === product.sku ? "font-medium" : ""
                    }
                  >
                    {product.sku}
                  </TableCell>
                  <TableCell
                    className={
                      selectedItem === product.sku ? "font-medium" : ""
                    }
                  >
                    {product.legacy_base_sku}
                  </TableCell>
                  <TableCell
                    className={
                      selectedItem === product.sku ? "font-medium" : ""
                    }
                  >
                    {product.name || "—"}
                  </TableCell>
                  <TableCell
                    className={
                      selectedItem === product.sku ? "font-medium" : ""
                    }
                  >
                    {product.variants_count}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} className="text-center py-8">
                  <div className="flex justify-center items-center gap-2 min-h-[500px]">
                    <span>No products found</span>
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>

        {/* Pagination Controls */}
        <div className="flex flex-col w-full ">
          <div className="flex justify-center items-center gap-2 my-2">
            <span className="text-sm text-slate-600 dark:text-slate-400">
              Rows per page:
            </span>
            <select
              value={pagination.pageSize}
              onChange={(e) => {
                setPagination({
                  pageIndex: 0, // Reset to first page
                  pageSize: Number(e.target.value),
                });
              }}
              className="text-sm rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
            >
              {[20, 30, 40].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-center items-center gap-2">
            <Button
              variant="outline"
              disabled={pagination.pageIndex === 0}
              onClick={() =>
                setPagination({
                  ...pagination,
                  pageIndex: pagination.pageIndex - 1,
                })
              }
            >
              Previous
            </Button>
            {/* <Text className="mx-6" size="2">
              Page {pagination.pageIndex + 1}
            </Text> */}
            <p className="mx-6">Page {pagination.pageIndex + 1}</p>
            <Button
              variant="outline"
              disabled={filteredProducts.length < pagination.pageSize}
              onClick={() =>
                setPagination({
                  ...pagination,
                  pageIndex: pagination.pageIndex + 1,
                })
              }
            >
              Next
            </Button>
          </div>
        </div>
      </div>

      {/* <div className="flex-1 overflow-auto">
        {filteredProducts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-4 text-center">
            <Inbox className="h-12 w-12 text-slate-300 dark:text-slate-600 mb-2" />
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Keine Produkte gefunden
            </p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
              Versuchen Sie, Ihre Suchkriterien zu ändern
            </p>
          </div>
        ) : (
          <div className="p-2">
            <div className="grid grid-cols-[auto_1fr_auto] gap-2 font-medium text-sm text-slate-500 dark:text-slate-400 p-2 bg-slate-50 dark:bg-slate-800/50 rounded-t-lg">
              <div className="cursor-pointer" onClick={() => handleSort("sku")}>
                Nummer
                {sortField === "sku" && (
                  <span>{sortOrder === "asc" ? " ↑" : " ↓"}</span>
                )}
              </div>
              <div
                className="cursor-pointer"
                onClick={() => handleSort("name")}
              >
                Bezeichnung
                {sortField === "name" && (
                  <span>{sortOrder === "asc" ? " ↑" : " ↓"}</span>
                )}
              </div>
            </div>
            {sortedFilteredProducts.map((product) => (
              <div
                key={product.sku}
                className={`p-3 my-1 rounded-xl cursor-pointer transition-all ${
                  selectedItem === product.sku
                    ? "bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500"
                    : "hover:bg-slate-50 dark:hover:bg-slate-800/50 border-l-4 border-transparent"
                }`}
                onClick={() => setSelectedItem(product.sku)}
              >
                <div className="grid grid-cols-[auto_1fr_auto] gap-2 items-center">
                  <div className="font-medium">{product.sku}</div>
                  <div className="text-sm text-slate-500 dark:text-slate-400 truncate">
                    {product.name || "—"}
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Badge
                    variant="secondary"
                    className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    Zinnfigur
                  </Badge>
                  <Badge
                    variant="secondary"
                    className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                  >
                    <Bookmark className="h-3 w-3 mr-1" />
                    Eisenbahn
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </div> */}
    </div>
  );
}
