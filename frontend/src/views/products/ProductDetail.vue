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
                        <img :src="getMainImage" :alt="product.name" @error="handleImageError"/>
                    </div>
                    <div v-if="product.images && product.images.length > 1" class="image-thumbnails">
                        <div v-for="image in product.images" :key="image.id" class="thumbnail" :class="{ active: selectedImage && selectedImage.id === image.id }" @click="selectedImage = image">
                            <img :src="getValidImageUrl({ url: image.thumbnail_url || image.url })" :alt="product.name" @error="handleImageError"/>
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
                    <div v-for="variant in product.variants" :key="variant.id" class="variant-card" @click="viewVariantDetails(variant.id)">
                        <div class="variant-image">
                            <img :src="getVariantImage(variant)" :alt="variant.name" @error="handleImageError"/>
                        </div>
                        <div class="variant-info">
                            <h3>{{ variant.name }}</h3>
                            <p class="variant-sku">SKU: {{ variant.sku }}</p>
                            <div class="variant-attributes" v-if="variant.attributes && variant.attributes.length"><span v-for="(attr, index) in variant.attributes" :key="index" class="attribute-badge">
                  {{ attr.name }}: {{ attr.value }} </span>
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
  is_primary?: boolean;
  is_front?: boolean;
  image_type?: string;
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
  images?: ProductImage[];
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

// Add a new function to validate image URLs
const getValidImageUrl = (imageObj?: { url?: string }) => {
    // If no image object or URL, return placeholder
    if (!imageObj?.url) {
        console.log('No image URL provided, using placeholder');
        return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`;
    }

    // Check if URL is valid
    try {
        new URL(imageObj.url);
        return imageObj.url;
    } catch (e) {
        console.log('Invalid image URL:', imageObj.url);
        return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`;
    }
};

// Add an error handler for image loading
const handleImageError = (event: Event) => {
    const img = event.target as HTMLImageElement;
    console.log('Image failed to load:', img.src);
    img.src = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`;
};

// Update the getMainImage computed property
const getMainImage = computed(() => {
    // First try to get BE variant's image
    if (product.value.variants) {
        const beVariant = product.value.variants.find(v => 
            v.attributes?.some(attr => 
                attr.name.toLowerCase() === 'type' && 
                attr.value.toLowerCase() === 'be'
            ) ||
            v.sku?.toLowerCase().includes('be')
        );
        
        console.log('Found BE variant:', beVariant); // Debug log
        
        if (beVariant && beVariant.images && beVariant.images.length > 0) {
            // Try to find the best image from the BE variant
            const beImage = beVariant.images.find(img => 
                img.image_type === 'Produktfoto' && img.is_front
            ) || beVariant.images.find(img => 
                img.image_type === 'Produktfoto'
            ) || beVariant.images.find(img => 
                img.is_front
            ) || beVariant.images.find(img => 
                img.is_primary
            ) || beVariant.images[0];
            
            if (beImage) {
                console.log('Using BE variant image:', beImage.url); // Debug log
                return getValidImageUrl({ url: beImage.url });
            }
        } else if (beVariant?.primary_image) {
            console.log('Using BE variant primary image:', beVariant.primary_image.url); // Debug log
            return getValidImageUrl(beVariant.primary_image);
        }
    }
    
    // If selected image exists, use it
    if (selectedImage.value) {
        console.log('Using selected image:', selectedImage.value.url); // Debug log
        return getValidImageUrl(selectedImage.value);
    }
    
    // If product has images, use the best one
    if (product.value.images && product.value.images.length > 0) {
        const bestImage = product.value.images.find(img => 
            img.image_type === 'Produktfoto' && img.is_front
        ) || product.value.images.find(img => 
            img.image_type === 'Produktfoto'
        ) || product.value.images.find(img => 
            img.is_front
        ) || product.value.images.find(img => 
            img.is_primary
        ) || product.value.images[0];
        
        if (bestImage) {
            console.log('Using best product image:', bestImage.url); // Debug log
            return getValidImageUrl({ url: bestImage.url });
        }
    }
    
    // If product has primary image, use it
    if (product.value.primary_image) {
        console.log('Using product primary image:', product.value.primary_image.url); // Debug log
        return getValidImageUrl(product.value.primary_image);
    }
    
    // Fallback to no-image
    console.log('No image found, using placeholder'); // Debug log
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`;
});

// Update the getVariantImage function
const getVariantImage = (variant: Variant) => {
    if (variant.images && variant.images.length > 0) {
        const bestImage = variant.images.find(img => 
            img.image_type === 'Produktfoto' && img.is_front
        ) || variant.images.find(img => 
            img.image_type === 'Produktfoto'
        ) || variant.images.find(img => 
            img.is_front
        ) || variant.images.find(img => 
            img.is_primary
        ) || variant.images[0];
        
        if (bestImage) {
            return getValidImageUrl({ url: bestImage.url });
        }
    }
    
    if (variant.primary_image?.url) {
        return getValidImageUrl(variant.primary_image);
    }
    
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8050'}/static/images/no-image.png`;
};

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
        console.log('=== DEBUG API RESPONSE ===');
        console.log('Full response:', JSON.stringify(response.data, null, 2));
        console.log('Product images:', response.data.images);
        console.log('Primary image:', response.data.primary_image);
        if (response.data.variants) {
            response.data.variants.forEach((variant: Variant) => {
                console.log(`Variant ${variant.sku}:`, {
                    attributes: variant.attributes,
                    primary_image: variant.primary_image,
                    name: variant.name
                });
            });
        }
        console.log('=== END DEBUG ===');
        
        product.value = response.data;
        
        // First try to set BE variant image as default
        if (product.value.variants) {
            const beVariant = product.value.variants.find(v => 
                v.attributes?.some(attr => 
                    attr.name.toLowerCase() === 'type' && 
                    attr.value.toLowerCase() === 'be'
                ) ||
                v.sku?.toLowerCase().includes('be')
            );
            
            if (beVariant) {
                console.log('=== DEBUG BE VARIANT ===');
                console.log('Found BE variant:', beVariant.sku);
                console.log('BE variant primary image:', beVariant.primary_image);
                console.log('BE variant attributes:', beVariant.attributes);
                console.log('=== END DEBUG ===');
                
                if (beVariant.primary_image) {
                    selectedImage.value = beVariant.primary_image;
                }
            }
        }
        
        // If no BE variant image, fall back to product images
        if (!selectedImage.value && product.value.images && product.value.images.length > 0) {
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
