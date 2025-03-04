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
</router-link><span class="separator">/</span>
                </div>
                <h1>{{ variant.name }}</h1>
                <p class="sku">SKU: {{ variant.sku }}</p>
                <div class="variant-badges">
                    <div v-if="variant.category" class="category-badge">
                        {{ variant.category.name }}
</div>
                    <div class="stock-badge" :class="{ 'in-stock': variant.in_stock, 'out-of-stock': !variant.in_stock }">
                        {{ variant.in_stock ? 'In Stock' : 'Out of Stock' }}
</div>
                </div>
            </div>
            <div class="variant-layout">
                <!-- Variant images -->
                <div class="variant-images">
                    <div class="main-image">
                        <div v-if="!selectedImage && !variant.primary_image" class="no-image-placeholder">
                            <span>No Image Available</span>
                        </div>
                        <img 
                            v-else
                            :src="selectedImage ? selectedImage.url : (variant.primary_image ? variant.primary_image.url : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`)" 
                            :alt="variant.name"
                            @load="imageLoaded = true"
                            @error="handleImageError"
                            :class="{ 'loading': !imageLoaded }"
                        />
                        <div v-if="!imageLoaded" class="image-loading">
                            <span>Loading...</span>
                        </div>
                    </div>
                    
                    <div v-if="variant.images && variant.images.length > 1" class="image-thumbnails">
                        <div 
                            v-for="image in variant.images" 
                            :key="image.id" 
                            class="thumbnail"
                            :class="{ 
                                active: selectedImage && selectedImage.id === image.id,
                                'loading': !thumbnailsLoaded[image.id]
                            }"
                            @click="selectImage(image)"
                        >
                            <img 
                                :src="image.thumbnail_url || image.url" 
                                :alt="variant.name"
                                @load="handleThumbnailLoad(image.id)"
                                @error="() => handleThumbnailError(image.id)"
                            />
                            <div v-if="!thumbnailsLoaded[image.id]" class="thumbnail-loading">
                                <span>Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- Variant info -->
                <div class="variant-info">
                    <!-- Description -->
                    <div class="info-section">
                        <h3>Description</h3>
                        <p v-if="variant.description">{{ variant.description }}</p>
                        <p v-else>No description available.</p>
                    </div>
                    <!-- Attributes -->
                    <div v-if="variant.attributes && variant.attributes.length > 0" class="info-section">
                        <h3>Attributes</h3>
                        <div class="attributes-list">
                            <div v-for="(attr, index) in variant.attributes" :key="index" class="attribute-item"><span class="attribute-name">{{ attr.name }}:</span><span class="attribute-value">{{ attr.value }}</span>
                            </div>
                        </div>
                    </div>
                    <!-- Details -->
                    <div class="info-section">
                        <h3>Details</h3>
                        <table class="details-table">
                            <tr v-if="variant.category">
                                <td>Category:</td>
                                <td>{{ variant.category.name }}</td>
                            </tr>
                            <tr v-if="variant.in_stock !== undefined">
                                <td>Stock Status:</td>
                                <td>{{ variant.in_stock ? 'In Stock' : 'Out of Stock' }}</td>
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
            <!-- Related variants section -->
            <div v-if="relatedVariants.length > 0" class="related-variants-section">
                <h2>Other Variants of {{ variant.parent?.name }}</h2>
                <div class="variants-grid">
                    <div v-for="relatedVariant in relatedVariants" :key="relatedVariant.id" class="variant-card" @click="viewVariantDetails(relatedVariant.id)">
                        <div class="variant-image">
                            <img :src="relatedVariant.primary_image ? relatedVariant.primary_image.url : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`" :alt="relatedVariant.name"/>
                        </div>
                        <div class="variant-info">
                            <h3>{{ relatedVariant.name }}</h3>
                            <p class="variant-sku">SKU: {{ relatedVariant.sku }}</p>
                            <div class="variant-attributes" v-if="relatedVariant.attributes && relatedVariant.attributes.length"><span v-for="(attr, index) in relatedVariant.attributes" :key="index" class="attribute-badge">
                  {{ attr.name }}: {{ attr.value }} </span>
                            </div>
                            <div class="variant-stock" :class="{ 'in-stock': relatedVariant.in_stock, 'out-of-stock': !relatedVariant.in_stock }">
                                {{ relatedVariant.in_stock ? 'In Stock' : 'Out of Stock' }}
</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
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

interface ParentProduct {
  id: number;
  name: string;
}

interface Variant {
  id: number;
  name: string;
  sku: string;
  description?: string;
  primary_image?: ProductImage;
  images?: ProductImage[];
  category?: Category;
  attributes?: Attribute[];
  parent?: ParentProduct;
  in_stock?: boolean;
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
const variant = ref<Variant>({} as Variant);
const loading = ref(true);
const error = ref('');
const selectedImage = ref<ProductImage | null>(null);
const relatedVariants = ref<Variant[]>([]);
const imageLoaded = ref(false);
const thumbnailsLoaded = ref<Record<number, boolean>>({});

// Computed
const isCurrentVariant = (id: number) => {
  return variant.value.id === id;
};

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
    
    // Load related variants if this is part of a parent product
    if (variant.value.parent && variant.value.parent.id) {
      await loadRelatedVariants(variant.value.parent.id);
    }
  } catch (err) {
    console.error('Error loading variant details:', err);
    error.value = 'Failed to load variant details. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Load related variants
const loadRelatedVariants = async (parentId: number) => {
  try {
    const response = await productApi.getProduct(parentId);
    if (response.data.variants) {
      // Filter out the current variant
      relatedVariants.value = response.data.variants.filter(
        (v: Variant) => v.id !== variant.value.id
      );
    }
  } catch (err) {
    console.error('Error loading related variants:', err);
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
  if (variant.value.parent) {
    router.push({ name: 'ProductDetail', params: { id: variant.value.parent.id } });
  } else {
    router.back();
  }
};

// View variant details
const viewVariantDetails = (id: number) => {
  router.push({ name: 'VariantDetail', params: { id } });
};

// Add these new methods
const handleImageError = () => {
    imageLoaded.value = true;
    // Set fallback image
    const img = event?.target as HTMLImageElement;
    if (img) {
        img.src = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`;
    }
};

const selectImage = (image: ProductImage) => {
    selectedImage.value = image;
    imageLoaded.value = false; // Reset loading state for main image
};

const handleThumbnailLoad = (imageId: number) => {
    thumbnailsLoaded.value[imageId] = true;
};

const handleThumbnailError = (imageId: number) => {
    thumbnailsLoaded.value[imageId] = true;
    // Could add error state handling here if needed
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

.parent-link {
  margin-bottom: 10px;
  font-size: 14px;
}

.parent-link a {
  color: #d2bc9b;
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
  margin-bottom: 10px;
}

.variant-badges {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.category-badge {
  display: inline-block;
  background-color: #d2bc9b;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.stock-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.in-stock {
  background-color: #28a745;
  color: white;
}

.out-of-stock {
  background-color: #dc3545;
  color: white;
}

.variant-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
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
  position: relative;
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
  transition: opacity 0.3s ease;
}

.main-image img.loading {
  opacity: 0;
}

.image-loading,
.thumbnail-loading,
.no-image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  color: #666;
  font-size: 14px;
}

.no-image-placeholder {
  background-color: #eee;
  color: #666;
  font-size: 16px;
}

.image-thumbnails {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.thumbnail {
  position: relative;
  aspect-ratio: 1;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  background-color: #f8f9fa;
  transition: all 0.2s ease;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: opacity 0.3s ease;
}

.thumbnail.loading img {
  opacity: 0;
}

.thumbnail.active {
  border-color: #d2bc9b;
}

.thumbnail:hover {
  border-color: #e6d5c1;
}

.variant-info {
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

.attributes-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attribute-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eaeaea;
}

.attribute-name {
  font-weight: 600;
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

/* Related variants section */
.related-variants-section {
  margin-top: 40px;
}

.related-variants-section h2 {
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
</style> 
