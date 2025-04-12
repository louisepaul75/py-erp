export interface Product {
  id: number;
  name: string;
  sku: string;
  description: string;
  is_active: boolean;
  is_discontinued: boolean;
  is_new: boolean;
  release_date: string | null;
  created_at: string;
  updated_at: string;
  weight: number | null;
  length_mm: number | null;
  width_mm: number | null;
  height_mm: number | null;
  name_en: string;
  short_description: string;
  short_description_en: string;
  description_en: string;
  keywords: string;
  legacy_id: string;
  legacy_base_sku: string;
  is_hanging: boolean;
  is_one_sided: boolean;
  images: string[]; // Assuming images are an array of strings (URLs or paths)
  primary_image: string | null; // Assuming primary_image is a URL or path
  category: string | null; // Assuming category is a string or null
  tags: string[]; // Assuming tags are an array of strings
  variants_count: number;
  supplier?: Supplier | null; // Add optional supplier field
}

// Add Supplier type based on API response
export interface Supplier {
  id: string; // Changed from number to string (UUID)
  name: string;
}

export interface ApiResponse<T> {
  count: number; // Total number of items available
  page: number; // Current page number
  page_size: number; // Number of items per page
  results: T[]; // Use the generic type T
}

export interface SelectedItem {
  selectedItem: number | string | null;
}

export interface ProductListProps {
    showSidebar: boolean;
    searchTerm: string;
    setSearchTerm: React.Dispatch<React.SetStateAction<string>>;
    filteredProducts: Product[];
    totalItems: number;
    selectedItem: string | null | number;
    setSelectedItem: React.Dispatch<React.SetStateAction<string | number | null>>;
    pagination: {
      pageIndex: number;
      pageSize: number;
    };
    setPagination: React.Dispatch<
      React.SetStateAction<{
        pageIndex: number;
        pageSize: number;
      }>
    >;
    isLoading: boolean;
  }

  export interface ProductDetailProps {
    selectedItem: number | string | null; // number | string | null
    selectedProduct: Product | null; // Product type
    isCreatingParent?: boolean;
    onProductCreated?: (newProduct: Product) => void;
    onCancel?: () => void;
  }

export interface ParentProductSummary {
  id: number;
  sku: string;
  name: string;
}
