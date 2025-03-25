// components/ProductDetail/ProductDetail.tsx
import { useState } from "react";
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

  console.log("selectedProduct",selectedProduct)

  return (
    <div className="flex-1 overflow-auto z-20 bg-slate-50 dark:bg-slate-950 ">
      {/* Mutter/Varianten Tabs */}
      <TabsNavigation activeTab={activeTab} setActiveTab={setActiveTab} />

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
