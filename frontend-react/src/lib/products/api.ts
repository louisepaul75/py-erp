// lib/api.ts
import ky, {
  HTTPError,
  type Options as KyOptions,
  type NormalizedOptions,
} from "ky";
import { API_URL, AUTH_CONFIG } from "../config";

// Cookie storage utility
const cookieStorage = {
  getItem: (name: string) => {
    const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
    return match ? match[2] : null;
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
let isRefreshing = false;
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
  timeout: 30000,
  credentials: "include", // Added for consistency with original
  hooks: {
    beforeRequest: [
      (request) => {
        const csrfToken = document
          .querySelector('meta[name="csrf-token"]')
          ?.getAttribute("content");
        if (csrfToken) {
          request.headers.set("X-CSRFToken", csrfToken);
        }

        // Get the access token from cookies
        const accessToken = cookieStorage.getItem(
          AUTH_CONFIG.tokenStorage.accessToken
        );
        if (accessToken && !request.url.includes("token/")) {
          request.headers.set("Authorization", `Bearer ${accessToken}`);
        }

        console.log("Making request:", {
          method: request.method,
          url: request.url,
          headers: Object.fromEntries(request.headers.entries()),
          token: accessToken ? "Present" : "Not present",
        });
      },
    ],
    beforeError: [
      async (error: HTTPError) => {
        const { response, request } = error;

        if (!response) {
          console.error("Network error:", {
            message: error.message,
            request,
            error,
          });
          return error;
        }

        let errorMessage;
        try {
          errorMessage = await response.text();
        } catch {
          errorMessage = response.statusText;
        }

        console.error("API Error:", {
          status: response.status,
          method: request.method,
          url: request.url,
          fullURL: `${API_URL}${request.url}`,
          error: errorMessage,
          headers: Object.fromEntries(request.headers.entries()),
        });

        // Handle 401 with token refresh
        if (response.status === 401) {
          if (isRefreshing) {
            return new Promise<void>((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            })
              .then(() => {
                // Retry the original request after token refresh
                return ky(request);
              })
              .catch((err) => {
                throw err;
              });
          }

          isRefreshing = true;
          try {
            const refreshToken = cookieStorage.getItem(
              AUTH_CONFIG.tokenStorage.refreshToken
            );
            if (!refreshToken) throw new Error("No refresh token");

            const refreshResponse = await ky
              .post(new URL(AUTH_CONFIG.refreshEndpoint, API_URL).toString(), {
                json: { refresh: refreshToken },
              })
              .json<{ access: string }>();

            const newToken = refreshResponse.access;
            cookieStorage.setItem(
              AUTH_CONFIG.tokenStorage.accessToken,
              newToken,
              {
                maxAge: 15 * 60,
                secure: process.env.NODE_ENV === "production",
                sameSite: "strict",
              }
            );

            processQueue(null); // Resolve all queued requests
            request.headers.set("Authorization", `Bearer ${newToken}`);
            return ky(request); // Retry the original request
          } catch (refreshError) {
            processQueue(refreshError);
            cookieStorage.removeItem(AUTH_CONFIG.tokenStorage.accessToken);
            cookieStorage.removeItem(AUTH_CONFIG.tokenStorage.refreshToken);
            if (typeof window !== "undefined") {
              window.location.href = "/login";
            }
            throw refreshError;
          } finally {
            isRefreshing = false;
          }
        }

        error.message = errorMessage;
        return error;
      },
    ],
  },
});

// Interfaces remain unchanged
interface Product {
  id: string;
  nummer: string;
  bezeichnung: string;
  status: "active" | "inactive" | "draft";
  categories?: { id: string; name: string }[];
  variants?: Variant[];
}

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
}

interface ProductListParams {
  include_variants?: boolean;
  page?: number;
  page_size?: number;
  q?: string;
  category?: number;
  in_stock?: boolean;
  is_active?: boolean;
  [key: string]: any;
}

// Product API methods
export const productApi = {
  getProducts: async (params: ProductListParams = {}) => {
    if (params._ude_variants !== undefined) {
      params.include_variants = params._ude_variants;
      delete params._ude_variants;
    }

    // Default query parameters
    const defaultParams: ProductListParams = {
      page_size: 100,
      page: 1,
      is_parent: true,
      ...params, // Override defaults with any passed parameters
    };

    try {
      return await api.get("products/", { searchParams: defaultParams }).json();
    } catch (error) {
      console.error("Error fetching products:", error);
      throw error;
    }
  },

  getProduct: async (id: string): Promise<Product> => {
    try {
      return await api.get(`products/${id}/`).json();
    } catch (error) {
      console.error(`Error fetching product ${id}:`, error);
      throw error;
    }
  },

  createProduct: async (productData: Omit<Product, "id">): Promise<Product> => {
    try {
      return await api.post("products/", { json: productData }).json();
    } catch (error) {
      console.error("Error creating product:", error);
      throw error;
    }
  },

  updateProduct: async (
    id: string,
    productData: Partial<Product>
  ): Promise<Product> => {
    try {
      return await api.patch(`products/${id}/`, { json: productData }).json();
    } catch (error) {
      console.error(`Error updating product ${id}:`, error);
      throw error;
    }
  },

  deleteProduct: async (id: string): Promise<void> => {
    try {
      await api.delete(`products/${id}/`);
    } catch (error) {
      console.error(`Error deleting product ${id}:`, error);
      throw error;
    }
  },

  getCategories: async () => {
    try {
      return await api.get("products/categories/").json();
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
      return await api.get(`products/${productId}/variants/`).json();
    } catch (error) {
      console.error(`Error fetching variants for product ${productId}:`, error);
      throw error;
    }
  },

  getVariant: async (variantId: string): Promise<Variant> => {
    try {
      return await api.get(`products/variant/${variantId}/`).json();
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
        .post(`products/${productId}/variants/`, { json: variantData })
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
        .patch(`products/${productId}/variants/${variantId}/`, {
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
      await api.delete(`products/${productId}/variants/${variantId}/`);
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
      await api.delete(`products/${productId}/variants/`, {
        json: { variantIds },
      });
    } catch (error) {
      console.error(`Error deleting variants for product ${productId}:`, error);
      throw error;
    }
  },
};

export default api;
