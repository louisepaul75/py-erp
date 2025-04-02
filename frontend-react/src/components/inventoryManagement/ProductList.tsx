// components/ProductList.tsx
import { useState, useMemo, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Product } from "@/components/types/product";
import { ProductListProps } from "@/components/types/product";
import { SkinnyTable } from "@/components/ui/skinny-table";
import { StatusBadge } from "@/components/ui";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Search,
  X,
  Filter,
  ArrowUpDown,
  Sliders,
  Inbox,
  Tag,
  Bookmark,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

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
  totalItems,
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
  const [tableHeight, setTableHeight] = useState("calc(100vh - 250px)");

  useEffect(() => {
    // Handle responsive table height
    const updateTableHeight = () => {
      const windowHeight = window.innerHeight;
      setTableHeight(`calc(${windowHeight}px - 250px)`);
    };
    
    // Set initial height
    updateTableHeight();
    
    // Add event listener for window resize
    window.addEventListener("resize", updateTableHeight);
    
    // Clean up the event listener on component unmount
    return () => window.removeEventListener("resize", updateTableHeight);
  }, []);

  console.log("filteredProducts in ProductList", filteredProducts);
  console.log("totalItems in ProductList", totalItems);
  // Add debug logging for legacy_base_sku values
  console.log("Legacy SKU values:", filteredProducts?.map(product => ({
    id: product.id,
    sku: product.sku,
    legacy_base_sku: product.legacy_base_sku
  })));
  
  const sortedFilteredProducts = useMemo(() => {
    // Ensure filteredProducts is an array before sorting
    const productsToSort = Array.isArray(filteredProducts) ? filteredProducts : [];
    return [...productsToSort].sort((a, b) => {
      const aValue = a[sortField] ?? ""; // Fallback to an empty string if null/undefined
      const bValue = b[sortField] ?? ""; // Fallback to an empty string if null/undefined

      if (aValue < bValue) return sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });
  }, [filteredProducts, sortField, sortOrder]);

  // Calculate total pages - use the totalItems prop from parent
  const totalPages = Math.max(1, Math.ceil(totalItems / pagination.pageSize));

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
    <div className="h-full w-full border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
      {/* Search and Filters */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        {/* <div className="relative md:hidden mb-4">
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
        </div> */}
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
      <div className="flex-1 overflow-auto" style={{ height: tableHeight }}>
        <SkinnyTable
          data={sortedFilteredProducts}
          columns={[
            { field: "sku", header: "SKU" },
            { field: "name", header: "Name" },
            { 
              field: "legacy_base_sku", 
              header: "Legacy SKU",
              render: (item) => {
                // Custom renderer for legacy_base_sku field
                const value = item.legacy_base_sku;
                return value ? String(value) : "—";
              }
            },
            {
              field: "is_active",
              header: "Status",
              render: (item) => {
                const isActive = item.is_active;
                const variant = isActive ? "default" : "secondary"; // Map active/inactive to variants
                const colorClass = isActive 
                  ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-900/50" 
                  : "bg-gray-100 text-gray-800 dark:bg-gray-800/30 dark:text-gray-400 border border-gray-200 dark:border-gray-800/50"; // Keep original colors for now
                
                return (
                  <Badge
                    variant={variant}
                    className={cn("text-xs", colorClass)} // Apply original colors via className
                  >
                    {isActive ? "Active" : "Inactive"}
                  </Badge>
                );
              }
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
        <div className="flex justify-between items-center px-4 py-2">
          {/* Rows per page dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-600 dark:text-slate-400">
              Rows per page:
            </span>
            <Select
              value={pagination.pageSize.toString()}
              onValueChange={(value) => {
                const newPageSize = parseInt(value, 10);
                setPagination({
                  pageIndex: 0, // Reset to first page
                  pageSize: newPageSize,
                });
              }}
            >
              <SelectTrigger className="w-[100px] h-8 text-xs border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:ring-blue-500">
                <SelectValue placeholder="Size" />
              </SelectTrigger>
              <SelectContent>
                {[20, 30, 40, 50].map((size) => (
                  <SelectItem key={size} value={size.toString()}>
                    {size}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Page navigation */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-600 dark:text-slate-400">
              Page {pagination.pageIndex + 1} of {totalPages}
            </span>
            <div className="flex gap-1">
              <Button
                variant="outline"
                size="sm"
                className="h-8 px-2"
                onClick={() => setPagination({
                  ...pagination,
                  pageIndex: Math.max(0, pagination.pageIndex - 1)
                })}
                disabled={pagination.pageIndex === 0}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 px-2"
                onClick={() => {
                  console.log('Next page button clicked, current pageIndex:', pagination.pageIndex);
                  const newPageIndex = Math.min(totalPages - 1, pagination.pageIndex + 1);
                  console.log('Setting new pageIndex:', newPageIndex);
                  setPagination({
                    ...pagination,
                    pageIndex: newPageIndex
                  });
                }}
                disabled={pagination.pageIndex >= totalPages - 1}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
