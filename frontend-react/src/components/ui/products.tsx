// app/inventory-management/page.tsx (or wherever your component lives)
"use client";
import React from "react";
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import ProductList from "../inventoryManagement/ProductList";
import ProductDetail from "../inventoryManagement/ProductDetail/ProductDetail";
import { productApi } from "@/lib/products/api";
import { Product, ApiResponse } from "../types/product";

export default function InventoryManagement() {
  const [selectedItem, setSelectedItem] = useState<number | string | null>("");
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [darkMode, setDarkMode] = useState(false);
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
  // In products.tsx
  const [pagination, setPagination] = React.useState<{
    pageIndex: number;
    pageSize: number;
  }>({
    pageIndex: 0,
    pageSize: 20,
  });
  const [isLoading, setIsLoading] = useState(false);

  // Update your fetchProducts useEffect
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        console.log("Fetching products...");
        setIsLoading(true);
        const response = (await productApi.getProducts({
          page: pagination.pageIndex + 1, // Backend uses 1-based index
          page_size: pagination.pageSize,
        })) as ApiResponse;

        setProducts(response.results);
        setFilteredProducts(response.results);
        setSelectedItem(response.results[0]?.id || null);
        if (response.results.length > 0 && !selectedProduct.id) {
          setSelectedProduct(response.results[0]);
        }
        console.log("Fetched products:", response);
      } catch (error) {
        console.error("Error fetching products:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProducts();
  }, [pagination.pageIndex, pagination.pageSize]);

  useEffect(() => {
    console.log("Filtering products by search term");
    setFilteredProducts(
      products.filter(
        (product) =>
          product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
          product.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [searchTerm, products]);

  useEffect(() => {
    // Find the product in filteredProducts that matches the selectedItem
    const selected = filteredProducts.find(
      (product) => product.id === selectedItem
    );
  
    // Update the selectedProduct state
    if (selected) {
      setSelectedProduct(selected);
    }
  }, [selectedItem, filteredProducts]);

  useEffect(() => {
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      setDarkMode(true);
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  return (
    <div className={`min-h-screen ${darkMode ? "dark" : ""}`}>
      <div className="flex flex-col h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden">
        {/* Simple header with search */}
        <div className="py-4 px-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Produkte</h1>
          <div className="flex items-center gap-4">
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
            <Button
              variant="outline"
              size="icon"
              onClick={toggleDarkMode}
              className="ml-2"
            >
              {darkMode ? "☀️" : "🌙"}
            </Button>
          </div>
        </div>
        
        <div className="flex-1 flex overflow-hidden w-full">
          <div className="w-1/3 border-r border-slate-200 dark:border-slate-800">
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
      </div>
    </div>
  );
}
