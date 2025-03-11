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
        <button @click="goBack" class="back-button">&larr; Back to Products</button>
        <h1>{{ product.name }}</h1>
        <p class="sku">SKU: {{ product.sku }}</p>
        <div v-if="product.category" class="category-badge">
          {{ product.category.name }}
        </div>
      </div>
      <div class="product-layout">
        <!-- Product images (from variants) -->
        <div class="product-images">
          <div class="main-image">
            <img :src="getMainImage" :alt="product.name" @error="handleImageError" />
          </div>
          <!-- Display thumbnails from variant images -->
          <div v-if="variantThumbnails.length > 1" class="image-thumbnails">
            <div
              v-for="image in variantThumbnails"
              :key="image.id"
              class="thumbnail"
              :class="{ active: selectedImage && selectedImage.id === image.id }"
              @click="selectedImage = image"
            >
              <img
                :src="getValidImageUrl({ url: image.thumbnail_url || image.url })"
                :alt="product.name"
                @error="handleImageError"
              />
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
              <img :src="getVariantImage(variant)" :alt="variant.name" @error="handleImageError" />
            </div>
            <div class="variant-info">
              <h3>{{ variant.name }}</h3>
              <p class="variant-sku">SKU: {{ variant.sku }}</p>
              <div
                class="variant-attributes"
                v-if="variant.attributes && variant.attributes.length"
              >
                <span
                  v-for="(attr, index) in variant.attributes"
                  :key="index"
                  class="attribute-badge"
                >
                  {{ attr.name }}: {{ attr.value }}
                </span>
              </div>
              <div
                class="variant-stock"
                :class="{ 'in-stock': variant.in_stock, 'out-of-stock': !variant.in_stock }"
              >
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
import { getValidImageUrl, handleImageError, getNoImageUrl } from '@/utils/assetUtils';

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

// Computed property to collect all available images from variants
const variantThumbnails = computed(() => {
  const thumbnails: ProductImage[] = [];

  if (product.value.variants && product.value.variants.length > 0) {
    // First try to get images from BE variant
    const beVariant = product.value.variants.find(
      (v) =>
        v.attributes?.some(
          (attr) => attr.name.toLowerCase() === 'type' && attr.value.toLowerCase() === 'be'
        ) || v.sku?.toLowerCase().includes('be')
    );

    if (beVariant && beVariant.images && beVariant.images.length > 0) {
      // Add all images from BE variant
      thumbnails.push(...beVariant.images);
    }

    // If no BE variant images, collect images from all variants
    if (thumbnails.length === 0) {
      for (const variant of product.value.variants) {
        if (variant.images && variant.images.length > 0) {
          thumbnails.push(...variant.images);
        }
      }
    }
  }

  return thumbnails;
});

// Update the getMainImage computed property
const getMainImage = computed(() => {
  // Parent products don't have their own images, so we must use variant images
  if (product.value.variants && product.value.variants.length > 0) {
    // First try to get BE variant's image with preference for Produktfoto and front=True
    // Find BE variant by checking attributes or SKU
    const beVariant = product.value.variants.find(
      (v) =>
        v.attributes?.some(
          (attr) => attr.name.toLowerCase() === 'type' && attr.value.toLowerCase() === 'be'
        ) || v.sku?.toLowerCase().includes('be')
    );

    console.log('Found BE variant:', beVariant);

    if (beVariant && beVariant.images && beVariant.images.length > 0) {
      // Try to find the best image from the BE variant with priority:
      // 1. Produktfoto with front=True (exact match for requirements)
      const beImage = beVariant.images.find(
        (img) => img.image_type?.toLowerCase() === 'produktfoto' && img.is_front === true
      );

      if (beImage) {
        console.log('Using BE variant Produktfoto with front=True:', beImage.url);
        return getValidImageUrl({ url: beImage.url });
      }

      // 2. Any Produktfoto from BE variant
      const beProductfoto = beVariant.images.find(
        (img) => img.image_type?.toLowerCase() === 'produktfoto'
      );

      if (beProductfoto) {
        console.log('Using BE variant Produktfoto:', beProductfoto.url);
        return getValidImageUrl({ url: beProductfoto.url });
      }

      // 3. Any front=True image from BE variant
      const beFrontImage = beVariant.images.find((img) => img.is_front === true);

      if (beFrontImage) {
        console.log('Using BE variant front image:', beFrontImage.url);
        return getValidImageUrl({ url: beFrontImage.url });
      }

      // 4. Primary image from BE variant
      const bePrimaryImage = beVariant.images.find((img) => img.is_primary === true);

      if (bePrimaryImage) {
        console.log('Using BE variant primary image:', bePrimaryImage.url);
        return getValidImageUrl({ url: bePrimaryImage.url });
      }

      // 5. First image from BE variant
      console.log('Using first BE variant image:', beVariant.images[0].url);
      return getValidImageUrl({ url: beVariant.images[0].url });
    }

    // If BE variant has a primary_image property
    if (beVariant?.primary_image) {
      console.log('Using BE variant primary image:', beVariant.primary_image.url);
      return getValidImageUrl(beVariant.primary_image);
    }

    // If no BE variant or BE variant has no images, use the first variant with images
    for (const variant of product.value.variants) {
      if (variant.images && variant.images.length > 0) {
        // Try to find the best image with the same priority logic
        const bestImage =
          variant.images.find(
            (img) => img.image_type?.toLowerCase() === 'produktfoto' && img.is_front === true
          ) ||
          variant.images.find((img) => img.image_type?.toLowerCase() === 'produktfoto') ||
          variant.images.find((img) => img.is_front === true) ||
          variant.images.find((img) => img.is_primary === true) ||
          variant.images[0];

        console.log('Using image from variant:', variant.sku);
        return getValidImageUrl({ url: bestImage.url });
      }

      if (variant.primary_image) {
        console.log('Using primary image from variant:', variant.sku);
        return getValidImageUrl(variant.primary_image);
      }
    }
  }

  // If selected image exists, use it (this would be from a variant)
  if (selectedImage.value) {
    console.log('Using selected image:', selectedImage.value.url);
    return getValidImageUrl(selectedImage.value);
  }

  // Fallback to no-image if no variant images are available
  console.log('No variant images found, using placeholder');
  return getNoImageUrl();
});

// Update the getVariantImage function
const getVariantImage = (variant: Variant) => {
  if (variant.images && variant.images.length > 0) {
    // 1. First priority: Produktfoto with front=True
    let bestImage = variant.images.find((img) => img.image_type === 'Produktfoto' && img.is_front);

    // 2. Second priority: Any Produktfoto
    if (!bestImage) {
      bestImage = variant.images.find((img) => img.image_type === 'Produktfoto');
    }

    // 3. Third priority: Any front=True image
    if (!bestImage) {
      bestImage = variant.images.find((img) => img.is_front);
    }

    // 4. Fourth priority: Any image marked as primary
    if (!bestImage) {
      bestImage = variant.images.find((img) => img.is_primary);
    }

    // 5. Last resort: First image
    if (!bestImage) {
      bestImage = variant.images[0];
    }

    if (bestImage) {
      return getValidImageUrl({ url: bestImage.url });
    }
  }

  if (variant.primary_image?.url) {
    return getValidImageUrl(variant.primary_image);
  }

  return getNoImageUrl();
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

    // Log variant information
    if (response.data.variants) {
      response.data.variants.forEach((variant: Variant) => {
        console.log(`Variant ${variant.sku}:`, {
          attributes: variant.attributes,
          primary_image: variant.primary_image,
          images: variant.images,
          name: variant.name
        });
      });
    }
    console.log('=== END DEBUG ===');

    product.value = response.data;

    // Parent products don't have their own images, so we must use variant images
    if (product.value.variants && product.value.variants.length > 0) {
      // First try to set BE variant image as default with preference for Produktfoto and front=True
      const beVariant = product.value.variants.find(
        (v) =>
          v.attributes?.some(
            (attr) => attr.name.toLowerCase() === 'type' && attr.value.toLowerCase() === 'be'
          ) || v.sku?.toLowerCase().includes('be')
      );

      if (beVariant) {
        console.log('=== DEBUG BE VARIANT ===');
        console.log('Found BE variant:', beVariant.sku);
        console.log('BE variant images:', beVariant.images);
        console.log('BE variant primary image:', beVariant.primary_image);
        console.log('BE variant attributes:', beVariant.attributes);
        console.log('=== END DEBUG ===');

        // Try to find the best image from the BE variant with priority
        if (beVariant.images && beVariant.images.length > 0) {
          // 1. Produktfoto with front=True
          const beImage = beVariant.images.find(
            (img) => img.image_type?.toLowerCase() === 'produktfoto' && img.is_front === true
          );

          if (beImage) {
            console.log('Setting selected image to BE variant Produktfoto with front=True');
            selectedImage.value = beImage;
          } else {
            // 2. Any Produktfoto
            const beProductfoto = beVariant.images.find(
              (img) => img.image_type?.toLowerCase() === 'produktfoto'
            );

            if (beProductfoto) {
              console.log('Setting selected image to BE variant Produktfoto');
              selectedImage.value = beProductfoto;
            } else {
              // 3. Any front=True image
              const beFrontImage = beVariant.images.find((img) => img.is_front === true);

              if (beFrontImage) {
                console.log('Setting selected image to BE variant front image');
                selectedImage.value = beFrontImage;
              } else {
                // 4. Primary image
                const bePrimaryImage = beVariant.images.find((img) => img.is_primary === true);

                if (bePrimaryImage) {
                  console.log('Setting selected image to BE variant primary image');
                  selectedImage.value = bePrimaryImage;
                } else {
                  // 5. First image
                  console.log('Setting selected image to first BE variant image');
                  selectedImage.value = beVariant.images[0];
                }
              }
            }
          }
        } else if (beVariant.primary_image) {
          console.log('Setting selected image to BE variant primary image');
          selectedImage.value = beVariant.primary_image;
        }
      }

      // If no BE variant image was found, try to find an image from any variant
      if (!selectedImage.value) {
        for (const variant of product.value.variants) {
          if (variant.images && variant.images.length > 0) {
            // Use the same priority logic
            const bestImage =
              variant.images.find(
                (img) => img.image_type?.toLowerCase() === 'produktfoto' && img.is_front === true
              ) ||
              variant.images.find((img) => img.image_type?.toLowerCase() === 'produktfoto') ||
              variant.images.find((img) => img.is_front === true) ||
              variant.images.find((img) => img.is_primary === true) ||
              variant.images[0];

            console.log('Setting selected image from variant:', variant.sku);
            selectedImage.value = bestImage;
            break;
          }

          if (variant.primary_image) {
            console.log('Setting selected image to primary image from variant:', variant.sku);
            selectedImage.value = variant.primary_image;
            break;
          }
        }
      }
    }

    // If no variant image was found, selectedImage will remain null
    if (!selectedImage.value) {
      console.log('No variant images found for this product');
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

.loading,
.error {
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
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
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
