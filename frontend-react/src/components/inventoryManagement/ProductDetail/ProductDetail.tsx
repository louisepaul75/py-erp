// components/ProductDetail/ProductDetail.tsx
import { useState } from "react";
import TabsNavigation from "./TabsNavigation";
import MutterTab from "./MutterTab";
import VariantenTab from "./VariantenTab";

interface ProductDetailProps {
  selectedItem: string | null;
}

export default function ProductDetail({ selectedItem }: ProductDetailProps) {
  const [activeTab, setActiveTab] = useState("mutter");

  return (
    <div className="flex-1 overflow-auto z-20 bg-slate-50 dark:bg-slate-950 ">
      {/* Mutter/Varianten Tabs */}
      <TabsNavigation activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Tab Content */}
      {activeTab === "mutter" ? (
        <MutterTab selectedItem={selectedItem} />
      ) : (
        <VariantenTab selectedItem={selectedItem} />
      )}
    </div>
  );
}