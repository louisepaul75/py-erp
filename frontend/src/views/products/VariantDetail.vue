<template>
  <div class="variant-detail">
    <!-- Loading indicator -->
    <div v-if="loading" class="loading">
      <p>Loading variant details...</p>
    </div>
    
    <!-- Error message -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="back-button">Go Back</button>
    </div>
    
    <!-- Variant details -->
    <div v-else class="variant-content">
      <div class="variant-header">
        <button @click="goBack" class="back-button">
          &larr; Back
        </button>
        <div v-if="variant.parent" class="parent-link">
          <router-link :to="{ name: 'ProductDetail', params: { id: variant.parent.id } }">
            {{ variant.parent.name }}
          </router-link>
          <span class="separator">/</span>
        </div>
        <h1>{{ variant.name }}</h1>
        <p class="sku">SKU: {{ variant.sku }}</p>
      </div>
      
      <div class="variant-layout">
        <!-- Variant images -->
        <div class="variant-images">
          <div class="main-image">
            <img 
              :src="selectedImage ? selectedImage.url : (variant.primary_image ? variant.primary_image.url : '/static/images/no-image.png')" 
              :alt="variant.name"
            />
          </div>
          
          <div v-if="variant.images && variant.images.length > 1" class="image-thumbnails">
            <div 
              v-for="image in variant.images" 
              :key="image.id" 
              class="thumbnail"
              :class="{ active: selectedImage && selectedImage.id === image.id }"
              @click="selectedImage = image"
            >
              <img :src="image.thumbnail_url" :alt="variant.name" />
            </div>
          </div>
        </div>
        
        <!-- Variant info -->
        <div class="variant-info">
          <div class="info-section">
            <h3>Description</h3>
            <p v-if="variant.description">{{ variant.description }}</p>
            <p v-else-if="variant.parent && variant.parent.description">{{ variant.parent.description }}</p>
            <p v-else>No description available.</p>
          </div>
          
          <div class="info-section">
            <h3>Pricing</h3>
            <table class="pricing-table">
              <tr v-if="variant.retail_price !== undefined">
                <td>Retail Price:</td>
                <td>{{ formatPrice(variant.retail_price) }}</td>
              </tr>
              <tr v-if="variant.wholesale_price !== undefined">
                <td>Wholesale Price:</td>
                <td>{{ formatPrice(variant.wholesale_price) }}</td>
              </tr>
              <tr v-if="variant.recommended_price !== undefined">
                <td>Recommended Price:</td>
                <td>{{ formatPrice(variant.recommended_price) }}</td>
              </tr>
              <tr v-if="variant.purchase_price !== undefined">
                <td>Purchase Price:</td>
                <td>{{ formatPrice(variant.purchase_price) }}</td>
              </tr>
            </table>
          </div>
          
          <div class="info-section">
            <h3>Inventory</h3>
            <table class="inventory-table">
              <tr v-if="variant.current_stock !== undefined">
                <td>Current Stock:</td>
                <td>{{ variant.current_stock }}</td>
              </tr>
              <tr v-if="variant.min_stock !== undefined">
                <td>Minimum Stock:</td>
                <td>{{ variant.min_stock }}</td>
              </tr>
              <tr v-if="variant.max_stock !== undefined">
                <td>Maximum Stock:</td>
                <td>{{ variant.max_stock }}</td>
              </tr>
            </table>
          </div>
          
          <div class="info-section">
            <h3>Details</h3>
            <table class="details-table">
              <tr v-if="variant.category">
                <td>Category:</td>
                <td>{{ variant.category.name }}</td>
              </tr>
              <tr v-if="variant.is_active !== undefined">
                <td>Status:</td>
                <td>{{ variant.is_active ? 'Active' : 'Inactive' }}</td>
              </tr>
              <tr v-if="variant.created_at">
                <td>Created:</td>
                <td>{{ formatDate(variant.created_at) }}</td>
              </tr>
              <tr v-if="variant.updated_at">
                <td>Last Updated:</td>
                <td>{{ formatDate(variant.updated_at) }}</td>
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
const variant = ref({});
const loading = ref(true);
const error = ref('');
const selectedImage = ref(null);

// Load variant details
const loadVariant = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    // Get variant ID from props or route params
    const variantId = props.id || route.params.id;
    
    if (!variantId) {
      throw new Error('Variant ID is required');
    }
    
    const response = await productApi.getVariant(Number(variantId));
    variant.value = response.data;
    
    // Set default selected image
    if (variant.value.images && variant.value.images.length > 0) {
      selectedImage.value = variant.value.primary_image || variant.value.images[0];
    }
  } catch (err) {
    console.error('Error loading variant details:', err);
    error.value = 'Failed to load variant details. Please try again.';
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

// Format price
const formatPrice = (price: number) => {
  if (price === undefined || price === null) return '';
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(price);
};

// Navigate back
const goBack = () => {
  router.back();
};

// Initialize component
onMounted(() => {
  loadVariant();
});
</script>

<style scoped>
.variant-detail {
  padding: 20px 0;
}

.loading, .error {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.variant-header {
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

.parent-link {
  margin-bottom: 10px;
}

.parent-link a {
  color: #6c757d;
  text-decoration: none;
}

.parent-link a:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 5px;
  color: #6c757d;
}

h1 {
  margin: 0 0 10px;
  color: #2c3e50;
}

.sku {
  color: #6c757d;
  font-size: 14px;
}

.variant-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

@media (max-width: 768px) {
  .variant-layout {
    grid-template-columns: 1fr;
  }
}

.variant-images {
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

.variant-info {
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

.pricing-table,
.inventory-table,
.details-table {
  width: 100%;
  border-collapse: collapse;
}

.pricing-table td,
.inventory-table td,
.details-table td {
  padding: 8px 0;
}

.pricing-table td:first-child,
.inventory-table td:first-child,
.details-table td:first-child {
  font-weight: 500;
  width: 150px;
}
</style> 