// components/ProductDetail/ProductDetail.tsx
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import TabsNavigation from "./TabsNavigation";
import MutterTab from "./MutterTab";
import VariantenTab from "./VariantenTab";
import { SelectedItem } from "@/components/types/product";
import { ProductDetailProps } from "@/components/types/product";

export default function ProductDetail({
  selectedItem,
  selectedProduct,
}: ProductDetailProps) {
  const [activeTab, setActiveTab] = useState("mutter");
  const router = useRouter();

  console.log("ProductDetail rendering with selectedProduct:", selectedProduct);
  
  const handleAddNewVariant = () => {
    if (selectedProduct && selectedProduct.id) {
      console.log("handleAddNewVariant clicked for product:", selectedProduct.id);
      router.push(`/products/variant/create?parent=${selectedProduct.id}`);
    }
  };

  // Use effect to log when component mounts or selectedProduct changes
  useEffect(() => {
    console.log("ProductDetail selectedProduct updated:", selectedProduct);
  }, [selectedProduct]);

  return (
    <div className="h-full flex-1 overflow-auto z-20 bg-slate-50 dark:bg-slate-950 ">
      {/* Mutter/Varianten Tabs */}
      <TabsNavigation 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onAddVariant={selectedProduct ? handleAddNewVariant : undefined}
      />

      {/* Tab Content */}
      {activeTab === "mutter" ? (
        <MutterTab
          selectedItem={selectedItem}
          selectedProduct={selectedProduct}
        />
      ) : (
        <VariantenTab selectedItem={selectedItem} />
      )}
    </div>
  );
}
