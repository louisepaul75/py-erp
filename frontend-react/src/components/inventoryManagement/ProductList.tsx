// components/ProductList.tsx
import { useState, useMemo, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Product } from "@/components/types/product";
import { ProductListProps } from "@/components/types/product";
import { StatusBadge } from "@/components/ui";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDataTable } from "@/hooks/useDataTable";
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
  
  // Use the DataTable hook, primarily for sorting
  const { 
    processedData: sortedProducts, // Data sorted client-side by the hook
    sortConfig,
    requestSort
    // We DON'T use the hook's searchTerm/setSearchTerm here
  } = useDataTable<Product>({
    initialData: filteredProducts || [], // Pass potentially pre-filtered data
    initialSortKey: 'sku', // Set initial sort
    // No searchableFields needed as we rely on external filtering via props
  });

  // Calculate total pages - use the totalItems prop from parent
  const totalPages = Math.max(1, Math.ceil(totalItems / pagination.pageSize));

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
              className="rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <Filter className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <Sliders className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Product List - Use standard Table */}
      <div className="flex-1 overflow-auto" style={{ height: tableHeight }}>
        <Table className="h-full">
          <TableHeader>
            <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800/50">
              {/* SKU Header */}
              <TableHead className="font-medium text-slate-700 dark:text-slate-300">
                 <Button variant="ghost" onClick={() => requestSort('sku')} className="px-0 hover:bg-transparent">
                   SKU
                    {sortConfig.key === 'sku' && (
                     <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                    )}
                    {sortConfig.key !== 'sku' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                 </Button>
              </TableHead>
              {/* Name Header */}
              <TableHead className="font-medium text-slate-700 dark:text-slate-300">
                 <Button variant="ghost" onClick={() => requestSort('name')} className="px-0 hover:bg-transparent">
                   Name
                    {sortConfig.key === 'name' && (
                     <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                    )}
                    {sortConfig.key !== 'name' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                 </Button>
              </TableHead>
              {/* Legacy SKU Header - Assuming not sortable or handle if needed */}
              <TableHead className="font-medium text-slate-700 dark:text-slate-300">
                 Legacy SKU
                 {/* Add sort button if legacy_base_sku should be sortable */}
                 {/* <Button variant="ghost" onClick={() => requestSort('legacy_base_sku')} ...> ... </Button> */}
              </TableHead>
              {/* Status Header */}
              <TableHead className="font-medium text-slate-700 dark:text-slate-300">
                 <Button variant="ghost" onClick={() => requestSort('is_active')} className="px-0 hover:bg-transparent">
                   Status
                    {sortConfig.key === 'is_active' && (
                     <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                    )}
                    {sortConfig.key !== 'is_active' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                 </Button>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody className="relative h-full">
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8"> {/* Adjust colSpan */} 
                  <div className="flex justify-center items-center gap-2 h-full">
                    <span className="text-slate-600 dark:text-slate-400">Loading...</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : sortedProducts.length > 0 ? (
              sortedProducts.map((item) => (
                <TableRow
                  key={item.id} // Use id as key
                  onClick={() => handleItemSelect?.(item)}
                  className={cn(
                    "cursor-pointer transition-colors",
                    selectedItem === item.id // Use id for selection check
                      ? "bg-blue-50 dark:bg-blue-900/20 text-slate-900 dark:text-slate-100"
                      : "hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-800 dark:text-slate-300"
                  )}
                >
                  {/* SKU Cell */}
                  <TableCell className={selectedItem === item.id ? "font-medium" : ""}>{item.sku}</TableCell>
                  {/* Name Cell */}
                  <TableCell className={selectedItem === item.id ? "font-medium" : ""}>{item.name}</TableCell>
                  {/* Legacy SKU Cell */}
                  <TableCell className={selectedItem === item.id ? "font-medium" : ""}>
                    {item.legacy_base_sku ? String(item.legacy_base_sku) : "—"}
                  </TableCell>
                  {/* Status Cell */}
                  <TableCell className={selectedItem === item.id ? "font-medium" : ""}>
                    <Badge
                      variant={item.is_active ? "default" : "secondary"}
                      className={cn(
                        "text-xs",
                        item.is_active 
                          ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-900/50" 
                          : "bg-gray-100 text-gray-800 dark:bg-gray-800/30 dark:text-gray-400 border border-gray-200 dark:border-gray-800/50"
                      )}
                    >
                      {item.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} className="text-center py-8"> {/* Adjust colSpan */} 
                  <div className="flex justify-center items-center gap-2 h-full">
                    <span className="text-slate-600 dark:text-slate-400">No products found</span>
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
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
              <SelectTrigger className="w-[100px] text-xs">
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
