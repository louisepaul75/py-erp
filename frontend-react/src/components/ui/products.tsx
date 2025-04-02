"use client";

// Add this at the top of the file after imports
declare global {
  interface Window {
    debouncedSelectionTimeout?: ReturnType<typeof setTimeout>;
  }
}

// app/inventory-management/page.tsx (or wherever your component lives)
import React, { useState, useEffect, useCallback, useRef } from "react";
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
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isCreatingParent, setIsCreatingParent] = useState(false);
  
  const [pagination, setPagination] = useState<{
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
  const [shouldKeepSelection, setShouldKeepSelection] = useState(true);
  
  // Debounced item selection to prevent multiple rapid changes
  const debouncedSetSelectedItem = useCallback((item: number | string | null) => {
    // Skip if the item is the same
    if (item === selectedItem) return;
    
    // Clear any pending timeouts
    if (window.debouncedSelectionTimeout) {
      clearTimeout(window.debouncedSelectionTimeout);
    }
    
    // Set with a slight delay to prevent rapid changes
    window.debouncedSelectionTimeout = setTimeout(() => {
      setSelectedItem(item);
    }, 100);
  }, [selectedItem]);
  
  // Debounce search term to prevent too many API requests
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300); // 300ms delay
    
    return () => clearTimeout(timer);
  }, [searchTerm]);
  
  // Reset to first page when search term changes
  useEffect(() => {
    // Only reset pagination if we're not on the first page already
    if (pagination.pageIndex !== 0) {
      setPagination(prev => ({
        ...prev,
        pageIndex: 0
      }));
    }
  }, [debouncedSearchTerm]);

  // Memoized function to fetch products
  const fetchProducts = useCallback(async () => {
    // Create an abort controller for this request
    const abortController = new AbortController();
    
    try {
      setIsLoading(true);
      
      // Use direct search endpoint when a search term is provided
      let response;
      if (debouncedSearchTerm) {
        response = await productApi.getProductsDirectSearch({
          page: pagination.pageIndex + 1,
          page_size: pagination.pageSize,
          q: debouncedSearchTerm,
        }, abortController.signal) as ApiResponse;
      } else {
        // Use regular endpoint when no search term is provided
        response = await productApi.getProducts({
          page: pagination.pageIndex + 1,
          page_size: pagination.pageSize,
        }, abortController.signal) as ApiResponse;
      }

      if (response?.results) {
        setFilteredProducts(response.results);
        setTotalCount(response.count || 0);

        // Determine if initial load/selection logic should apply
        const isInitialLoad = 
          (pagination.pageIndex === 0 && !debouncedSearchTerm && (initialVariantId || initialParentId)) || 
          shouldKeepSelection;

        if (isInitialLoad) {
          const id = initialVariantId || initialParentId;
          if (id) {
            const initialProduct = response.results.find(
              (product) => product.id === parseInt(id),
            );
            if (initialProduct) {
              setSelectedItem(initialProduct.id);
              setSelectedProduct(initialProduct);
            } else if (response.results.length > 0 && !shouldKeepSelection) {
              // Fallback if initial ID not found but results exist (only on first load)
              setSelectedItem(response.results[0].id);
              setSelectedProduct(response.results[0]);
            }
          } else if (response.results.length > 0 && !shouldKeepSelection) {
            // No initial ID provided, select first item (only on first load)
            setSelectedItem(response.results[0].id);
            setSelectedProduct(response.results[0]);
          }
          
          // After initial load, reset shouldKeepSelection
          if (shouldKeepSelection) {
            setShouldKeepSelection(false);
          }
        } else if (response.results.length === 0) {
          // Only clear selection if no results are found
          setSelectedItem(null);
          setSelectedProduct(null);
        }
        // Don't reset selection otherwise - this prevents flashing back to default

      } else {
        setFilteredProducts([]);
        setTotalCount(0);
        setSelectedItem(null);
        setSelectedProduct(null);
      }
    } catch (error) {
      // Only handle error if it's not an abort error
      if (!(error instanceof DOMException && error.name === 'AbortError')) {
        console.error("Error fetching products:", error);
        setFilteredProducts([]);
        setTotalCount(0);
        // Don't reset selection on error unless absolutely necessary
      }
    } finally {
      setIsLoading(false);
    }
    
    // Return a cleanup function that aborts the request if component unmounts or dependencies change
    return () => {
      abortController.abort();
    };
  }, [pagination.pageIndex, pagination.pageSize, debouncedSearchTerm, initialVariantId, initialParentId, shouldKeepSelection]);

  // Initial fetch and refetch when dependencies change
  useEffect(() => {
    // Create an abort controller for this effect's fetch
    const controller = new AbortController();
    
    // Immediately invoke fetchProducts
    fetchProducts();
    
    // Return cleanup function directly
    return () => {
      controller.abort();
    };
  }, [fetchProducts, debouncedSearchTerm]);

  // Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

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
    // Skip if no selected item or if we're creating a parent
    if (!selectedItem || isCreatingParent) return;
    
    // Use a ref to track the latest request
    const abortController = new AbortController();
    
    // First, try to find the product in the current list
    const selected = filteredProducts.find(
      (product) => product.id === selectedItem
    );

    if (selected) {
      // Set product directly from filtered list - this is immediate
      setSelectedProduct(selected);
      const newPath = selected.variants_count > 0
        ? `/products/parent/${selected.id}`
        : `/products/variant/${selected.id}`;

      if (pathname !== newPath) {
        // Only push if the path is actually changing
        router.push(newPath);
      }
    } else {
      // If not found in the filteredProducts list, fetch directly
      // But first check if we're already loading or if we already have this product
      // to prevent unnecessary flashing
      if (!isLoading && (!selectedProduct || selectedProduct.id !== selectedItem)) {
        // Use a timeout to stagger requests and prevent too many simultaneous requests
        // This helps reduce the network waterfall and prevents flashing
        const timeoutId = setTimeout(async () => {
          try {
            setIsLoading(true);
            // Use the abort controller for this request
            const product = await productApi.getProduct(selectedItem, abortController.signal);
            
            // Don't update if the selection changed while we were fetching
            if (selectedItem === product.id) {
              setSelectedProduct(product);
              
              const newPath = product.variants_count > 0
                ? `/products/parent/${product.id}`
                : `/products/variant/${product.id}`;
  
              if (pathname !== newPath) {
                // Only push if the path is actually changing
                router.push(newPath);
              }
            }
          } catch (error) {
            // Only log and reset if it's not an abort error
            if (!(error instanceof DOMException && error.name === 'AbortError')) {
              console.error(`Error fetching product ${selectedItem}:`, error);
              // If the product cannot be fetched, reset selection
              setSelectedItem(null);
              setSelectedProduct(null);
            }
          } finally {
            setIsLoading(false);
          }
        }, 50); // Small delay to prevent UI flashing

        // Clear the timeout if component unmounts or dependencies change
        return () => {
          clearTimeout(timeoutId);
          abortController.abort();
        };
      }
    }
    
    // Clean up function to abort any in-flight requests when the component unmounts
    // or when selectedItem changes
    return () => {
      abortController.abort();
    };
  }, [selectedItem, filteredProducts, pathname, router, isCreatingParent, isLoading, selectedProduct]);

  // Add useEffect for tracking visits
  useEffect(() => {
    if (selectedProduct && selectedProduct.id && selectedProduct.name && !isCreatingParent) {
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
  }, [selectedProduct, addVisitedItem, isCreatingParent]);

  // Handler for creating new parent product
  const handleCreateNewParent = () => {
    // Instead of navigating, set the state to indicate we're creating a new parent
    setIsCreatingParent(true);
    setSelectedItem(null);
    setSelectedProduct(null);
  };

  // Handler for when a new parent product is created
  const handleParentProductCreated = (newProduct: Product) => {
    setIsCreatingParent(false);
    setSelectedItem(newProduct.id);
    setSelectedProduct(newProduct);
    // Refresh the products list
    fetchProducts();
  };

  // Handler to cancel creating a new parent product
  const handleCancelCreate = () => {
    setIsCreatingParent(false);
    // If there are products in the list, select the first one
    if (filteredProducts.length > 0) {
      setSelectedItem(filteredProducts[0].id);
      setSelectedProduct(filteredProducts[0]);
    }
  };

  // Custom function to handle pagination changes
  const handlePaginationChange = (newPagination: { pageIndex: number, pageSize: number }) => {
    // We want to keep the current selection when changing pages
    setShouldKeepSelection(true);
    setPagination(newPagination);
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
                  placeholder="Search by exact SKU or legacy-SKU..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="pl-10 h-9 w-full"
                  title="Searches for exact matches on SKU or legacy-base-SKU fields. For partial matches, use at least 3 characters."
                />
                {searchTerm.length > 0 && (
                  <div className="text-xs text-slate-500 mt-1">
                    Using direct search for exact matches on SKU and legacy-SKU
                  </div>
                )}
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
                    setSelectedItem={(item) => {
                      setIsCreatingParent(false);
                      debouncedSetSelectedItem(item);
                    }}
                    pagination={pagination}
                    setPagination={handlePaginationChange}
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
                {isCreatingParent ? (
                  <ProductDetail
                    selectedItem={null}
                    selectedProduct={null}
                    isCreatingParent={true}
                    onProductCreated={handleParentProductCreated}
                    onCancel={handleCancelCreate}
                  />
                ) : selectedProduct ? (
                  <ProductDetail
                    selectedItem={selectedItem}
                    selectedProduct={selectedProduct}
                    isCreatingParent={false}
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
