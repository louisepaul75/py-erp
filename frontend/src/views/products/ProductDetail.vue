<template>
  <div class="product-detail">
    <!-- Loading indicator -->
    <div v-if="loading" class="loading">
      <p>Loading product details...</p>
    </div>
    
    <!-- Error message -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="back-button">Go Back</button>
    </div>
    
    <!-- Product details -->
    <div v-else class="product-content">
      <div class="product-header">
        <button @click="goBack" class="back-button">
          &larr; Back to Products
        </button>
        <h1>{{ product.name }}</h1>
        <p class="sku">SKU: {{ product.sku }}</p>
      </div>
      
      <div class="product-layout">
        <!-- Product images -->
        <div class="product-images">
          <div class="main-image">
            <img 
              :src="selectedImage ? selectedImage.url : (product.primary_image ? product.primary_image.url : '/static/images/no-image.png')" 
              :alt="product.name"
            />
          </div>
          
          <div v-if="product.images && product.images.length > 1" class="image-thumbnails">
            <div 
              v-for="image in product.images" 
              :key="image.id" 
              class="thumbnail"
              :class="{ active: selectedImage && selectedImage.id === image.id }"
              @click="selectedImage = image"
            >
              <img :src="image.thumbnail_url" :alt="product.name" />
            </div>
          </div>
        </div>
        
        <!-- Product info -->
        <div class="product-info">
          <div class="info-section">
            <h3>Description</h3>
            <p v-if="product.description">{{ product.description }}</p>
            <p v-else>No description available.</p>
          </div>
          
          <div v-if="product.variants && product.variants.length > 0" class="info-section">
            <h3>Variants</h3>
            <div class="variants-list">
              <div 
                v-for="variant in product.variants" 
                :key="variant.id" 
                class="variant-item"
                @click="viewVariantDetails(variant.id)"
              >
                <span class="variant-name">{{ variant.name }}</span>
                <span class="variant-sku">{{ variant.sku }}</span>
              </div>
            </div>
          </div>
          
          <div class="info-section">
            <h3>Details</h3>
            <table class="details-table">
              <tr v-if="product.category">
                <td>Category:</td>
                <td>{{ product.category.name }}</td>
              </tr>
              <tr v-if="product.is_active !== undefined">
                <td>Status:</td>
                <td>{{ product.is_active ? 'Active' : 'Inactive' }}</td>
              </tr>
              <tr v-if="product.created_at">
                <td>Created:</td>
                <td>{{ formatDate(product.created_at) }}</td>
              </tr>
              <tr v-if="product.updated_at">
                <td>Last Updated:</td>
                <td>{{ formatDate(product.updated_at) }}</td>
              </tr>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { productApi } from '@/services/api';

// Router and route
const router = useRouter();
const route = useRoute();

// Props
const props = defineProps<{
  id?: string | number;
}>();

// State
const product = ref({});
const loading = ref(true);
const error = ref('');
const selectedImage = ref(null);

// Load product details
const loadProduct = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    // Get product ID from props or route params
    const productId = props.id || route.params.id;
    
    if (!productId) {
      throw new Error('Product ID is required');
    }
    
    const response = await productApi.getProduct(Number(productId));
    product.value = response.data;
    
    // Set default selected image
    if (product.value.images && product.value.images.length > 0) {
      selectedImage.value = product.value.primary_image || product.value.images[0];
    }
  } catch (err) {
    console.error('Error loading product details:', err);
    error.value = 'Failed to load product details. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Format date
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// Navigate back
const goBack = () => {
  router.back();
};

// View variant details
const viewVariantDetails = (id: number) => {
  router.push({ name: 'VariantDetail', params: { id } });
};

// Initialize component
onMounted(() => {
  loadProduct();
});
</script>

<style scoped>
.product-detail {
  padding: 20px 0;
}

.loading, .error {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.product-header {
  margin-bottom: 30px;
}

.back-button {
  background-color: transparent;
  border: none;
  color: #d2bc9b;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  margin-bottom: 15px;
  display: inline-block;
}

.back-button:hover {
  text-decoration: underline;
}

h1 {
  margin: 0 0 10px;
  color: #2c3e50;
}

.sku {
  color: #6c757d;
  font-size: 14px;
}

.product-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

@media (max-width: 768px) {
  .product-layout {
    grid-template-columns: 1fr;
  }
}

.product-images {
  display: flex;
  flex-direction: column;
}

.main-image {
  height: 400px;
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 15px;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.image-thumbnails {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.thumbnail {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
}

.thumbnail.active {
  border-color: #d2bc9b;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.info-section {
  padding-bottom: 20px;
  border-bottom: 1px solid #eaeaea;
}

.info-section:last-child {
  border-bottom: none;
}

.info-section h3 {
  margin: 0 0 15px;
  color: #2c3e50;
  font-size: 18px;
}

.variants-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.variant-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.variant-item:hover {
  background-color: #e9ecef;
}

.variant-name {
  font-weight: 500;
}

.variant-sku {
  color: #6c757d;
  font-size: 14px;
}

.details-table {
  width: 100%;
  border-collapse: collapse;
}

.details-table td {
  padding: 8px 0;
}

.details-table td:first-child {
  font-weight: 500;
  width: 120px;
}
</style> 