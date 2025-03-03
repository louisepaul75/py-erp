<template>
  <div class="product-list">
    <h1>Products</h1>
    
    <!-- Search and filter form -->
    <div class="filters">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search products..." 
          @input="debounceSearch"
        />
      </div>
      
      <div class="filter-options">
        <select v-model="selectedCategory" @change="loadProducts">
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        
        <label>
          <input type="checkbox" v-model="inStock" @change="loadProducts" />
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
    </div>
    
    <!-- Product grid -->
    <div v-else class="product-grid">
      <div 
        v-for="product in products" 
        :key="product.id" 
        class="product-card"
        @click="viewProductDetails(product.id)"
      >
        <div class="product-image">
          <img 
            :src="product.primary_image ? product.primary_image.url : '/static/images/no-image.png'" 
            :alt="product.name"
          />
        </div>
        <div class="product-info">
          <h3>{{ product.name }}</h3>
          <p class="sku">SKU: {{ product.sku }}</p>
          <p v-if="product.variants_count" class="variants">
            {{ product.variants_count }} variants available
          </p>
        </div>
      </div>
    </div>
    
    <!-- Pagination -->
    <div v-if="products.length > 0" class="pagination">
      <button 
        :disabled="currentPage === 1" 
        @click="changePage(currentPage - 1)"
      >
        Previous
      </button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button 
        :disabled="currentPage === totalPages" 
        @click="changePage(currentPage + 1)"
      >
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

// Router
const router = useRouter();

// State
const products = ref([]);
const categories = ref([]);
const loading = ref(true);
const error = ref('');
const searchQuery = ref('');
const selectedCategory = ref('');
const inStock = ref(false);
const currentPage = ref(1);
const totalProducts = ref(0);
const pageSize = ref(12);

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

// Load products with current filters
const loadProducts = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const params = {
      page: currentPage.value,
      q: searchQuery.value,
      category: selectedCategory.value,
      in_stock: inStock.value,
    };
    
    const response = await productApi.getProducts(params);
    products.value = response.data.results;
    totalProducts.value = response.data.count;
  } catch (err) {
    console.error('Error loading products:', err);
    error.value = 'Failed to load products. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Load categories
const loadCategories = async () => {
  try {
    const response = await productApi.getCategories();
    categories.value = response.data;
  } catch (err) {
    console.error('Error loading categories:', err);
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

// Initialize component
onMounted(() => {
  loadCategories();
  loadProducts();
});
</script>

<style scoped>
.product-list {
  padding: 20px 0;
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
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.product-image {
  height: 200px;
  overflow: hidden;
  background-color: #f8f9fa;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.product-info {
  padding: 15px;
}

.product-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #2c3e50;
}

.sku {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 5px;
}

.variants {
  font-size: 12px;
  color: #28a745;
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
}

.pagination button:disabled {
  background-color: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
}
</style> 