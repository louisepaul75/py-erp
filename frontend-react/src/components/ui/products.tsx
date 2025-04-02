// app/inventory-management/page.tsx (or wherever your component lives)
"use client";
import React, { useState, useEffect, useCallback } from "react";
import { Search, PlusCircle } from "lucide-react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import ProductList from "../inventoryManagement/ProductList";
import ProductDetail from "../inventoryManagement/ProductDetail/ProductDetail";
import { productApi } from "@/lib/products/api";
import { Product, ApiResponse } from "../types/product";
import { useLastVisited } from "@/context/LastVisitedContext";

// Import from centralized component library
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  Input,
} from "@/components/ui";

interface ProductsPageProps {
  initialVariantId?: string;
  initialParentId?: string;
}

export function ProductsPage({ initialVariantId, initialParentId }: ProductsPageProps) {
  const [selectedItem, setSelectedItem] = useState<number | string | null>(
    initialVariantId ? parseInt(initialVariantId) : 
    initialParentId ? parseInt(initialParentId) : ""
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  
  const [pagination, setPagination] = React.useState<{
    pageIndex: number;
    pageSize: number;
  }>({
    pageIndex: 0,
    pageSize: 20,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [contentHeight, setContentHeight] = useState("calc(100vh - 15rem)");
  const router = useRouter();
  const pathname = usePathname();
  const { addVisitedItem } = useLastVisited();

  // Memoized function to fetch products
  const fetchProducts = useCallback(async () => {
    try {
      console.log(
        `Fetching products... Page: ${pagination.pageIndex + 1}, Size: ${pagination.pageSize}, Search: '${searchTerm}'`,);
      setIsLoading(true);
      const response = (await productApi.getProducts({
        page: pagination.pageIndex + 1,
        page_size: pagination.pageSize,
        search: searchTerm,
      })) as ApiResponse;

      console.log("API Response:", response);

      if (response?.results) {
        setFilteredProducts(response.results);
        setTotalCount(response.count || 0);

        // Determine if initial load/selection logic should apply
        const isInitialLoad = pagination.pageIndex === 0 && !searchTerm && (initialVariantId || initialParentId);

        if (isInitialLoad) {
          const id = initialVariantId || initialParentId;
          const initialProduct = response.results.find(
            (product) => product.id === parseInt(id!),
          );
          if (initialProduct) {
            setSelectedItem(initialProduct.id);
            setSelectedProduct(initialProduct);
          } else if (response.results.length > 0) {
            // Fallback if initial ID not found but results exist
            setSelectedItem(response.results[0].id);
            setSelectedProduct(response.results[0]);
          }
        } else if (response.results.length > 0) {
          // Non-initial load: check if current selection is valid
          const currentSelectionExists = response.results.some(p => p.id === selectedItem);
          if (!currentSelectionExists) {
            // Select first item if current selection is gone
            setSelectedItem(response.results[0].id);
            setSelectedProduct(response.results[0]);
          }
          // If currentSelectionExists, selection remains unchanged by this block
        } else {
          // No results: clear selection
          setSelectedItem(null);
          setSelectedProduct(null);
        }

      } else {
        setFilteredProducts([]);
        setTotalCount(0);
        setSelectedItem(null);
        setSelectedProduct(null);
      }
    } catch (error) {
      console.error("Error fetching products:", error);
      setFilteredProducts([]);
      setTotalCount(0);
      setSelectedItem(null);
      setSelectedProduct(null);
    } finally {
      setIsLoading(false);
    }
  }, [pagination.pageIndex, pagination.pageSize, searchTerm, initialVariantId, initialParentId, selectedItem]); // Added selectedItem dependency

  // Initial fetch and refetch on dependencies change
  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]); // Depend only on the memoized fetch function

  // Effect for updating content height based on window size
  useEffect(() => {
    const updateContentHeight = () => {
      const windowHeight = window.innerHeight;
      setContentHeight(`calc(${windowHeight}px - 15rem)`);
    };
    
    // Set initial height
    updateContentHeight();
    
    // Add event listener for window resize
    window.addEventListener("resize", updateContentHeight);
    
    // Clean up the event listener on component unmount
    return () => window.removeEventListener("resize", updateContentHeight);
  }, []);

  // Update product selection handling AND URL push
  useEffect(() => {
    if (selectedItem) {
      const selected = filteredProducts.find(
        (product) => product.id === selectedItem
      );

      if (selected) {
        setSelectedProduct(selected);
        const newPath = selected.variants_count > 0
          ? `/products/parent/${selected.id}`
          : `/products/variant/${selected.id}`;

        if (pathname !== newPath) {
          // Only push if the path is actually changing
          router.push(newPath);
        }
      }
    }
  }, [selectedItem, filteredProducts, pathname, router]);

  // Add useEffect for tracking visits
  useEffect(() => {
    if (selectedProduct && selectedProduct.id && selectedProduct.name) {
      const path = selectedProduct.variants_count > 0
        ? `/products/parent/${selectedProduct.id}`
        : `/products/variant/${selectedProduct.id}`;

      addVisitedItem({
        type: 'product', // Or determine parent/variant specifically if needed
        id: String(selectedProduct.id),
        name: selectedProduct.name,
        path: path,
      });
    }
  }, [selectedProduct, addVisitedItem]);

  // Handler for creating new parent product
  const handleCreateNewParent = () => {
    router.push('/products/parent/create');
  };

  return (
    <div className="container mx-auto py-4 px-4 md:px-6">
      <div className="max-w-full mx-auto">
        <Card>
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-4">
              <div className="relative w-full md:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 h-4 w-4" />
                <Input
                  type="search"
                  placeholder="Suche nach Produkt..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 h-9 w-full"
                />
              </div>
            </div>
            <div className="flex flex-col md:flex-row overflow-hidden" style={{ height: contentHeight }}>
              <div className="w-full md:w-1/3 border-b md:border-b-0 md:border-r dark:border-slate-800 mb-4 md:mb-0 flex flex-col">
                <div className="flex-grow overflow-y-auto">
                  <ProductList
                    showSidebar={true}
                    searchTerm={searchTerm}
                    setSearchTerm={setSearchTerm}
                    filteredProducts={filteredProducts}
                    totalItems={totalCount}
                    selectedItem={selectedItem}
                    setSelectedItem={setSelectedItem}
                    pagination={pagination}
                    setPagination={setPagination}
                    isLoading={isLoading}
                  />
                </div>
                <div className="p-4 border-t dark:border-slate-800 flex-shrink-0">
                  <Button
                    onClick={handleCreateNewParent}
                    className="w-full"
                  >
                    <PlusCircle className="mr-2 h-4 w-4" />
                    New Parent Product
                  </Button>
                </div>
              </div>
              <div className="w-full md:w-2/3 h-1/2 md:h-full overflow-auto pl-4">
                {selectedProduct ? (
                  <ProductDetail
                    selectedItem={selectedItem}
                    selectedProduct={selectedProduct}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-500">
                    Select a product to view details or create a new one.
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Default export for the page
export default function ProductsPageContainer({ initialVariantId, initialParentId }: ProductsPageProps = {}) {
  return <ProductsPage initialVariantId={initialVariantId} initialParentId={initialParentId} />;
}
