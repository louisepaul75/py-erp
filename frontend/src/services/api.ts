import axios from 'axios';

// Get API base URL from localStorage, environment variable, or use default
const storedApiUrl = localStorage.getItem('apiUrl');
const apiBaseUrl = storedApiUrl || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050/api';
console.log('Using API base URL:', apiBaseUrl);

// Create axios instance with default config
const api = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  withCredentials: true, // Important for CSRF token handling
  timeout: 10000, // 10 second timeout
});

// Add request interceptor to include CSRF token
api.interceptors.request.use((config) => {
  // Get CSRF token from cookie
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

// Helper function to get cookies
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

// Product API endpoints
export const productApi = {
  // Get all products with optional filters
  getProducts: async (params = {}) => {
    return api.get('/products/', { params });
  },
  
  // Get product details by ID
  getProduct: async (id: number) => {
    return api.get(`/products/${id}/`);
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