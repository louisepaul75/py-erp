// components/ProductList.tsx
import { useState, useMemo } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Product } from "@/components/types/product";
import { ProductListProps } from "@/components/types/product";
import { SkinnyTable } from "@/components/ui/skinny-table";
import { StatusBadge } from "@/components/ui";
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
  const router = useRouter();
  const pathname = usePathname();
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

  const handleItemSelect = (item: any) => {
    setSelectedItem(item.id);
    const newPath = item.variants_count > 0
      ? `/products/parent/${item.id}`
      : `/products/variant/${item.id}`;
    
    if (pathname !== newPath) {
      router.push(newPath);
    }
  };

  return (
    <div className="w-full md:w-80 lg:w-96 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
      {/* Search and Filters */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
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
              className="h-8 w-8 rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <Filter className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
              onClick={() => handleSort("sku")} // Default sort by SKU
              aria-label="Sort by SKU"
            >
              <ArrowUpDown className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <Sliders className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Product List */}
      <div className="flex-1 overflow-auto">
        <SkinnyTable
          data={filteredProducts}
          columns={[
            { field: "sku", header: "SKU" },
            { field: "name", header: "Name" },
            { field: "legacy_base_sku", header: "Legacy SKU" },
            {
              field: "is_active",
              header: "Status",
              render: (item) => (
                <StatusBadge
                  status={item.is_active ? "active" : "inactive"}
                  className="text-xs"
                >
                  {item.is_active ? "Active" : "Inactive"}
                </StatusBadge>
              ),
            },
          ]}
          selectedItem={selectedItem}
          onItemSelect={handleItemSelect}
          isLoading={isLoading}
          noDataMessage="No products found"
        />
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-col w-full border-t border-slate-200 dark:border-slate-800">
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
            className="text-sm rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
          >
            {[20, 30, 40].map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
