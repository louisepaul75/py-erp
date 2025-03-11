<template>
  <div class="category-list">
    <h1>Product Categories</h1>

    <!-- Loading indicator -->
    <div v-if="loading" class="loading">
      <p>Loading categories...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <!-- Categories grid -->
    <div v-else class="categories-grid">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card"
        @click="filterProductsByCategory(category.id)"
      >
        <h3>{{ category.name }}</h3>
        <p v-if="category.description">{{ category.description }}</p>
        <p v-if="category.product_count" class="product-count">
          {{ category.product_count }} products
        </p>
      </div>
    </div>

    <!-- No categories message -->
    <div v-if="categories.length === 0 && !loading" class="no-results">
      <p>No categories found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { productApi } from '@/services/api';

// Router
const router = useRouter();

// State
const categories = ref([]);
const loading = ref(true);
const error = ref('');

// Load categories
const loadCategories = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await productApi.getCategories();
    categories.value = response.data;
  } catch (err) {
    console.error('Error loading categories:', err);
    error.value = 'Failed to load categories. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Filter products by category
const filterProductsByCategory = (categoryId: number) => {
  router.push({
    name: 'ProductList',
    query: { category: categoryId.toString() }
  });
};

// Initialize component
onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.category-list {
  padding: 20px 0;
}

h1 {
  margin-bottom: 30px;
}

.loading,
.error,
.no-results {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.category-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  cursor: pointer;
  height: 100%;
  min-height: 150px;
  display: flex;
  flex-direction: column;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.category-card h3 {
  margin: 0 0 15px;
  color: #d2bc9b;
}

.category-card p {
  margin: 0 0 10px;
  color: #6c757d;
}

.product-count {
  margin-top: auto;
  font-weight: 500;
  color: #28a745;
}
</style>
