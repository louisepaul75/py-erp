// app/inventory-management/page.tsx (or wherever your component lives)
"use client";
import React from "react";
import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import ProductList from "../inventoryManagement/ProductList";
import ProductDetail from "../inventoryManagement/ProductDetail/ProductDetail";
import { productApi } from "@/lib/products/api";
import { Product, ApiResponse } from "../types/product";

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

interface InventoryManagementProps {
  initialVariantId?: string;
  initialParentId?: string;
}

export function InventoryManagement({ initialVariantId, initialParentId }: InventoryManagementProps) {
  const [selectedItem, setSelectedItem] = useState<number | string | null>(
    initialVariantId ? parseInt(initialVariantId) : 
    initialParentId ? parseInt(initialParentId) : ""
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product>({
    id: 0,
    name: "",
    sku: "",
    description: "",
    is_active: false,
    is_discontinued: false,
    is_new: false,
    release_date: null,
    created_at: "",
    updated_at: "",
    weight: null,
    length_mm: null,
    width_mm: null,
    height_mm: null,
    name_en: "",
    short_description: "",
    short_description_en: "",
    description_en: "",
    keywords: "",
    legacy_id: "",
    legacy_base_sku: "",
    is_hanging: false,
    is_one_sided: false,
    images: [],
    primary_image: null,
    category: null,
    tags: [],
    variants_count: 0,
  });
  
  const [pagination, setPagination] = React.useState<{
    pageIndex: number;
    pageSize: number;
  }>({
    pageIndex: 0,
    pageSize: 20,
  });
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // Update fetchProducts useEffect to handle both IDs
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        console.log("Fetching products...");
        setIsLoading(true);
        const response = (await productApi.getProducts({
          page: pagination.pageIndex + 1,
          page_size: pagination.pageSize,
        })) as ApiResponse;

        // Log raw API response
        console.log("Raw API Response:", response);

        setProducts(response.results);
        setFilteredProducts(response.results);
        
        // Handle initial product selection
        if (initialVariantId || initialParentId) {
          const id = initialVariantId || initialParentId;
          const initialProduct = response.results.find(
            (product) => product.id === parseInt(id!)
          );
          if (initialProduct) {
            setSelectedItem(initialProduct.id);
            setSelectedProduct(initialProduct);
          }
        } else {
          // Default behavior
          if (response.results && response.results.length > 0) {
            setSelectedItem(response.results[0]?.id || null);
            if (!selectedProduct?.id) {
              setSelectedProduct(response.results[0]);
            }
          } else {
            setSelectedItem(null);
          }
        }
        
        console.log("Fetched products:", response);
      } catch (error) {
        console.error("Error fetching products:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProducts();
  }, [pagination.pageIndex, pagination.pageSize, initialVariantId, initialParentId]);

  useEffect(() => {
    // Log products state before filtering
    console.log("Products state before filtering:", products);
    console.log("Filtering products by search term");
    // Ensure products is an array before filtering
    if (Array.isArray(products)) {
      setFilteredProducts(
        products.filter(
          (product) =>
            product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
            product.name.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    } else {
      // If products isn't an array (e.g., initially undefined), set filteredProducts to empty
      setFilteredProducts([]); 
    }
  }, [searchTerm, products]);

  // Update product selection handling
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
          router.push(newPath);
        }
      }
    }
  }, [selectedItem, filteredProducts, pathname, router]);

  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      <div className="max-w-full mx-auto">
        <Card>
          <CardHeader >
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-bold text-primary">Produkte</CardTitle>
                <CardDescription>Verwalten Sie Ihre Produkte und Varianten</CardDescription>
              </div>
              <div className="relative w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <Input
                  type="search"
                  placeholder="Suche nach Produkt..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0 ">
            <div className="flex overflow-hidden h-[calc(100vh-15rem)]">
              <div className="w-1/3 border-r  dark:border-slate-800">
                <ProductList
                  showSidebar={true}
                  searchTerm={searchTerm}
                  setSearchTerm={setSearchTerm}
                  filteredProducts={filteredProducts}
                  selectedItem={selectedItem}
                  setSelectedItem={setSelectedItem}
                  pagination={pagination}
                  setPagination={setPagination}
                  isLoading={isLoading}
                />
              </div>
              <div className="w-2/3">
                <ProductDetail
                  selectedItem={selectedItem}
                  selectedProduct={selectedProduct}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Default export for the page
export default function InventoryManagementPage() {
  return <InventoryManagement />;
}
