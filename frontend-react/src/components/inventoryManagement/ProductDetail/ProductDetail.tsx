// components/ProductDetail/ProductDetail.tsx
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import TabsNavigation from "./TabsNavigation";
import MutterTab from "./MutterTab";
import VariantenTab from "./VariantenTab";
import { SelectedItem } from "@/components/types/product";
import { ProductDetailProps } from "@/components/types/product";
import { productApi } from "@/lib/products/api";
import { Product } from "@/components/types/product";

export default function ProductDetail({
  selectedItem,
  selectedProduct,
  isCreatingParent = false,
  onProductCreated,
  onCancel,
}: ProductDetailProps) {
  const [activeTab, setActiveTab] = useState("mutter");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  console.log("ProductDetail rendering with selectedProduct:", selectedProduct, "isCreatingParent:", isCreatingParent);
  
  // Create an empty product object for new parent product creation
  const emptyProduct: Product = {
    id: 0,
    name: "",
    sku: "",
    description: "",
    is_active: true,
    is_discontinued: false,
    is_new: false,
    release_date: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
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
    variants_count: 0
  };
  
  // If creating a parent product, use the empty product template
  const displayProduct = isCreatingParent ? emptyProduct : selectedProduct;
  
  const handleAddNewVariant = () => {
    if (selectedProduct && selectedProduct.id) {
      console.log("handleAddNewVariant clicked for product:", selectedProduct.id);
      router.push(`/products/variant/create?parent=${selectedProduct.id}`);
    }
  };

  // Handle creating a new parent product
  const handleCreateProduct = async (productData: Omit<Product, "id">) => {
    if (onProductCreated) {
      setIsLoading(true);
      setError(null);
      
      try {
        const newProduct = await productApi.createProduct(productData);
        onProductCreated(newProduct);
      } catch (err: any) {
        console.error("Error creating product:", err);
        setError(`Failed to create product: ${err.message || "Unknown error"}`);
        setIsLoading(false);
      }
    }
  };

  // Handle cancel creating a new parent product
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/products');
    }
  };

  // Use effect to log when component mounts or selectedProduct changes
  useEffect(() => {
    console.log("ProductDetail selectedProduct updated:", selectedProduct);
  }, [selectedProduct]);

  return (
    <div className="h-full flex-1 overflow-auto z-20 bg-slate-50 dark:bg-slate-950">
      {/* Mutter/Varianten Tabs */}
      <TabsNavigation 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onAddVariant={!isCreatingParent && selectedProduct ? handleAddNewVariant : undefined}
        isCreatingParent={isCreatingParent}
      />

      {/* Tab Content */}
      {activeTab === "mutter" ? (
        <MutterTab
          selectedItem={selectedItem}
          selectedProduct={displayProduct}
          isCreatingParent={isCreatingParent}
          onSave={isCreatingParent ? handleCreateProduct : undefined}
          onCancel={isCreatingParent ? handleCancel : undefined}
        />
      ) : (
        <VariantenTab selectedItem={selectedItem} />
      )}
    </div>
  );
}
