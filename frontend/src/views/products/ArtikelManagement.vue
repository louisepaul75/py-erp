<template>
  <div class="artikel-management">
    <!-- Header -->
    <div class="artikel-header">
      <div class="artikel-title"><span class="artikel-heart">❤</span><span>Artikel</span></div>
      <div class="window-controls">
        <button class="window-control-button" @click="minimizeWindow"><span>_</span></button>
        <button class="window-control-button" @click="maximizeWindow"><span>□</span></button>
        <button class="window-control-button" @click="closeWindow"><span>×</span></button>
      </div>
    </div>
    <!-- Toolbar -->
    <div class="artikel-toolbar">
      <button class="toolbar-button">
        <PlusIcon class="icon-small" />
      </button>
      <button class="toolbar-button">
        <MinusIcon class="icon-small" />
      </button>
      <div class="search-input-container">
        <AtSignIcon class="search-icon" />
        <input
          class="search-input"
          placeholder="Search..."
          v-model="searchQuery"
          @input="debounceSearch"
        />
      </div>
      <button class="toolbar-button">
        <TypeIcon class="icon-small" />
      </button>
      <button class="toolbar-button">
        <EyeIcon class="icon-small" />
      </button>
      <button class="toolbar-button">
        <SearchIcon class="icon-small" />
      </button>
      <button class="toolbar-button">
        <FileTextIcon class="icon-small" />
      </button>
      <button class="artikel-button" @click="saveProduct">Speichern</button>
      <button class="artikel-button">Artikel übernehmen</button>
      <div class="toolbar-right">
        <button class="toolbar-button">
          <RotateCcwIcon class="icon-small" />
        </button>
        <button class="toolbar-button">
          <SettingsIcon class="icon-small" />
        </button>
      </div>
    </div>
    <!-- Main Content -->
    <div class="artikel-content">
      <!-- Left Panel - Product List -->
      <div class="product-list-panel">
        <div class="artikel-list-container">
          <div class="artikel-list-header">
            <div class="artikel-list-header-item">Nummer</div>
            <div class="artikel-list-header-item">Bezeichnung</div>
          </div>
          <div class="artikel-list" @scroll="handleScroll">
            <!-- Loading state -->
            <div v-if="isLoadingProductList && !productData.length" class="artikel-loading">
              <p>Loading products...</p>
              <div class="loading-spinner"></div>
            </div>
            <!-- Error state -->
            <div v-else-if="productListError && !productData.length" class="artikel-error">
              <p>{{ productListError }}</p>
              <button class="artikel-button" @click="() => loadProducts(false)">Retry</button>
            </div>
            <!-- Empty state -->
            <div v-else-if="productData.length === 0" class="artikel-empty">
              <p>No products found</p>
              <p v-if="searchQuery" class="artikel-empty-hint">Try a different search term</p>
            </div>
            <!-- Product list -->
            <template v-else>
              <div
                v-for="product in productData"
                :key="product.id || product.nummer"
                class="artikel-list-item"
                :class="{ selected: product.selected }"
                @click="selectProduct(product)"
              >
                <div class="artikel-list-item-nummer">{{ product.nummer }}</div>
                <div class="artikel-list-item-bezeichnung">{{ product.bezeichnung }}</div>
              </div>
              <!-- Loading more indicator -->
              <div v-if="isLoadingMoreProducts || loadingAll" class="artikel-list-loading-more">
                <p>
                  {{ loadingAll ? 'Loading all products...' : 'Loading more products...' }} ({{
                    productData.length
                  }}
                  of {{ totalProductCount }})
                </p>
              </div>
              <!-- Load more button -->
              <div v-else-if="hasMorePages" class="artikel-list-load-more">
                <div class="load-buttons">
                  <button class="artikel-button" @click="manualLoadMore">
                    Load More ({{ productData.length }} of {{ totalProductCount }})
                  </button>
                  <button class="artikel-button load-all-button" @click="loadAllProducts">
                    Load All Products
                  </button>
                </div>
              </div>
              <!-- End of list indicator -->
              <div v-else-if="productData.length > 0" class="artikel-list-end">
                <p>Showing all {{ productData.length }} products</p>
              </div>
            </template>
          </div>
        </div>
      </div>
      <!-- Right Panel - Product Details -->
      <div class="product-details-panel">
        <!-- Loading state -->
        <div v-if="isLoadingProduct" class="artikel-loading">
          <p>Loading product details...</p>
        </div>
        <!-- Error state -->
        <div v-else-if="productLoadError" class="artikel-error">
          <p>{{ productLoadError }}</p>
        </div>
        <!-- Product details -->
        <div v-else class="artikel-details">
          <div class="artikel-tabs">
            <button
              class="artikel-tab"
              :class="{ active: activeTab === 'mutter' }"
              @click="activeTab = 'mutter'"
            >
              Mutter
            </button>
            <button
              class="artikel-tab"
              :class="{ active: activeTab === 'varianten' }"
              @click="activeTab = 'varianten'"
            >
              Varianten
            </button>
          </div>
          <div class="artikel-details-content">
            <div v-if="activeTab === 'mutter'">
              <div class="artikel-form-section">
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Bezeichnung</div>
                  <input class="artikel-form-input" v-model="selectedProductData.bezeichnung" />
                </div>
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Beschreibung</div>
                  <textarea
                    class="artikel-form-textarea"
                    v-model="selectedProductData.beschreibung"
                  ></textarea>
                </div>
              </div>
              <div class="artikel-form-section">
                <div class="artikel-form-row checkbox-row">
                  <label class="artikel-checkbox-label">
                    <input type="checkbox" v-model="selectedProductData.hangend" />
                    <span>Hängend</span>
                  </label>
                  <label class="artikel-checkbox-label">
                    <input type="checkbox" v-model="selectedProductData.einseitig" />
                    <span>Einseitig</span>
                  </label>
                </div>
              </div>
              <div class="artikel-form-section">
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Breite</div>
                  <input class="artikel-form-input" v-model="selectedProductData.breite" />
                </div>
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Höhe</div>
                  <input class="artikel-form-input" v-model="selectedProductData.hohe" />
                </div>
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Tiefe</div>
                  <input class="artikel-form-input" v-model="selectedProductData.tiefe" />
                </div>
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Gewicht</div>
                  <input class="artikel-form-input" v-model="selectedProductData.gewicht" />
                </div>
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Boxgröße</div>
                  <input class="artikel-form-input" v-model="selectedProductData.boxgrosse" />
                </div>
              </div>
              <div class="artikel-form-section">
                <div class="artikel-form-row">
                  <div class="artikel-form-label">Tags</div>
                  <input class="artikel-form-input" v-model="selectedProductData.tags" />
                </div>
              </div>
            </div>
            
            <div v-else-if="activeTab === 'varianten'">
              <!-- Storage Locations Section -->
              <div class="artikel-form-section">
                <h3 class="section-title">Lagerorte</h3>
                
                <!-- Loading state -->
                <div v-if="isLoadingStorageLocations" class="artikel-loading">
                  <p>Loading storage locations...</p>
                </div>
                
                <!-- Error state -->
                <div v-else-if="storageLocationsError" class="artikel-error">
                  <p>{{ storageLocationsError }}</p>
                </div>
                
                <!-- Empty state -->
                <div v-else-if="productStorageLocations.length === 0" class="artikel-empty">
                  <p>No storage locations found for this product</p>
                </div>
                
                <!-- Storage locations list -->
                <div v-else class="storage-locations-list">
                  <div class="storage-locations-header">
                    <div class="storage-location-header-item">Location</div>
                    <div class="storage-location-header-item">Code</div>
                    <div class="storage-location-header-item">Quantity</div>
                    <div class="storage-location-header-item">Status</div>
                  </div>
                  <div class="storage-locations-items">
                    <div
                      v-for="location in productStorageLocations"
                      :key="location.id"
                      class="storage-location-item"
                    >
                      <div class="storage-location-name">{{ location.name }}</div>
                      <div class="storage-location-code">{{ location.location_code }}</div>
                      <div class="storage-location-quantity">{{ location.quantity }}</div>
                      <div class="storage-location-status" :class="location.reservation_status.toLowerCase()">
                        {{ location.reservation_status }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Right Side Panel -->
        <div class="side-panel">
          <div class="side-panel-header">
            <span class="section-label">Besteht aus</span>
            <span class="section-label">Anz</span>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="table-header">DE</th>
                  <th class="table-header"></th>
                  <th class="table-header"></th>
                  <th class="table-header"></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="table-cell">EN</td>
                  <td class="table-cell"></td>
                  <td class="table-cell"></td>
                  <td class="table-cell"></td>
                </tr>
                <tr v-for="i in 10" :key="i">
                  <td class="table-cell"></td>
                  <td class="table-cell"></td>
                  <td class="table-cell"></td>
                  <td class="table-cell"></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="publish-button-container">
            <button class="publish-button">Publish</button>
          </div>
          <div class="help-button-container">
            <div class="help-button">?</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Debug panel (only visible in development) -->
  <div v-if="isDevelopment" class="debug-info">
    <div>Total products: {{ totalProductCount }}</div>
    <div>Loaded products: {{ productData.length }}</div>
    <div>Current page: {{ currentPage }}</div>
    <div>Has more pages: {{ hasMorePages ? 'Yes' : 'No' }}</div>
    <div>
      Loading: {{ isLoadingProductList || isLoadingMoreProducts || loadingAll ? 'Yes' : 'No' }}
    </div>
    <div>Loading all: {{ loadingAll ? 'Yes' : 'No' }}</div>
    <div>Pages loaded: {{ loadedPages }}</div>
  </div>
</template>
<script setup lang="ts">
import {
  ref,
  reactive,
  onMounted,
  watch,
  defineProps,
  defineEmits,
  computed,
  onUnmounted
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  Plus as PlusIcon,
  Minus as MinusIcon,
  AtSign as AtSignIcon,
  Type as TypeIcon,
  Eye as EyeIcon,
  Search as SearchIcon,
  FileText as FileTextIcon,
  RotateCcw as RotateCcwIcon,
  Settings as SettingsIcon
} from 'lucide-vue-next';
import { productApi } from '@/services/api';
import { inventoryService, ProductStorageLocation } from '@/services/inventory';

// Define props and emits
const props = defineProps({
  product: {
    type: Object,
    default: null
  },
  id: {
    type: [String, Number],
    default: null
  }
});

const emit = defineEmits(['close']);
const route = useRoute();
const router = useRouter();

// State for loading product data
const isLoadingProduct = ref(false);
const productLoadError = ref('');
const searchQuery = ref('');

// Product data from API
const productData = ref<any[]>([]);
const isLoadingProductList = ref(true);
const productListError = ref('');

// Pagination state
const currentPage = ref(1);
const hasMorePages = ref(false);
const isLoadingMoreProducts = ref(false);
const totalProductCount = ref(0);
const initialLoadComplete = ref(false);
const maxInitialPages = ref(10); // Increased from 5 to 10 pages initially
const loadedPages = ref(0);
const loadingAll = ref(false);

// Selected product data
const selectedProductData = reactive({
  bezeichnung: '',
  beschreibung: '',
  hangend: false,
  einseitig: false,
  breite: '',
  hohe: '',
  tiefe: '',
  gewicht: '',
  boxgrosse: '',
  tags: ''
});

// Storage locations for the selected product
const productStorageLocations = ref<ProductStorageLocation[]>([]);
const isLoadingStorageLocations = ref(false);
const storageLocationsError = ref('');

// Active tab
const activeTab = ref('mutter');

// Debug mode detection
const isDevelopment = computed(() => {
  return process.env.NODE_ENV === 'development';
});

// Load products from API
const loadProducts = async (loadMore = false) => {
  if (loadMore) {
    isLoadingMoreProducts.value = true;
  } else {
    isLoadingProductList.value = true;
    productData.value = []; // Clear existing data when not loading more
    currentPage.value = 1;
    initialLoadComplete.value = false;
    loadedPages.value = 0;
  }

  productListError.value = '';

  try {
    console.log(`Loading products from API... Page: ${currentPage.value}`);
    loadedPages.value++;

    // Create params object for filtering
    const params: Record<string, any> = {
      page_size: 100, // Reduced from 1000 to 100 for faster initial load
      page: currentPage.value,
      q: searchQuery.value, // Apply search query if any
      is_parent: true // Only fetch parent products
    };

    const response = await productApi.getProducts(params);
    console.log('Products API response:', response);

    if (response && response.data) {
      let products = [];

      if (Array.isArray(response.data)) {
        // Handle case where response is a direct array
        products = response.data;
        hasMorePages.value = false; // No pagination info in this case
      } else if (response.data.results) {
        // Handle paginated response
        products = response.data.results;

        // Update pagination state
        hasMorePages.value = !!response.data.next;
        totalProductCount.value = response.data.count || 0;

        console.log('Total products available:', totalProductCount.value);
        console.log('Has next page:', hasMorePages.value);
        console.log('Products loaded in this batch:', products.length);
        console.log(`Loaded ${loadedPages.value} pages so far`);
        console.log(
          `Total products loaded: ${loadMore ? productData.value.length + products.length : products.length} of ${totalProductCount.value}`
        );
      }

      // Map the products to the format needed for the list
      const mappedProducts = products.map((product: any) => ({
        nummer: product.sku || '', // Map SKU to Nummer
        bezeichnung: product.name || '', // Map Name to Bezeichnung
        id: product.id,
        selected: false,
        product: product // Keep the original product data
      }));

      if (loadMore) {
        // Append to existing products
        productData.value = [...productData.value, ...mappedProducts];
      } else {
        // Replace existing products
        productData.value = mappedProducts;
      }

      console.log('Total mapped products in view:', productData.value.length);

      // Automatically load more pages during initial load
      if (
        hasMorePages.value &&
        !initialLoadComplete.value &&
        currentPage.value < maxInitialPages.value
      ) {
        console.log(`Initial load: automatically loading page ${currentPage.value + 1}...`);
        currentPage.value++;
        setTimeout(() => loadProducts(true), 100);
      } else {
        initialLoadComplete.value = true;

        // If we're loading all products, continue loading until we have all of them
        if (loadingAll.value && hasMorePages.value) {
          console.log('Loading all products: continuing to next page');
          currentPage.value++;
          setTimeout(() => loadProducts(true), 100);
        } else {
          loadingAll.value = false;
        }
      }
    }
  } catch (err: any) {
    console.error('Error loading products:', err);
    productListError.value = `Failed to load products: ${err.message || 'Unknown error'}`;

    if (!loadMore) {
      // Only clear if not loading more
      productData.value = [];
    }

    initialLoadComplete.value = true;
    loadingAll.value = false;
  } finally {
    if (loadMore) {
      isLoadingMoreProducts.value = false;
    } else {
      isLoadingProductList.value = false;
    }
  }
};

// Load more products when scrolling
const loadMoreProducts = () => {
  if (hasMorePages.value && !isLoadingMoreProducts.value) {
    currentPage.value++;
    loadProducts(true);
  }
};

// Handle scroll event to load more products
const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement;
  const scrollPosition = target.scrollTop + target.clientHeight;
  const scrollHeight = target.scrollHeight;

  // Load more when user scrolls to 80% of the list (reduced from 90%)
  const scrollThreshold = 0.8;

  console.log(
    `Scroll position: ${scrollPosition}, Scroll height: ${scrollHeight}, Threshold: ${scrollHeight * scrollThreshold}`
  );

  if (
    scrollPosition > scrollHeight * scrollThreshold &&
    hasMorePages.value &&
    !isLoadingMoreProducts.value
  ) {
    console.log('Scroll threshold reached, loading more products...');
    loadMoreProducts();
  }
};

// Add a method to manually load more products
const manualLoadMore = () => {
  if (hasMorePages.value && !isLoadingMoreProducts.value) {
    console.log('Manually loading more products...');
    loadMoreProducts();
  }
};

// Filter products based on search query
const filterProducts = () => {
  // Reset pagination when filtering
  currentPage.value = 1;
  initialLoadComplete.value = false;
  loadProducts();
};

// Debounce search input
let searchTimeout: number | null = null;
const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  searchTimeout = setTimeout(() => {
    filterProducts();
  }, 300) as unknown as number;
};

// Select product function
const selectProduct = async (product: {
  nummer: string;
  bezeichnung: string;
  selected?: boolean;
  id?: number;
}) => {
  // Clear previous selection
  productData.value.forEach((p) => (p.selected = false));

  // Set new selection
  product.selected = true;

  // If product has ID, load its details
  if (product.id) {
    await loadProductDetails(product.id);
  }
};

// Load product details from API
const loadProductDetails = async (productId: number) => {
  isLoadingProduct.value = true;
  productLoadError.value = '';

  try {
    console.log('Loading product details for ID:', productId);
    const response = await productApi.getProduct(productId);

    if (response && response.data) {
      console.log('Product details loaded:', response.data);

      // Map API product data to ArtikelManagement format
      const product = response.data;

      selectedProductData.bezeichnung = product.name || '';
      selectedProductData.beschreibung = product.description || '';
      selectedProductData.hangend = product.is_hanging || false;
      selectedProductData.einseitig = product.is_one_sided || false;

      // Map additional fields if they exist
      if (product.attributes) {
        // Extract dimensions and other attributes
        product.attributes.forEach((attr: any) => {
          const name = attr.name?.toLowerCase();
          const value = attr.value;

          if (name === 'breite' || name === 'width') {
            selectedProductData.breite = value;
          } else if (name === 'höhe' || name === 'height') {
            selectedProductData.hohe = value;
          } else if (name === 'tiefe' || name === 'depth') {
            selectedProductData.tiefe = value;
          } else if (name === 'gewicht' || name === 'weight') {
            selectedProductData.gewicht = value;
          } else if (name === 'boxgröße' || name === 'box size') {
            selectedProductData.boxgrosse = value;
          }
        });
      }

      // Extract tags if they exist
      if (product.tags) {
        selectedProductData.tags = Array.isArray(product.tags)
          ? product.tags.join(', ')
          : product.tags;
      }
      
      // Load storage locations for this product
      await loadStorageLocations(productId);
    }
  } catch (err: any) {
    console.error('Error loading product details:', err);
    productLoadError.value = `Failed to load product details: ${err.message || 'Unknown error'}`;
  } finally {
    isLoadingProduct.value = false;
  }
};

// Load storage locations for a product
const loadStorageLocations = async (productId: number) => {
  isLoadingStorageLocations.value = true;
  storageLocationsError.value = '';
  
  try {
    console.log('Loading storage locations for product ID:', productId);
    const locations = await inventoryService.getLocationsByProduct(productId);
    productStorageLocations.value = locations;
    console.log('Storage locations loaded:', locations);
  } catch (err: any) {
    console.error('Error loading storage locations:', err);
    storageLocationsError.value = `Failed to load storage locations: ${err.message || 'Unknown error'}`;
    productStorageLocations.value = [];
  } finally {
    isLoadingStorageLocations.value = false;
  }
};

// Load product data from API by ID
const loadProductFromApi = async (productId: string | number) => {
  isLoadingProduct.value = true;
  productLoadError.value = '';

  try {
    console.log('Loading product data for ID:', productId);
    // Ensure productId is a number
    const id = typeof productId === 'string' ? parseInt(productId, 10) : productId;
    const response = await productApi.getProduct(id);

    if (response && response.data) {
      console.log('Product data loaded:', response.data);

      // Map API product data to ArtikelManagement format
      const product = response.data;

      selectedProductData.bezeichnung = product.name || '';
      selectedProductData.beschreibung = product.description || '';
      selectedProductData.hangend = product.is_hanging || false;
      selectedProductData.einseitig = product.is_one_sided || false;

      // Map additional fields if they exist
      if (product.attributes) {
        // Extract dimensions and other attributes
        product.attributes.forEach((attr: any) => {
          const name = attr.name?.toLowerCase();
          const value = attr.value;

          if (name === 'breite' || name === 'width') {
            selectedProductData.breite = value;
          } else if (name === 'höhe' || name === 'height') {
            selectedProductData.hohe = value;
          } else if (name === 'tiefe' || name === 'depth') {
            selectedProductData.tiefe = value;
          } else if (name === 'gewicht' || name === 'weight') {
            selectedProductData.gewicht = value;
          } else if (name === 'boxgröße' || name === 'box size') {
            selectedProductData.boxgrosse = value;
          }
        });
      }

      // Extract tags if they exist
      if (product.tags) {
        selectedProductData.tags = Array.isArray(product.tags)
          ? product.tags.join(', ')
          : product.tags;
      }

      // Select the corresponding product in the list if it exists
      if (product.sku) {
        const matchingProduct = productData.value.find((p) => p.nummer === product.sku);
        if (matchingProduct) {
          selectProduct(matchingProduct);
        }
      }
      
      // Load storage locations for this product
      await loadStorageLocations(id);
    }
  } catch (err: any) {
    console.error('Error loading product:', err);
    productLoadError.value = `Failed to load product: ${err.message || 'Unknown error'}`;
  } finally {
    isLoadingProduct.value = false;
  }
};

// Window control functions
const minimizeWindow = () => {
  console.log('Minimize window');
};

const maximizeWindow = () => {
  console.log('Maximize window');
};

const closeWindow = () => {
  // If we're in a modal, emit close event
  if (props.product) {
    emit('close');
  }
  // If we're in a standalone page, navigate back
  else {
    router.back();
  }
};

// Save product changes
const saveProduct = async () => {
  try {
    // Get the currently selected product from the list
    const selectedProduct = productData.value.find((p) => p.selected);
    if (!selectedProduct?.id) {
      console.error('No product selected');
      return;
    }

    // Prepare data for update
    const updateData = {
      name: selectedProductData.bezeichnung,
      description: selectedProductData.beschreibung,
      is_hanging: selectedProductData.hangend,
      is_one_sided: selectedProductData.einseitig
    };

    // Update the product
    const response = await productApi.updateProduct(selectedProduct.id, updateData);
    console.log('Product updated:', response.data);

    // Update the product in the list
    selectedProduct.bezeichnung = selectedProductData.bezeichnung;
    selectedProduct.product = response.data;
  } catch (err: any) {
    console.error('Error saving product:', err);
    productLoadError.value = `Failed to save product: ${err.message || 'Unknown error'}`;
  }
};

// Watch for product prop changes
watch(
  () => props.product,
  (newProduct) => {
    if (newProduct) {
      console.log('Product data received via prop:', newProduct);

      // Map the product data to the ArtikelManagement format
      selectedProductData.bezeichnung = newProduct.name || '';
      selectedProductData.beschreibung = newProduct.description || '';
      selectedProductData.hangend = newProduct.is_hanging || false;
      selectedProductData.einseitig = newProduct.is_one_sided || false;

      // Map additional fields if they exist
      if (newProduct.attributes) {
        // Extract dimensions and other attributes
        newProduct.attributes.forEach((attr: any) => {
          const name = attr.name?.toLowerCase();
          const value = attr.value;

          if (name === 'breite' || name === 'width') {
            selectedProductData.breite = value;
          } else if (name === 'höhe' || name === 'height') {
            selectedProductData.hohe = value;
          } else if (name === 'tiefe' || name === 'depth') {
            selectedProductData.tiefe = value;
          } else if (name === 'gewicht' || name === 'weight') {
            selectedProductData.gewicht = value;
          } else if (name === 'boxgröße' || name === 'box size') {
            selectedProductData.boxgrosse = value;
          }
        });
      }

      // Extract tags if they exist
      if (newProduct.tags) {
        selectedProductData.tags = Array.isArray(newProduct.tags)
          ? newProduct.tags.join(', ')
          : newProduct.tags;
      }

      // Select the corresponding product in the list if it exists
      if (newProduct.sku) {
        const matchingProduct = productData.value.find((p) => p.nummer === newProduct.sku);
        if (matchingProduct) {
          selectProduct(matchingProduct);
        }
      }
    }
  },
  { immediate: true }
);

// Watch for route param changes
watch(
  () => route.params.id,
  (newId) => {
    if (newId && !props.product) {
      // Ensure newId is a string or number, not an array
      const id = Array.isArray(newId) ? newId[0] : newId;
      loadProductFromApi(id);
    }
  },
  { immediate: true }
);

// Add a method to load ALL products
const loadAllProducts = () => {
  if (!loadingAll.value) {
    console.log('Loading ALL products...');
    loadingAll.value = true;

    // If we already have some products loaded, just continue from current page
    if (productData.value.length > 0 && hasMorePages.value) {
      currentPage.value++;
      loadProducts(true);
    } else {
      // Otherwise start fresh
      loadProducts();
    }
  }
};

onMounted(() => {
  console.log('ArtikelManagement component mounted');
  console.log('Initial product prop:', props.product);
  console.log('Route params:', route.params);

  // Load the product list
  loadProducts();

  // If we have an ID from the route and no product prop, load the product
  const routeId = route.params.id || props.id;
  if (routeId && !props.product) {
    // Ensure routeId is a string or number, not an array
    const id = Array.isArray(routeId) ? routeId[0] : routeId;
    loadProductFromApi(id);
  }

  // Add event listener for window resize to adjust loading behavior
  window.addEventListener('resize', handleResize);

  // Initial check if we should load all products based on screen size
  checkIfShouldLoadAll();
});

// Clean up event listeners
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

// Handle window resize
const handleResize = () => {
  checkIfShouldLoadAll();
};

// Check if we should load all products based on screen size
const checkIfShouldLoadAll = () => {
  // On larger screens, automatically load all products
  if (
    window.innerWidth >= 1440 &&
    !loadingAll.value &&
    hasMorePages.value &&
    productData.value.length < totalProductCount.value
  ) {
    console.log('Large screen detected, automatically loading all products');
    loadAllProducts();
  }
};
</script>
<style scoped>
.artikel-management {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans',
    'Helvetica Neue', sans-serif;
}

.artikel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
}

.artikel-title {
  font-size: 16px;
  font-weight: 600;
}

.window-controls {
  display: flex;
  gap: 10px;
}

.window-control-button {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: #d2bc9b;
  color: white;
}

.window-control-button:hover {
  background-color: #c0a989;
}

.artikel-toolbar {
  display: flex;
  padding: 10px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
  gap: 10px;
}

.toolbar-button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  font-size: 14px;
}

.toolbar-button:hover {
  background-color: #f0f0f0;
}

.search-input-container {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  width: 16px;
  height: 16px;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.artikel-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  height: calc(100vh - 110px); /* Allocate proper height, accounting for header and toolbar */
}

.product-list-panel {
  width: 40%;
  border-right: 1px solid #eaeaea;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%; /* Ensure full height */
}

.product-details-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.artikel-list-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  height: 100%; /* Ensure full height */
}

.artikel-list-header {
  display: flex;
  padding: 10px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
}

.artikel-list-header-item {
  font-weight: 600;
  font-size: 14px;
}

.artikel-list-header-item:first-child {
  width: 100px;
}

.artikel-list-header-item:last-child {
  flex: 1;
}

.artikel-list {
  flex: 1;
  overflow-y: auto;
  height: 100%;
  position: relative;
  scrollbar-width: thin; /* For Firefox */
  scrollbar-color: #d2bc9b #f8f9fa; /* For Firefox */
}

/* Customize scrollbar for WebKit browsers */
.artikel-list::-webkit-scrollbar {
  width: 8px;
}

.artikel-list::-webkit-scrollbar-track {
  background: #f8f9fa;
}

.artikel-list::-webkit-scrollbar-thumb {
  background-color: #d2bc9b;
  border-radius: 4px;
  border: 2px solid #f8f9fa;
}

/* Ensure the list items don't shrink */
.artikel-list-item {
  display: flex;
  padding: 10px;
  border-bottom: 1px solid #eaeaea;
  cursor: pointer;
  min-height: 40px; /* Ensure minimum height for each item */
  flex-shrink: 0; /* Prevent items from shrinking */
}

.artikel-list-item:hover {
  background-color: #f8f9fa;
}

.artikel-list-item.selected {
  background-color: #f0f7ff;
  border-left: 3px solid #d2bc9b;
}

.artikel-list-item-nummer {
  width: 100px;
  font-size: 14px;
}

.artikel-list-item-bezeichnung {
  flex: 1;
  font-size: 14px;
}

/* Loading and error states */
.artikel-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  height: 100%;
  color: #6c757d;
}

.artikel-error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  height: 100%;
  color: #dc3545;
}

.artikel-empty {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  height: 100%;
  color: #6c757d;
}

.artikel-empty-hint {
  font-size: 14px;
  color: #6c757d;
  margin-top: 10px;
}

/* Product details styles */
.artikel-details {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.artikel-tabs {
  display: flex;
  border-bottom: 1px solid #eaeaea;
}

.artikel-tab {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #6c757d;
}

.artikel-tab:hover {
  color: #495057;
}

.artikel-tab.active {
  border-bottom: 2px solid #d2bc9b;
  font-weight: 600;
  color: #212529;
}

.artikel-details-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.artikel-form-section {
  margin-bottom: 20px;
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 20px;
}

.artikel-form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.artikel-form-row {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.artikel-form-label {
  font-size: 14px;
  margin-bottom: 5px;
  font-weight: 500;
  color: #495057;
}

.artikel-form-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.artikel-form-input:focus {
  border-color: #d2bc9b;
  outline: none;
  box-shadow: 0 0 0 2px rgba(210, 188, 155, 0.25);
}

.artikel-form-textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
}

.artikel-form-textarea:focus {
  border-color: #d2bc9b;
  outline: none;
  box-shadow: 0 0 0 2px rgba(210, 188, 155, 0.25);
}

.checkbox-row {
  flex-direction: row;
  gap: 20px;
}

.artikel-checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 14px;
}

.artikel-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background-color: #d2bc9b;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.artikel-button:hover {
  background-color: #c0a989;
}

.icon-small {
  width: 16px;
  height: 16px;
}

.icon-tiny {
  width: 12px;
  height: 12px;
}

/* Add styles for the loading more indicator and end of list */
.artikel-list-loading-more {
  padding: 15px;
  text-align: center;
  color: #6c757d;
  font-size: 14px;
  background-color: #f8f9fa;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60px; /* Increased height for better visibility */
}

.artikel-list-loading-more::before {
  content: '';
  width: 20px;
  height: 20px;
  margin-right: 10px;
  border: 3px solid #d2bc9b;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.artikel-list-end {
  padding: 15px;
  text-align: center;
  color: #6c757d;
  font-size: 14px;
  background-color: #f8f9fa;
  border-top: 1px solid #eaeaea;
  height: 60px; /* Increased height for better visibility */
  display: flex;
  justify-content: center;
  align-items: center;
}

.artikel-list-load-more {
  padding: 15px;
  text-align: center;
  background-color: #f8f9fa;
  border-top: 1px solid #eaeaea;
  height: 60px; /* Increased height for better visibility */
  display: flex;
  justify-content: center;
  align-items: center;
}

.load-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.artikel-list-load-more .artikel-button {
  min-width: 200px; /* Ensure button has good width */
}

.load-all-button {
  background-color: #6c757d;
}

.load-all-button:hover {
  background-color: #5a6268;
}

/* Debug info */
.debug-info {
  position: fixed;
  bottom: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 20px auto;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Storage Locations Styles */
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
}

.storage-locations-list {
  border: 1px solid #eaeaea;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
}

.storage-locations-header {
  display: flex;
  background-color: #f8f9fa;
  padding: 10px;
  font-weight: 600;
  border-bottom: 1px solid #eaeaea;
}

.storage-location-header-item {
  flex: 1;
  font-size: 14px;
}

.storage-locations-items {
  max-height: 300px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #d2bc9b #f8f9fa;
}

.storage-locations-items::-webkit-scrollbar {
  width: 8px;
}

.storage-locations-items::-webkit-scrollbar-track {
  background: #f8f9fa;
}

.storage-locations-items::-webkit-scrollbar-thumb {
  background-color: #d2bc9b;
  border-radius: 4px;
  border: 2px solid #f8f9fa;
}

.storage-location-item {
  display: flex;
  padding: 10px;
  border-bottom: 1px solid #eaeaea;
  transition: background-color 0.2s;
}

.storage-location-item:hover {
  background-color: #f8f9fa;
}

.storage-location-item:last-child {
  border-bottom: none;
}

.storage-location-name,
.storage-location-code,
.storage-location-quantity,
.storage-location-status {
  flex: 1;
  font-size: 14px;
}

.storage-location-status {
  font-weight: 500;
}

.storage-location-status.available {
  color: #4caf50;
}

.storage-location-status.reserved {
  color: #ff9800;
}

.storage-location-status.allocated {
  color: #2196f3;
}

.storage-location-status.picked {
  color: #f44336;
}
</style>
