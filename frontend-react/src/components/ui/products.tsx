// app/inventory-management/page.tsx (or wherever your component lives)
"use client";
import React from "react";
import { useState, useEffect } from "react";
import MainSidebar from "../inventoryManagement/MainSidebar";
import Header from "../inventoryManagement/Header";
import ProductList from "../inventoryManagement/ProductList";
import ProductDetail from "../inventoryManagement/ProductDetail/ProductDetail";
import { productApi } from "@/lib/products/api";
import { Product, ApiResponse, SelectedItem } from "../types/product";

export default function InventoryManagement() {
  const [selectedItem, setSelectedItem] = useState<number | string | null>("");
  const [showSidebar, setShowSidebar] = useState(true);
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

  // const products = [
  //   { nummer: "307967", bezeichnung: "", status: "active" },
  //   { nummer: "132355", bezeichnung: "", status: "inactive" },
  //   { nummer: "-1", bezeichnung: "", status: "draft" },
  //   {
  //     nummer: "912859",
  //     bezeichnung: '"Adler"-Erste Eisenbahn',
  //     status: "active",
  //   },
  //   { nummer: "218300", bezeichnung: '"Adler"-Lock', status: "active" },
  //   { nummer: "310048", bezeichnung: '"Adler"-Tender', status: "active" },
  //   { nummer: "411430", bezeichnung: '"Adler"-Wagen', status: "active" },
  //   { nummer: "409129", bezeichnung: '"Adler"-Wagen-offen', status: "active" },
  //   { nummer: "300251", bezeichnung: '"Adler"-Wagen/Führer', status: "active" },
  //   { nummer: "922678", bezeichnung: "100-0", status: "inactive" },
  //   { nummer: "325473", bezeichnung: "100-0/3", status: "active" },
  //   { nummer: "530620", bezeichnung: "100-0/5", status: "active" },
  //   {
  //     nummer: "921063",
  //     bezeichnung: "1x Saugnapf für Glasscheibe Vitrine",
  //     status: "active",
  //   },
  //   {
  //     nummer: "903786",
  //     bezeichnung: "22 Zoll Display Sichtschutz Bildschirm",
  //     status: "active",
  //   },
  //   {
  //     nummer: "718205",
  //     bezeichnung: "27 Zoll Display Sichtschutz Bildschirm",
  //     status: "active",
  //   },
  //   {
  //     nummer: "701703",
  //     bezeichnung: "5x BelegDrucker Rollen",
  //     status: "active",
  //   },
  //   {
  //     nummer: "831738",
  //     bezeichnung: "7 miniatur Hasen in drei Teile",
  //     status: "active",
  //   },
  //   { nummer: "309069", bezeichnung: "7 Schwaben mit Hase", status: "active" },
  //   { nummer: "811140", bezeichnung: "80-2", status: "active" },
  //   { nummer: "304527", bezeichnung: "80-4", status: "active" },
  // ];

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
        setSelectedItem(response.results[0].id);
        if (!selectedProduct) {
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


  console.log("zmbye");

  useEffect(() => {
    console.log("how many times");
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
    <div className={`min-h-screen  ${darkMode ? "dark" : ""}`}>
      <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden">
        <MainSidebar showSidebar={showSidebar} />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header
            showSidebar={showSidebar}
            setShowSidebar={setShowSidebar}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            darkMode={darkMode}
            toggleDarkMode={toggleDarkMode}
          />
          <div className="flex-1 flex overflow-hidden w-full">
            {showSidebar && (
              <ProductList
                showSidebar={showSidebar}
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                filteredProducts={filteredProducts}
                selectedItem={selectedItem}
                setSelectedItem={setSelectedItem}
                pagination={pagination}
                setPagination={setPagination}
                isLoading={isLoading}
              />
            )}
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
