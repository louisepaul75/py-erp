import axios from 'axios';

// Determine the appropriate base URL based on the environment
export const determineBaseUrl = () => {
  // First check localStorage for any manually set URL
  const storedUrl = localStorage.getItem('api_base_url');
  if (storedUrl) return storedUrl;

  // Check if we're running on the specific IP
  const isSpecificIP = window.location.hostname === '192.168.73.65';
  if (isSpecificIP) {
    // Use HTTPS instead of HTTP to avoid Mixed Content errors
    return 'https://192.168.73.65';
  }

  // Then check if we're running locally
  const isLocalhost = window.location.hostname === 'localhost' ||
                     window.location.hostname === '127.0.0.1' ||
                     window.location.hostname === '0.0.0.0';

  // If we're running locally, use localhost URL
  if (isLocalhost) {
    return 'http://localhost:8050';
  }

  // Otherwise use the configured network URL or fallback to window.location.origin
  return import.meta.env.VITE_API_NETWORK_URL || import.meta.env.VITE_API_BASE_URL || window.location.origin;
};

const baseUrl = determineBaseUrl();
const apiBaseUrl = baseUrl;

// Log the API base URL being used
console.log('API Base URL:', apiBaseUrl);
console.log('Running on hostname:', window.location.hostname);
console.log('Is specific IP:', window.location.hostname === '192.168.73.65');
console.log('Is localhost:', window.location.hostname === 'localhost' ||
                          window.location.hostname === '127.0.0.1' ||
                          window.location.hostname === '0.0.0.0');

// Create axios instance with default config
const api = axios.create({
  baseURL: apiBaseUrl + '/api',  // Add /api prefix to all requests
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Required for cookies/CORS
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Add CSRF token if available
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    // Only add Authorization header for authenticated endpoints
    const token = localStorage.getItem('access_token');
    if (token && !config.url?.includes('token/')) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried refreshing token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await api.post('/token/refresh/', {
          refresh: refreshToken
        });

        const newAccessToken = response.data.access;

        // Store the new token
        localStorage.setItem('access_token', newAccessToken);

        // Update the Authorization header
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;

        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, clear tokens and reject
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Product API endpoints
interface ProductListParams {
  _ude_variants?: boolean;
  include_variants?: boolean;
  page?: number;
  page_size?: number;
  q?: string;
  category?: number;
  in_stock?: boolean;
  is_active?: boolean;
  [key: string]: any;
}

export const productApi = {
  // Get all products with optional filters
  getProducts: async (params: ProductListParams = {}) => {
    // Convert _ude_variants to include_variants if present
    if (params._ude_variants !== undefined) {
      params.include_variants = params._ude_variants;
      delete params._ude_variants;
    }
    return api.get('/products/', { params });
  },

  // Get product details by ID
  getProduct: async (id: number) => {
    return api.get(`/products/${id}/`);
  },

  // Update product by ID
  updateProduct: async (id: number, data: any) => {
    return api.patch(`/api/products/${id}/`, data);
  },

  // Get product variant details
  getVariant: async (id: number) => {
    return api.get(`/products/variant/${id}/`);
  },

  // Get all product categories
  getCategories: async () => {
    return api.get('/products/categories/');
  }
};

// Sales API endpoints
export const salesApi = {
  // Get all sales orders with optional filters
  getSalesOrders: async (params = {}) => {
    return api.get('/sales/orders/', { params });
  },

  // Get sales order details by ID
  getSalesOrder: async (id: number) => {
    return api.get(`/sales/orders/${id}/`);
  },

  // Create a new sales order
  createSalesOrder: async (data: any) => {
    return api.post('/sales/orders/', data);
  },

  // Update an existing sales order
  updateSalesOrder: async (id: number, data: any) => {
    return api.put(`/sales/orders/${id}/`, data);
  },

  // Delete a sales order
  deleteSalesOrder: async (id: number) => {
    return api.delete(`/sales/orders/${id}/`);
  },

  // Get all customers
  getCustomers: async (params = {}) => {
    return api.get('/sales/customers/', { params });
  }
};

export default api;
