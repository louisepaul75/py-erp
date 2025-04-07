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
    initialParentId ? parseInt(initialParentId) : null
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

  // Initial fetch and refetch when dependencies change
  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;
    
    const fetchProducts = async () => {
      if (signal.aborted) return;
      
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

        if (signal.aborted) return;

        if (response?.results) {
          setFilteredProducts(response.results);
          setTotalCount(response.count || 0);

          // Simplified initial load/selection logic without shouldKeepSelection
          const isFirstPageLoad = pagination.pageIndex === 0 && !debouncedSearchTerm;
          const initialId = initialVariantId ? parseInt(initialVariantId) : initialParentId ? parseInt(initialParentId) : null;

          if (isFirstPageLoad) { // Only apply special selection logic on the very first load
            if (initialId) {
              const initialProduct = response.results.find(
                (product) => product.id === initialId,
              );
              if (initialProduct) {
                setSelectedItem(initialProduct.id);
                setSelectedProduct(initialProduct);
              } else if (response.results.length > 0) { // Fallback if initial ID not found
                setSelectedItem(response.results[0].id);
                setSelectedProduct(response.results[0]);
              }
            } else if (response.results.length > 0) { // No initial ID, select first item
              setSelectedItem(response.results[0].id);
              setSelectedProduct(response.results[0]);
            }
            // No need for else block to clear selection here, handled below
          }
          
          // Clear selection if the current response has no results (after initial load logic)
          if (response.results.length === 0) {
            setSelectedItem(null);
            setSelectedProduct(null);
          }
        } else { // Handle case where response has no results array
          setFilteredProducts([]);
          setTotalCount(0);
          setSelectedItem(null);
          setSelectedProduct(null);
        }
      } catch (error) {
        // Explicitly check for AbortError name
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
          console.error("Error fetching products:", error);
          setFilteredProducts([]);
          setTotalCount(0);
        }
      } finally {
        if (!signal.aborted) {
          setIsListLoading(false);
        }
      }
    };

    fetchProducts();

    return () => {
      try {
        controller.abort();
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          console.log("Fetch products request aborted as expected.");
        } else {
          console.error("Unexpected error during fetch products abort:", error);
        }
      }
    };
  }, [pagination.pageIndex, pagination.pageSize, debouncedSearchTerm, initialVariantId, initialParentId]);

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

  // Effect for FETCHING product detail data
  useEffect(() => {
    // **Guard**: Don't load details if no item is selected or creating parent
    if (!selectedItem || isCreatingParent) {
      console.log("Skipping detail load (no item or creating parent):", { selectedItem, isCreatingParent });
      setSelectedProduct(null); // Clear product if no item selected
      setIsDetailLoading(false); // Ensure loading is false if we skip
      return;
    }

    const controller = new AbortController();
    const signal = controller.signal;
    let isActive = true;
    const selectedItemId = typeof selectedItem === 'string' ? parseInt(selectedItem) : selectedItem;

    const loadProduct = async () => {
      console.log("Proceeding to load detail for:", selectedItemId);
      try {
        setIsDetailLoading(true); // Ensure loading is true when we start fetching
        const product = await productApi.getProduct(selectedItemId, signal);

        if (!isActive || signal.aborted) return;

        console.log("Successfully loaded product detail:", product.id);
        setSelectedProduct(product); // Only set the product state here

      } catch (error) {
        // Explicitly check for AbortError name in detail fetch as well
        if (!signal.aborted && isActive && !(error instanceof DOMException && error.name === 'AbortError')) {
          console.error(`Error fetching product ${selectedItemId}:`, error);
          setSelectedItem(null); // Reset selection on error
          setSelectedProduct(null);
        } else if (error instanceof DOMException && error.name === 'AbortError') {
           console.log("Fetch detail request aborted as expected (during fetch).");
        }
      } finally {
        if (!signal.aborted && isActive) {
          console.log("Finished detail loading attempt for:", selectedItemId);
          setIsDetailLoading(false);
        }
      }
    };

    loadProduct();

    return () => {
      console.log("Cleaning up detail fetch effect for:", selectedItem);
      isActive = false;
      try {
        controller.abort();
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          console.log("Fetch detail request aborted as expected (in cleanup).");
        } else {
          console.error("Unexpected error during fetch detail abort:", error);
        }
      }
    };
    // Only depend on the item ID and creation status for fetching
  }, [selectedItem, isCreatingParent]);

  // Effect for handling NAVIGATION based on the loaded product and current path
  useEffect(() => {
      // **Guard**: Only run if we have a selected product and are not creating a parent
      if (!selectedProduct || isCreatingParent) {
          return;
      }
      
      const expectedPath = selectedProduct.variants_count > 0
          ? `/products/parent/${selectedProduct.id}`
          : `/products/variant/${selectedProduct.id}`;

      // Only push if the path is actually different
      if (pathname !== expectedPath) {
          console.log(`Pathname mismatch. Current: "${pathname}", Expected: "${expectedPath}". Pushing new path.`);
          router.push(expectedPath);
      }
  // This effect depends on the product, pathname, router and creation status
  }, [selectedProduct, pathname, router, isCreatingParent]);

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
    setPagination(newPagination);
  };

  return (
    <div className="container mx-auto py-4 px-4 md:px-6">
      <div className="max-w-full mx-auto">
        <Card>
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-4">
              <div className="relative w-full md:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  type="search"
                  placeholder="Search by exact SKU or legacy-SKU..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="pl-10 h-9 w-full"
                  title="Searches for exact matches on SKU or legacy-base-SKU fields. For partial matches, use at least 3 characters."
                />
                {searchTerm.length > 0 && (
                  <div className="text-xs text-muted-foreground mt-1">
                    Using direct search for exact matches on SKU and legacy-SKU
                  </div>
                )}
              </div>
            </div>
            <div className="flex flex-col md:flex-row overflow-hidden" style={{ height: contentHeight }}>
              <div className="w-full md:w-1/3 border-b md:border-b-0 md:border-r border mb-4 md:mb-0 flex flex-col">
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
                    isLoading={isListLoading}
                  />
                </div>
                <div className="p-4 border-t border flex-shrink-0">
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
                  <div className="flex items-center justify-center h-full text-muted-foreground">
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
