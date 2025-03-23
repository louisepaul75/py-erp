// app/inventory-management/page.tsx (or wherever your component lives)
"use client";

import { useState, useEffect } from "react";
import MainSidebar from "../inventoryManagement/MainSidebar";
import Header from "../inventoryManagement/Header";
import ProductList from "../inventoryManagement/ProductList";
import ProductDetail from "../inventoryManagement/ProductDetail/ProductDetail";
import { productApi } from "@/lib/products/api";
interface Product {
  nummer: string;
  bezeichnung: string;
  status: string;
}

export default function InventoryManagement() {
  const [selectedItem, setSelectedItem] = useState<string | null>("218300");
  const [showSidebar, setShowSidebar] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [darkMode, setDarkMode] = useState(false);
  console.log("I am in inventory product page");

  const products = [
    { nummer: "307967", bezeichnung: "", status: "active" },
    { nummer: "132355", bezeichnung: "", status: "inactive" },
    { nummer: "-1", bezeichnung: "", status: "draft" },
    {
      nummer: "912859",
      bezeichnung: '"Adler"-Erste Eisenbahn',
      status: "active",
    },
    { nummer: "218300", bezeichnung: '"Adler"-Lock', status: "active" },
    { nummer: "310048", bezeichnung: '"Adler"-Tender', status: "active" },
    { nummer: "411430", bezeichnung: '"Adler"-Wagen', status: "active" },
    { nummer: "409129", bezeichnung: '"Adler"-Wagen-offen', status: "active" },
    { nummer: "300251", bezeichnung: '"Adler"-Wagen/Führer', status: "active" },
    { nummer: "922678", bezeichnung: "100-0", status: "inactive" },
    { nummer: "325473", bezeichnung: "100-0/3", status: "active" },
    { nummer: "530620", bezeichnung: "100-0/5", status: "active" },
    {
      nummer: "921063",
      bezeichnung: "1x Saugnapf für Glasscheibe Vitrine",
      status: "active",
    },
    {
      nummer: "903786",
      bezeichnung: "22 Zoll Display Sichtschutz Bildschirm",
      status: "active",
    },
    {
      nummer: "718205",
      bezeichnung: "27 Zoll Display Sichtschutz Bildschirm",
      status: "active",
    },
    {
      nummer: "701703",
      bezeichnung: "5x BelegDrucker Rollen",
      status: "active",
    },
    {
      nummer: "831738",
      bezeichnung: "7 miniatur Hasen in drei Teile",
      status: "active",
    },
    { nummer: "309069", bezeichnung: "7 Schwaben mit Hase", status: "active" },
    { nummer: "811140", bezeichnung: "80-2", status: "active" },
    { nummer: "304527", bezeichnung: "80-4", status: "active" },
  ];

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        console.log("Fetching products with default parameters...");
        const products = await productApi.getProducts({
          page: 1,
          page_size: 20, // Adjust as needed
        });
        console.log("Fetched products:", products);
      } catch (error) {
        console.error("Error fetching products:", error);
      }
    };
    fetchProducts();
  }, []);

  useEffect(() => {
    setFilteredProducts(
      products.filter(
        (product) =>
          product.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
          product.bezeichnung.toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [searchTerm]);

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
              />
            )}
            <ProductDetail selectedItem={selectedItem} />
          </div>
        </div>
      </div>
    </div>
  );
}
