<template>
    <div class="product-list">
        <h1>Products</h1>
        <!-- Search and filter form -->
        <div class="filters">
            <div class="search-box">
                <input type="text" v-model="searchQuery" placeholder="Search products..." @input="debounceSearch"/>
            </div>
            <div class="filter-options">
                <select v-model="selectedCategory" @change="loadProducts">
                    <option value="">All Categories</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">
                        {{ category.name }}
</option>
                </select>
                <label>
                    <input type="checkbox" v-model="inStock" @change="loadProducts"/>
                    In Stock Only
                </label>
            </div>
        </div>
        <!-- Loading indicator -->
        <div v-if="loading" class="loading">
            <p>Loading products...</p>
        </div>
        <!-- Error message -->
        <div v-else-if="error" class="error">
            <p>{{ error }}</p>
            <div class="error-actions">
                <button @click="loadProducts" class="retry-button">
                    Retry
</button>
                <button @click="testApiConnection" class="test-button">
                    Test API
</button>
            </div>
            <div class="api-debug" v-if="showApiDebug">
                <h4>Debug API Connection</h4>
                <div class="api-url-input">
                    <label for="apiUrl">API URL:</label>
                    <input type="text" id="apiUrl" v-model="apiUrl" placeholder="http://localhost:8050"/>
                    <button @click="updateApiUrl" class="update-button">Update</button>
                </div>
            </div>
            <button @click="showApiDebug = !showApiDebug" class="debug-toggle">
                {{ showApiDebug ? 'Hide Debug Options' : 'Show Debug Options' }}
</button>
        </div>
        <!-- Product grid -->
        <div v-else class="product-grid">
            <div v-for="product in products" :key="product.id" class="product-card" @click="viewProductDetails(product.id)">
                <div class="product-image">
                    <img 
                        :src="product.primary_image && product.primary_image.url ? product.primary_image.url : '/static/images/no-image.png'" 
                        :alt="product.name"
                        @error="handleImageError"
                    />
                </div>
                <div class="product-info">
                    <h3>{{ product.name }}</h3>
                    <p class="sku">SKU: {{ product.sku }}</p>
                    <p v-if="product.variants_count" class="variants-badge">
                        {{ product.variants_count }} variants 
                    </p>
                    <p v-if="product.category" class="category">
                        {{ product.category.name }} 
                    </p>
                </div>
            </div>
        </div>
        <!-- Pagination -->
        <div v-if="products.length > 0" class="pagination">
            <button :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
                Previous
</button><span>Page {{ currentPage }} of {{ totalPages }}</span>
            <button :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">
                Next
</button>
        </div>
        <!-- No results message -->
        <div v-if="products.length === 0 && !loading" class="no-results">
            <p>No products found matching your criteria.</p>
        </div>
    </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { productApi } from '@/services/api';
import { useAuthStore } from '@/store/auth';

// Define types
interface Category {
  id: number;
  name: string;
}

interface ProductImage {
  id: number;
  url: string;
  thumbnail_url: string;
}

interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string;
  list_price?: number;
  stock_quantity?: number;
  variants_count?: number;
  primary_image?: ProductImage;
  category?: Category;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

// Router
const router = useRouter();
const authStore = useAuthStore();

// State
const products = ref<Product[]>([]);
const categories = ref<Category[]>([]);
const loading = ref(true);
const error = ref('');
const searchQuery = ref('');
const selectedCategory = ref('');
const inStock = ref(false);
const currentPage = ref(1);
const totalProducts = ref(0);
const pageSize = ref(12);

// Debug state
const showApiDebug = ref(false);
const apiUrl = ref(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050');

// Computed
const totalPages = computed(() => Math.ceil(totalProducts.value / pageSize.value));

// Search debounce
let searchTimeout: number | null = null;

const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1; // Reset to first page on new search
    loadProducts();
  }, 300) as unknown as number;
};

// Mock data for testing when API fails
const mockProducts = [
  {
    id: 1,
    name: 'Office Desk - Premium',
    sku: 'DESK-001',
    variants_count: 4,
    category: { id: 1, name: 'Furniture' },
    primary_image: { 
      id: 1, 
      url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
  {
    id: 2,
    name: 'Ergonomic Office Chair',
    sku: 'CHAIR-002',
    variants_count: 6,
    category: { id: 1, name: 'Furniture' },
    primary_image: { 
      id: 2, 
      url: 'https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1505843490538-5133c6c7d0e1?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
  {
    id: 3,
    name: 'Modern Bookshelf',
    sku: 'SHELF-003',
    variants_count: 3,
    category: { id: 1, name: 'Furniture' },
    primary_image: { 
      id: 3, 
      url: 'https://images.unsplash.com/photo-1588279102080-a8333fd4dc10?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1588279102080-a8333fd4dc10?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
  {
    id: 4,
    name: 'Laptop - Business Series',
    sku: 'TECH-001',
    variants_count: 5,
    category: { id: 2, name: 'Electronics' },
    primary_image: { 
      id: 4, 
      url: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
  {
    id: 5,
    name: 'Wireless Headphones',
    sku: 'TECH-002',
    variants_count: 3,
    category: { id: 2, name: 'Electronics' },
    primary_image: { 
      id: 5, 
      url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
  {
    id: 6,
    name: 'Smart Watch',
    sku: 'TECH-003',
    variants_count: 4,
    category: { id: 2, name: 'Electronics' },
    primary_image: { 
      id: 6, 
      url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
  {
    id: 7,
    name: 'Notebook Set',
    sku: 'STAT-001',
    variants_count: 2,
    category: { id: 3, name: 'Stationery' },
    primary_image: { 
      id: 7, 
      url: 'https://images.unsplash.com/photo-1531346878377-a5be20888e57?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1531346878377-a5be20888e57?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
  {
    id: 8,
    name: 'Premium Pen Set',
    sku: 'STAT-002',
    variants_count: 3,
    category: { id: 3, name: 'Stationery' },
    primary_image: { 
      id: 8, 
      url: 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
      thumbnail_url: 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?ixlib=rb-1.2.1&auto=format&fit=crop&w=200&q=60'
    },
    is_active: true,
  },
];

// Load products with current filters
const loadProducts = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      error.value = 'Please log in to view products';
      router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } });
      return;
    }
    
    // Create params object with only defined values
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value
    };
    
    // Only add parameters that have values
    if (searchQuery.value) params.q = searchQuery.value;
    if (selectedCategory.value) params.category = selectedCategory.value;
    if (inStock.value) params.in_stock = inStock.value;
    
    console.log('API request params:', params);
    
    const response = await productApi.getProducts(params);
    console.log('API response:', response);
    
    if (response && response.data) {
      if (Array.isArray(response.data)) {
        // Handle case where response is a direct array
        products.value = response.data;
        totalProducts.value = response.data.length;
      } else if (response.data.results) {
        // Handle paginated response
        products.value = response.data.results;
        totalProducts.value = response.data.count || response.data.results.length;
      } else {
        // Handle case where results property is missing
        console.error('API response has invalid format:', response.data);
        error.value = 'Invalid API response format';
        products.value = [];
        totalProducts.value = 0;
      }
    } else {
      // Handle case where response or response.data is undefined
      console.error('API response is invalid:', response);
      error.value = 'Invalid API response format';
      products.value = [];
      totalProducts.value = 0;
    }
  } catch (err: any) {
    console.error('Error loading products:', err);
    error.value = `Failed to load products: ${err.message || 'Unknown error'}`;
    
    if (err.response) {
      console.error('API error details:', err.response);
      
      // Handle authentication errors
      if (err.response.status === 401) {
        error.value = 'Please log in to view products';
        router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } });
        return;
      }
      
      error.value += ` (Status: ${err.response.status})`;
      
      if (err.response.data && err.response.data.detail) {
        error.value += ` - ${err.response.data.detail}`;
      }
    }
    
    products.value = [];
    totalProducts.value = 0;
  } finally {
    loading.value = false;
  }
};

// Load categories
const loadCategories = async () => {
  try {
    console.log('Loading categories...');
    const response = await productApi.getCategories();
    console.log('Categories response:', response);
    
    if (response && response.data) {
      categories.value = response.data;
    } else {
      console.error('Invalid categories response:', response);
      categories.value = [];
    }
  } catch (err: any) {
    console.error('Error loading categories:', err);
    categories.value = [];
    
    // Don't show error for categories, just log it
    // This allows the product list to still load even if categories fail
  }
};

// Change page
const changePage = (page: number) => {
  currentPage.value = page;
  loadProducts();
};

// View product details
const viewProductDetails = (id: number) => {
  router.push({ name: 'ProductDetail', params: { id } });
};

// Test API connection with minimal parameters
const testApiConnection = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    console.log('Testing API connection with minimal parameters');
    
    // Try a simple request with no filters
    const response = await productApi.getProducts();
    console.log('API test successful:', response.data);
    
    // If successful, show success message
    error.value = 'API test successful! Now trying to load products...';
    
    // Then try to load products again
    setTimeout(() => {
      loadProducts();
    }, 1000);
  } catch (err: any) {
    console.error('API test failed:', err);
    error.value = `API test failed: ${err.message || 'Unknown error'}`;
    
    if (err.response) {
      console.error('API test response:', err.response);
      error.value += ` (Status: ${err.response.status})`;
      
      if (err.response.data && err.response.data.detail) {
        error.value += ` - ${err.response.data.detail}`;
      }
    }
    
    // Show option to use mock data
    error.value += '\n\nWould you like to use sample data instead?';
    
    // Add button to use mock data
    setTimeout(() => {
      const errorDiv = document.querySelector('.error');
      if (errorDiv) {
        const mockButton = document.createElement('button');
        mockButton.textContent = 'Use Sample Data';
        mockButton.className = 'mock-button';
        mockButton.onclick = useMockData;
        errorDiv.appendChild(mockButton);
      }
    }, 0);
  } finally {
    loading.value = false;
  }
};

// Use mock data instead of API
const useMockData = () => {
  loading.value = true;
  error.value = '';
  
  setTimeout(() => {
    products.value = mockProducts;
    totalProducts.value = mockProducts.length;
    loading.value = false;
  }, 500);
};

// Update API URL
const updateApiUrl = () => {
  // Store in localStorage for persistence
  localStorage.setItem('apiUrl', apiUrl.value);
  
  // Force reload the page to apply the new API URL
  window.location.reload();
};

// Initialize component
onMounted(async () => {
  console.log('ProductList component mounted');
  
  // Check for stored API URL
  const storedApiUrl = localStorage.getItem('apiUrl');
  if (storedApiUrl) {
    apiUrl.value = storedApiUrl;
    console.log('Using stored API URL:', apiUrl.value);
  }
  
  // Initialize auth store if needed
  if (!authStore.isAuthenticated && !authStore.isLoading) {
    await authStore.init();
  }
  
  // Load products from API
  loadProducts();
  
  // Load categories for the filter
  loadCategories();
});

// Check if the server is up
const checkServerStatus = async (): Promise<boolean> => {
  try {
    console.log('Checking server status...');
    
    // Try to fetch the API status
    let response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/status`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      mode: 'cors',
    });
    
    // If status endpoint doesn't exist, try the products endpoint
    if (response.status === 404) {
      console.log('Status endpoint not found, trying products endpoint...');
      response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/products/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        mode: 'cors',
      });
    }
    
    console.log('Server status response:', response);
    
    // Consider 500 errors as server being up but having issues
    if (response.status === 500) {
      console.warn('Server is up but returning 500 error');
      return true;
    }
    
    return response.ok;
  } catch (err) {
    console.error('Server status check failed:', err);
    return false;
  }
};

// Handle image error
const handleImageError = (event: Event) => {
  console.error('Image load failed');
  // Set the source to the fallback image
  if (event.target instanceof HTMLImageElement) {
    event.target.src = '/static/images/no-image.png';
  }
};
</script>
<style scoped>
.product-list {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-box input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filter-options {
  display: flex;
  gap: 15px;
  align-items: center;
}

.filter-options select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.loading, .error, .no-results {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
}

.retry-button, .test-button {
  padding: 8px 15px;
  background-color: #d2bc9b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-button:hover, .test-button:hover {
  background-color: #c0a989;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.product-card {
  border: 1px solid #eaeaea;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  background-color: white;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.product-image {
  height: 200px;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.product-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.product-info {
  padding: 15px;
}

.product-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #333;
  line-height: 1.3;
}

.sku {
  color: #6c757d;
  font-size: 12px;
  margin-bottom: 10px;
}

.variants-badge {
  display: inline-block;
  background-color: #d2bc9b;
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-top: 5px;
}

.category {
  color: #6c757d;
  font-size: 12px;
  margin-top: 5px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.pagination button {
  padding: 8px 15px;
  background-color: #d2bc9b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.pagination button:hover:not(:disabled) {
  background-color: #c0a989;
}

.pagination button:disabled {
  background-color: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
}

.api-debug {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  text-align: left;
}

.api-debug h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.api-url-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.api-url-input input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.update-button {
  padding: 8px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.update-button:hover {
  background-color: #0069d9;
}

.debug-toggle {
  margin-top: 15px;
  background-color: transparent;
  border: 1px solid #d2bc9b;
  color: #d2bc9b;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.debug-toggle:hover {
  background-color: #f8f9fa;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
  }
  
  .filter-options {
    flex-wrap: wrap;
  }
  
  .product-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style> 
