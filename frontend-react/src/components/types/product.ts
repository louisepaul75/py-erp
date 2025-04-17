import React from 'react';

export interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string;
  is_active: boolean;
  is_discontinued: boolean;
  category?: string;
  release_date?: string | null;
  tags?: string[];
  keywords?: string;
  primary_image?: { thumbnail_url?: string; image_url: string } | null;
  variants_count: number;
  height_mm?: number | null;
  length_mm?: number | null;
  width_mm?: number | null;
  weight?: number | null;
  is_hanging?: boolean;
  is_one_sided?: boolean;
  is_new?: boolean;
  legacy_base_sku?: string | null;
  supplier?: Supplier | null;
  created_at?: string;
  updated_at?: string;
}

// Add Supplier type based on API response
export interface Supplier {
  id: number;
  name: string;
}

export interface Variant {
  id: number;
  sku: string;
  name: string;
  variant_code?: string | null;
  is_active: boolean;
  images?: ProductImage[];
}

// ProductImage interface
export interface ProductImage {
  id: number;
  image_url: string;
  thumbnail_url?: string | null;
  is_primary?: boolean;
  is_front?: boolean;
  image_type?: string | null;
  alt_text?: string | null;
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
