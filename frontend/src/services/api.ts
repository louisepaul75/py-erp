import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  withCredentials: true, // Important for CSRF token handling
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

export default api; 