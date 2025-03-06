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
        <div v-if="product.category" class="category-badge">
          {{ product.category.name }}
        </div>
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

      <!-- Variants section -->
      <div v-if="product.variants && product.variants.length > 0" class="variants-section">
        <h2>Product Variants ({{ product.variants.length }})</h2>

        <div class="variants-grid">
          <div
            v-for="variant in product.variants"
            :key="variant.id"
            class="variant-card"
            @click="viewVariantDetails(variant.id)"
          >
            <div class="variant-image">
              <img
                :src="variant.primary_image ? variant.primary_image.url : '/static/images/no-image.png'"
                :alt="variant.name"
              />
            </div>
            <div class="variant-info">
              <h3>{{ variant.name }}</h3>
              <p class="variant-sku">SKU: {{ variant.sku }}</p>
              <div class="variant-attributes" v-if="variant.attributes && variant.attributes.length">
                <span
                  v-for="(attr, index) in variant.attributes"
                  :key="index"
                  class="attribute-badge"
                >
                  {{ attr.name }}: {{ attr.value }}
                </span>
              </div>
              <div class="variant-stock" :class="{ 'in-stock': variant.in_stock, 'out-of-stock': !variant.in_stock }">
                {{ variant.in_stock ? 'In Stock' : 'Out of Stock' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-variants">
        <p>This product has no variants.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { productApi } from '@/services/api';

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

interface Attribute {
  name: string;
  value: string;
}

interface Variant {
  id: number;
  name: string;
  sku: string;
  primary_image?: ProductImage;
  attributes?: Attribute[];
  in_stock?: boolean;
}

interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string;
  primary_image?: ProductImage;
  images?: ProductImage[];
  category?: Category;
  variants?: Variant[];
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

// Router and route
const router = useRouter();
const route = useRoute();

// Props
const props = defineProps<{
  id?: string | number;
}>();

// State
const product = ref<Product>({} as Product);
const loading = ref(true);
const error = ref('');
const selectedImage = ref<ProductImage | null>(null);

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
  position: relative;
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
  margin-bottom: 10px;
}

.category-badge {
  display: inline-block;
  background-color: #d2bc9b;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.product-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-image img {
  max-width: 100%;
  max-height: 100%;
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
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumbnail.active {
  border-color: #d2bc9b;
}

.thumbnail img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.info-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 18px;
}

.details-table {
  width: 100%;
  border-collapse: collapse;
}

.details-table td {
  padding: 8px 0;
  border-bottom: 1px solid #eaeaea;
}

.details-table td:first-child {
  font-weight: 600;
  width: 40%;
}

/* Variants section */
.variants-section {
  margin-top: 40px;
}

.variants-section h2 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.variants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.variant-card {
  border: 1px solid #eaeaea;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  background-color: white;
}

.variant-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.variant-image {
  height: 180px;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.variant-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.variant-info {
  padding: 15px;
}

.variant-info h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #333;
}

.variant-sku {
  color: #6c757d;
  font-size: 12px;
  margin-bottom: 10px;
}

.variant-attributes {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.attribute-badge {
  background-color: #f0f0f0;
  color: #333;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.variant-stock {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 0;
}

.in-stock {
  color: #28a745;
}

.out-of-stock {
  color: #dc3545;
}

.no-variants {
  text-align: center;
  padding: 30px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 40px;
}
</style>
