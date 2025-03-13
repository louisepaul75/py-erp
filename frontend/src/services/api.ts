import axios from 'axios';
import { useAuthStore } from '../store/auth';

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
  const isLocalhost =
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '0.0.0.0';

  // If we're running locally, use localhost URL
  if (isLocalhost) {
    return 'http://localhost:8050';
  }

  // Otherwise use the configured network URL or fallback to window.location.origin
  return (
    import.meta.env.VITE_API_NETWORK_URL ||
    import.meta.env.VITE_API_BASE_URL ||
    window.location.origin
  );
};

const apiBaseUrl = determineBaseUrl();

// Log the API base URL being used
console.log('API Base URL:', apiBaseUrl);
console.log('Running on hostname:', window.location.hostname);
console.log('Is specific IP:', window.location.hostname === '192.168.73.65');
console.log(
  'Is localhost:',
  window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '0.0.0.0'
);

// Create axios instance with default config
const api = axios.create({
  baseURL: apiBaseUrl + '/api', // Add /api prefix to all requests
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // Required for cookies/CORS
});

// Flag to prevent multiple simultaneous token refreshes
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

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

    // Log request for debugging
    console.log('Making request:', {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL || '',
      fullURL: (config.baseURL || '') + (config.url || ''),
      headers: config.headers,
      token: token ? 'Present' : 'Not present'
    });

    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is network-related, log it and reject
    if (!error.response) {
      console.error('Network error:', {
        message: error.message,
        config: {
          url: originalRequest?.url,
          baseURL: originalRequest?.baseURL,
          method: originalRequest?.method,
          headers: originalRequest?.headers
        }
      });
      return Promise.reject(error);
    }

    // Log response error for debugging
    console.error('Response error:', {
      status: error.response?.status,
      url: originalRequest.url,
      baseURL: originalRequest.baseURL,
      fullURL: originalRequest.baseURL + originalRequest.url,
      error: error.response?.data,
      headers: originalRequest.headers
    });

    // Handle 401 Unauthorized error
    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        try {
          const token = await new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          });
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return api(originalRequest);
        } catch (err) {
          return Promise.reject(err);
        }
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await api.post('/token/refresh/', {
          refresh: refreshToken
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        originalRequest.headers['Authorization'] = `Bearer ${access}`;

        processQueue(null, access);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
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
  },

  // Get customer details by ID
  getCustomer: async (id: number) => {
    return api.get(`/sales/customers/${id}/`);
  },

  // Update an existing customer
  updateCustomer: async (id: number, data: any) => {
    return api.put(`/sales/customers/${id}/`, data);
  },

  // Get orders for a specific customer
  getCustomerOrders: async (customerId: number, params = {}) => {
    return api.get(`/sales/customers/${customerId}/orders/`, { params });
  },

  // Delete a customer
  deleteCustomer: async (id: number) => {
    return api.delete(`/sales/customers/${id}/`);
  }
};

// External API connection endpoints
export const externalApiConnections = {
  // Get all connection settings
  getConnections: async () => {
    return api.get('/external/connections/');
  },

  // Update a connection setting
  updateConnection: async (connectionName: string, enabled: boolean) => {
    return api.post(`/external/connections/${connectionName}/`, { enabled });
  }
};

export default api;
