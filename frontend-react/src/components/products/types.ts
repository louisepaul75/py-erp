// components/products/types.ts
import { Product, Supplier } from '@/components/types/product';

export type ProductFormData = Partial<Product> & {
  name: string;
  sku: string;
  height_mm?: number | null;
  length_mm?: number | null;
  width_mm?: number | null;
  weight?: number | null;
  is_hanging?: boolean;
  is_one_sided?: boolean;
  is_new?: boolean;
  legacy_base_sku?: string | null;
};

export const defaultProductData: ProductFormData = {
  name: '',
  sku: '',
  description: '',
  is_active: true,
  is_discontinued: false,
  category: '',
  release_date: null,
  tags: [],
  keywords: '',
  primary_image: null,
  variants_count: 0,
  height_mm: null,
  length_mm: null,
  width_mm: null,
  weight: null,
  is_hanging: false,
  is_one_sided: false,
  is_new: false,
  legacy_base_sku: undefined,
};