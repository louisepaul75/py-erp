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

// Add proper interface for the ProductList component
interface ProductListProps {
  showSidebar: boolean;
  searchTerm: string;
  setSearchTerm: (value: string) => void;
  filteredProducts: Product[];
  totalItems: number;
  selectedItem: number | string | null;
  setSelectedItem: (item: number | string | null) => void;
  pagination: { pageIndex: number; pageSize: number };
  setPagination: (pagination: { pageIndex: number; pageSize: number }) => void;
  isLoading: boolean;
}

// Add proper interface for the ProductDetail component
interface ProductDetailProps {
  selectedItem: number | string | null;
  selectedProduct: Product | null;
  isCreatingParent?: boolean;
  onProductCreated?: (product: Product) => void;
  onCancel?: () => void;
}

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
  
  // Separate loading states for list and detail
  const [isListLoading, setIsListLoading] = useState(false);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  
  const [pagination, setPagination] = useState<{
    pageIndex: number;
    pageSize: number;
  }>({
    pageIndex: 0,
    pageSize: 20,
  });
  
  const [contentHeight, setContentHeight] = useState("calc(100vh - 15rem)");
  const router = useRouter();
  const pathname = usePathname();
  const { addVisitedItem } = useLastVisited();
  const [shouldKeepSelection, setShouldKeepSelection] = useState(true);
  
  // Debounced item selection to prevent multiple rapid changes
  const debouncedSetSelectedItem = useCallback((item: number | string | null) => {
    console.log("debouncedSetSelectedItem called with:", item);
    
    // Skip if the item is the same as current selection
    if (item === selectedItem) {
      console.log("Skipping selection - same as current item");
      return;
    }
    
    // Clear any pending timeouts
    if (window.debouncedSelectionTimeout) {
      clearTimeout(window.debouncedSelectionTimeout);
    }
    
    // Set with a slight delay to prevent rapid changes
    window.debouncedSelectionTimeout = setTimeout(() => {
      console.log("Setting selectedItem to:", item);
      setSelectedItem(item);
    }, 150); // Increase delay to ensure any in-progress requests complete
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

  // Memoize the fetch function to prevent recreation on every render
  const fetchProductsList = useCallback(async (signal: AbortSignal) => {
    try {
      setIsListLoading(true);
      
      // Use direct search endpoint when a search term is provided
      let response;
      if (debouncedSearchTerm) {
        response = await productApi.getProductsDirectSearch({
          page: pagination.pageIndex + 1,
          page_size: pagination.pageSize,
          q: debouncedSearchTerm,
        }, signal) as ApiResponse;
      } else {
        // Use regular endpoint when no search term is provided
        response = await productApi.getProducts({
          page: pagination.pageIndex + 1,
          page_size: pagination.pageSize,
        }, signal) as ApiResponse;
      }

      if (!signal.aborted) {
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
        } else {
          setFilteredProducts([]);
          setTotalCount(0);
          setSelectedItem(null);
          setSelectedProduct(null);
        }
      }
    } catch (error) {
      // Only handle error if it's not an abort error
      if (error instanceof DOMException && error.name === 'AbortError') {
        // Silently handle abort errors
        return;
      }
      console.error("Error fetching products:", error);
      setFilteredProducts([]);
      setTotalCount(0);
    } finally {
      if (!signal.aborted) {
        setIsListLoading(false);
      }
    }
  }, [pagination.pageIndex, pagination.pageSize, debouncedSearchTerm, initialVariantId, initialParentId, shouldKeepSelection]);

  // Initial fetch and refetch when dependencies change
  useEffect(() => {
    // Create a new controller specifically for this effect's execution
    const controller = new AbortController();
    
    // Fetch products immediately
    fetchProductsList(controller.signal);
    
    // Return a cleanup function that aborts the request
    return () => {
      controller.abort();
    };
  }, [fetchProductsList]);

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
    console.log("Product selection effect running, selectedItem:", selectedItem);
    
    // Use a ref to track the latest request to prevent race conditions
    let isCurrent = true;
    
    // Skip if no selected item or if we're creating a parent
    if (!selectedItem || isCreatingParent) {
      console.log("Skipping product selection - no selected item or creating parent");
      return;
    }
    
    // First, try to find the product in the current list
    // Compare as numbers to avoid string/number mismatches
    const selectedItemId = typeof selectedItem === 'string' ? parseInt(selectedItem) : selectedItem;
    
    console.log("Looking for product with ID:", selectedItemId, "in", filteredProducts.length, "products");
    
    const selected = filteredProducts.find(product => {
      const productId = typeof product.id === 'string' ? parseInt(product.id) : product.id;
      return productId === selectedItemId;
    });
    
    console.log("Found product in list?", selected ? "Yes" : "No");

    const loadProductDetail = async () => {
      // Skip if we're already loading the detail
      if (isDetailLoading) {
        console.log("Already loading detail, skipping");
        return;
      }
      
      console.log("Loading product detail for ID:", selectedItemId);
      setIsDetailLoading(true);
      
      try {
        // Create a new controller for this specific request
        const controller = new AbortController();
        
        // Always fetch fresh product data from the API to ensure consistency
        try {
          console.log("Fetching product details from API for ID:", selectedItemId);
          const product = await productApi.getProduct(selectedItemId, controller.signal);
          
          // Check if this is still the current request before updating state
          if (isCurrent && !controller.signal.aborted) {
            console.log("Received product from API:", product.id, product.name);
            setSelectedProduct(product);
            
            const newPath = product.variants_count > 0
              ? `/products/parent/${product.id}`
              : `/products/variant/${product.id}`;
  
            if (pathname !== newPath) {
              console.log("Navigating to:", newPath);
              router.push(newPath);
            }
          }
        } catch (error) {
          if (!(error instanceof DOMException && error.name === 'AbortError') && isCurrent) {
            console.error(`Error fetching product ${selectedItemId}:`, error);
            setSelectedItem(null);
            setSelectedProduct(null);
          }
        }
      } finally {
        // Only update loading state if this is still the current request
        if (isCurrent) {
          console.log("Finished loading product detail");
          setIsDetailLoading(false);
        }
      }
    };

    // Execute loadProductDetail immediately
    loadProductDetail();
    
    // Clean up function
    return () => {
      // Mark this request as no longer current
      console.log("Cleaning up product selection effect");
      isCurrent = false;
    };
  }, [selectedItem, filteredProducts, pathname, router, isCreatingParent, isDetailLoading]);

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
    
    // Create a new controller and fetch the updated product list
    const controller = new AbortController();
    fetchProductsList(controller.signal);
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
                    setSelectedItem={(item: number | string | null) => {
                      setIsCreatingParent(false);
                      debouncedSetSelectedItem(item);
                    }}
                    pagination={pagination}
                    setPagination={(value: { pageIndex: number; pageSize: number }) => {
                      handlePaginationChange(value);
                    }}
                    isLoading={isListLoading}
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
                    {isDetailLoading ? (
                      "Loading product details..."
                    ) : (
                      "Select a product to view details or create a new one."
                    )}
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
