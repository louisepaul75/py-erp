// lib/api.ts
import ky, {
  HTTPError,
  type Options as KyOptions,
  type NormalizedOptions,
} from "ky";
import { API_URL, AUTH_CONFIG } from "../config";
import { Product, ApiResponse } from "@/components/types/product";
import { getServerCookie } from "../auth/serverCookies";

// Cookie storage utility for client-side operations
const cookieStorage = {
  getItem: (name: string): string | null => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()?.split(';').shift() ?? null;
    return null;
  },
  setItem: (name: string, value: string, options = {}) => {
    document.cookie = `${name}=${value}; path=/; ${Object.entries(options)
      .map(([k, v]) => `${k}=${v}`)
      .join("; ")}`;
  },
  removeItem: (name: string) => {
    document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  },
};

// Token refresh handling
const isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: void | PromiseLike<void>) => void;
  reject: (error: any) => void;
}> = [];

const processQueue = (error: any) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

// Create ky instance
const api = ky.create({
  prefixUrl: API_URL,
  timeout: 60000,
  credentials: "include",
  hooks: {
    beforeRequest: [
      async (request) => {
        // Only run in browser environment
        if (typeof window !== 'undefined') {
          const csrfToken = document
            .querySelector('meta[name="csrf-token"]')
            ?.getAttribute("content");
          if (csrfToken) {
            request.headers.set("X-CSRFToken", csrfToken);
          }

          // Get the access token from client-side cookies
          const accessToken = cookieStorage.getItem(
            AUTH_CONFIG.tokenStorage.accessToken
          );
          if (accessToken && !request.url.includes("token/")) {
            request.headers.set("Authorization", `Bearer ${accessToken}`);
          }
        }
      },
    ],
    beforeError: [
      async (error: HTTPError) => {
        const { response } = error;

        // Log the error details
        console.error("API Error:", {
          status: response?.status,
          method: error.request?.method,
          url: error.request?.url,
          message: error.message
        });

        try {
          // Try to get and set the error message from response text
          if (response) {
            error.message = await response.text();
          }
        } catch {}

        // Return the error directly - this is what the type system expects
        return error;
      }
    ],
  },
});

// Interfaces remain unchanged

interface Variant {
  id: string;
  nummer: string;
  bezeichnung: string;
  auspraegung: string;
  prod: boolean;
  vertr: boolean;
  vkArtikel: boolean;
  releas: string;
  price: number;
  selected?: boolean;
  [key: string]: any;
}

interface ProductListParams {
  include_variants?: boolean;
  page?: number;
  page_size?: number;
  q?: string;
  category?: number;
  in_stock?: boolean;
  is_active?: boolean;
  fields?: string;
  [key: string]: any;
}

// Product API methods
export const productApi = {
  getProducts: async (params: ProductListParams = {}, signal?: AbortSignal) => {
    if (params._include_variants !== undefined) {
      params.include_variants = params._include_variants;
      delete params._include_variants;
    }

    // Default query parameters
    const defaultParams: ProductListParams = {
      page_size: 30,
      page: 1,
      is_parent: true,
      fields: "id,name,sku,is_active,variants_count,legacy_base_sku",
      ...params, // Override defaults with any passed parameters
    };

    try {
      const response = await api.get("v1/products/", { 
        searchParams: defaultParams,
        signal 
      }).json<ApiResponse>();
      return response;
    } catch (error) {
      console.error("Error fetching products:", error);
      throw error;
    }
  },

  getProductsDirectSearch: async (params: ProductListParams = {}, signal?: AbortSignal) => {
    if (params._include_variants !== undefined) {
      params.include_variants = params._include_variants;
      delete params._include_variants;
    }

    // Default query parameters
    const defaultParams: ProductListParams = {
      page_size: 30,
      page: 1,
      is_parent: true,
      fields: "id,name,sku,is_active,variants_count,legacy_base_sku",
      ...params, // Override defaults with any passed parameters
    };

    try {
      const response = await api.get("v1/products/direct-search/", { 
        searchParams: defaultParams,
        signal 
      }).json<ApiResponse>();
      return response;
    } catch (error) {
      console.error("Error with direct search for products:", error);
      throw error;
    }
  },

  getProduct: async (id: string | number, signal?: AbortSignal): Promise<Product> => {
    try {
      return await api.get(`v1/products/${id}/`, { signal }).json();
    } catch (error) {
      console.error(`Error fetching product ${id}:`, error);
      throw error;
    }
  },
  getProductBySlug: async (sku: string | number): Promise<Product> => {
    try {
      return await api.get(`v1/products/by-slug/${sku}/`).json();
    } catch (error) {
      console.error(`Error fetching product ${sku}:`, error);
      throw error;
    }
  },

  searchParentProducts: async (searchTerm: string): Promise<Product[]> => {
    try {
      const params = {
        type: "parent", // Assuming backend filters by type=parent
        search: searchTerm,
        fields: "id,name,sku", // Only fetch necessary fields
        page_size: 10, // Limit results for dropdown
      };
      const response = await api.get("v1/products/", { searchParams: params }).json<ApiResponse>();
      return response.results || []; // Return results or empty array
    } catch (error) {
      console.error("Error searching parent products:", error);
      throw error;
    }
  },

  createProduct: async (productData: Omit<Product, "id"> & { parent_id?: number | string }): Promise<Product> => {
    try {
      return await api.post("v1/products/", { json: productData }).json();
    } catch (error) {
      console.error("Error creating product:", error);
      if (error instanceof HTTPError) {
        console.error("HTTPError details:", error);
      }
      throw error;
    }
  },

  updateProduct: async (
    id: string,
    productData: Partial<Product>
  ): Promise<Product> => {
    try {
      return await api.patch(`v1/products/${id}/`, { json: productData }).json();
    } catch (error) {
      console.error(`Error updating product ${id}:`, error);
      throw error;
    }
  },

  deleteProduct: async (id: string): Promise<void> => {
    try {
      await api.delete(`v1/products/${id}/`);
    } catch (error) {
      console.error(`Error deleting product ${id}:`, error);
      throw error;
    }
  },

  getCategories: async () => {
    try {
      return await api.get("v1/products/categories/").json();
    } catch (error) {
      console.error("Error fetching categories:", error);
      throw error;
    }
  },
};

// Variant API methods
export const variantApi = {
  getVariants: async (productId: string): Promise<Variant[]> => {
    try {
      return await api.get(`v1/products/${productId}/variants/`).json();
    } catch (error) {
      console.error(`Error fetching variants for product ${productId}:`, error);
      throw error;
    }
  },

  getVariant: async (variantId: string): Promise<Variant> => {
    try {
      return await api.get(`v1/products/variant/${variantId}/`).json();
    } catch (error) {
      console.error(`Error fetching variant ${variantId}:`, error);
      throw error;
    }
  },

  createVariant: async (
    productId: string,
    variantData: Omit<Variant, "id">
  ): Promise<Variant> => {
    try {
      return await api
        .post(`v1/products/${productId}/variants/`, { json: variantData })
        .json();
    } catch (error) {
      console.error(`Error creating variant for product ${productId}:`, error);
      throw error;
    }
  },

  updateVariant: async (
    productId: string,
    variantId: string,
    variantData: Partial<Variant>
  ): Promise<Variant> => {
    try {
      return await api
        .patch(`v1/products/${productId}/variants/${variantId}/`, {
          json: variantData,
        })
        .json();
    } catch (error) {
      console.error(
        `Error updating variant ${variantId} for product ${productId}:`,
        error
      );
      throw error;
    }
  },

  deleteVariant: async (
    productId: string,
    variantId: string
  ): Promise<void> => {
    try {
      await api.delete(`v1/products/${productId}/variants/${variantId}/`);
    } catch (error) {
      console.error(
        `Error deleting variant ${variantId} for product ${productId}:`,
        error
      );
      throw error;
    }
  },

  deleteVariants: async (
    productId: string,
    variantIds: string[]
  ): Promise<void> => {
    try {
      await api.delete(`v1/products/${productId}/variants/`, {
        json: { variantIds },
      });
    } catch (error) {
      console.error(`Error deleting variants for product ${productId}:`, error);
      throw error;
    }
  },
};

export default api;