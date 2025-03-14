<template>
  <v-container fluid class="pa-0">
    <v-card flat>
      <v-card-text>
        <v-row>
          <v-col cols="12" class="pb-0">
            <v-card outlined>
              <v-card-title class="d-flex justify-space-between align-center">
                <span class="text-subtitle-1 font-weight-medium">
                  {{ $t('inventory.storageLocations') }}
                </span>
                <div>
                  <v-text-field
                    v-model="searchQuery"
                    :label="$t('common.search')"
                    prepend-icon="mdi-magnify"
                    hide-details
                    density="compact"
                    variant="outlined"
                    class="mr-2"
                    style="max-width: 300px; display: inline-block"
                  ></v-text-field>
                  <v-btn color="primary" @click="refreshData">
                    <v-icon start>mdi-refresh</v-icon>
                    {{ $t('common.refresh') }}
                  </v-btn>
                </div>
              </v-card-title>
              
              <v-data-table
                :headers="headers"
                :items="filteredLocations"
                :loading="inventoryStore.isStorageLocationsLoading"
                :items-per-page="10"
                :footer-props="{
                  'items-per-page-options': [10, 25, 50, 100],
                  showFirstLastPage: true,
                }"
                :no-data-text="$t('common.noResults')"
                :no-results-text="$t('common.noResults')"
                multi-sort
                class="elevation-0"
              >
                <!-- Status column -->
                <template v-slot:item.is_active="{ item }">
                  <v-chip
                    :color="item.is_active ? 'success' : 'error'"
                    size="x-small"
                    label
                  >
                    {{ item.is_active ? $t('common.active') : $t('common.inactive') }}
                  </v-chip>
                </template>
                
                <!-- Sale column -->
                <template v-slot:item.sale="{ item }">
                  <v-icon
                    :color="item.sale ? 'success' : 'grey'"
                    size="small"
                  >
                    {{ item.sale ? 'mdi-check' : 'mdi-minus' }}
                  </v-icon>
                </template>
                
                <!-- Special spot column -->
                <template v-slot:item.special_spot="{ item }">
                  <v-icon
                    :color="item.special_spot ? 'info' : 'grey'"
                    size="small"
                  >
                    {{ item.special_spot ? 'mdi-check' : 'mdi-minus' }}
                  </v-icon>
                </template>
                
                <!-- Products count column -->
                <template v-slot:item.product_count="{ item }">
                  <div class="d-flex align-center">
                    <v-chip
                      color="primary"
                      size="x-small"
                      label
                      class="mr-1"
                    >
                      {{ item.product_count }}
                    </v-chip>
                    <v-tooltip location="bottom">
                      <template v-slot:activator="{ props }">
                        <v-btn 
                          icon 
                          size="x-small" 
                          color="grey-lighten-1" 
                          v-bind="props"
                          @click="refreshProductCount(item)"
                          :loading="refreshingLocationId === item.id"
                        >
                          <v-icon size="x-small">mdi-refresh</v-icon>
                        </v-btn>
                      </template>
                      <span>{{ $t('inventory.refreshProductCount') }}</span>
                    </v-tooltip>
                  </div>
                </template>
                
                <!-- Actions column -->
                <template v-slot:item.actions="{ item }">
                  <v-tooltip location="bottom">
                    <template v-slot:activator="{ props }">
                      <v-btn 
                        icon 
                        size="x-small" 
                        color="primary" 
                        v-bind="props"
                        @click="viewLocationDetails(item)"
                      >
                        <v-icon size="x-small">mdi-eye</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ $t('common.view') }}</span>
                  </v-tooltip>
                  
                  <v-tooltip location="bottom">
                    <template v-slot:activator="{ props }">
                      <v-btn 
                        icon 
                        size="x-small" 
                        color="info" 
                        v-bind="props"
                        @click="viewInventoryAtLocation(item)"
                      >
                        <v-icon size="x-small">mdi-package-variant</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ $t('inventory.viewInventory') }}</span>
                  </v-tooltip>
                </template>
              </v-data-table>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    
    <!-- Location Details Dialog -->
    <v-dialog v-model="locationDialog" max-width="600px">
      <v-card v-if="selectedLocation">
        <v-card-title class="text-h5 primary--text">
          {{ selectedLocation.name }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-barcode</v-icon>
                  </template>
                  <v-list-item-title>{{ $t('inventory.locationCode') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedLocation.location_code || '-' }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-map-marker</v-icon>
                  </template>
                  <v-list-item-title>{{ $t('inventory.location') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ selectedLocation.country }}, {{ selectedLocation.city_building }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-view-grid</v-icon>
                  </template>
                  <v-list-item-title>{{ $t('inventory.position') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ $t('inventory.unit') }}: {{ selectedLocation.unit }}, 
                    {{ $t('inventory.compartment') }}: {{ selectedLocation.compartment }}, 
                    {{ $t('inventory.shelf') }}: {{ selectedLocation.shelf }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-information</v-icon>
                  </template>
                  <v-list-item-title>{{ $t('common.status') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip
                      :color="selectedLocation.is_active ? 'success' : 'error'"
                      size="x-small"
                      label
                    >
                      {{ selectedLocation.is_active ? $t('common.active') : $t('common.inactive') }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-tag</v-icon>
                  </template>
                  <v-list-item-title>{{ $t('inventory.flags') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip
                      :color="selectedLocation.sale ? 'success' : 'grey'"
                      size="x-small"
                      label
                      class="mr-1"
                    >
                      {{ $t('inventory.saleLocation') }}
                    </v-chip>
                    <v-chip
                      :color="selectedLocation.special_spot ? 'warning' : 'grey'"
                      size="x-small"
                      label
                    >
                      {{ $t('inventory.specialSpot') }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item v-if="selectedLocation.description">
                  <template v-slot:prepend>
                    <v-icon>mdi-text</v-icon>
                  </template>
                  <v-list-item-title>{{ $t('common.description') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedLocation.description }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="locationDialog = false">
            {{ $t('common.close') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Products by Location Dialog -->
    <v-dialog v-model="productsDialog" fullscreen hide-overlay transition="dialog-bottom-transition">
      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="closeProductsDialog">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>
            {{ $t('inventory.productsInLocation') }}: {{ selectedLocation ? selectedLocation.name : '' }}
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn dark text @click="refreshProductsData">
              <v-icon start>mdi-refresh</v-icon>
              {{ $t('common.refresh') }}
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>
        
        <v-card-text>
          <v-container fluid>
            <!-- Loading indicator -->
            <v-row v-if="inventoryStore.isProductsByLocationLoading">
              <v-col cols="12" class="text-center">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
                <div class="mt-2">{{ $t('common.loading') }}</div>
              </v-col>
            </v-row>
            
            <!-- Error message -->
            <v-row v-else-if="inventoryStore.getProductsByLocationError">
              <v-col cols="12">
                <v-alert type="error" variant="outlined">
                  {{ inventoryStore.getProductsByLocationError }}
                </v-alert>
              </v-col>
            </v-row>
            
            <!-- No data message -->
            <v-row v-else-if="!inventoryStore.getProductsByLocation.length">
              <v-col cols="12">
                <v-alert type="info" variant="outlined">
                  {{ $t('inventory.noProductsInLocation') }}
                </v-alert>
              </v-col>
            </v-row>
            
            <!-- Products by location data -->
            <template v-else>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="productSearchQuery"
                    :label="$t('inventory.searchProducts')"
                    prepend-icon="mdi-magnify"
                    clearable
                    variant="outlined"
                    density="compact"
                    hide-details
                    class="mb-4"
                  ></v-text-field>
                </v-col>
              </v-row>
              
              <v-row>
                <v-col cols="12">
                  <v-expansion-panels>
                    <v-expansion-panel
                      v-for="box in filteredBoxes"
                      :key="box.box_id"
                    >
                      <v-expansion-panel-title>
                        <div class="d-flex align-center">
                          <v-icon color="primary" class="mr-2">mdi-package-variant-closed</v-icon>
                          <span class="font-weight-medium">{{ $t('inventory.box') }}: {{ box.box_code }}</span>
                          <v-chip class="ml-4" size="small">
                            {{ box.slots.length }} {{ $t('inventory.slots') }}
                          </v-chip>
                          <v-chip class="ml-2" size="small" color="primary" text-color="white">
                            {{ getTotalProductsInBox(box) }} {{ $t('inventory.products') }}
                          </v-chip>
                        </div>
                      </v-expansion-panel-title>
                      <v-expansion-panel-text>
                        <v-data-table
                          :headers="productHeaders"
                          :items="getProductsInBox(box)"
                          :items-per-page="10"
                          :footer-props="{
                            'items-per-page-options': [10, 25, 50, 100],
                            showFirstLastPage: true,
                          }"
                          :no-data-text="$t('common.noResults')"
                          :no-results-text="$t('common.noResults')"
                          multi-sort
                          class="elevation-0"
                        >
                          <template v-slot:item.reservation_status="{ item }">
                            <v-chip
                              :color="getStatusColor(item.reservation_status)"
                              size="x-small"
                              label
                            >
                              {{ item.reservation_status }}
                            </v-chip>
                          </template>
                          
                          <template v-slot:item.date_stored="{ item }">
                            {{ formatDate(item.date_stored) }}
                          </template>
                        </v-data-table>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-col>
              </v-row>
            </template>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useInventoryStore } from '@/store/inventory';
import { useNotificationsStore } from '@/store/notifications';
import { useI18n } from 'vue-i18n';

const inventoryStore = useInventoryStore();
const notificationsStore = useNotificationsStore();
const { t } = useI18n();

// Reactive state
const searchQuery = ref('');
const productSearchQuery = ref('');
const locationDialog = ref(false);
const productsDialog = ref(false);
const selectedLocation = ref(null);
const refreshingLocationId = ref(null); // Track which location is being refreshed

// Table headers
const headers = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Location Code', key: 'location_code', sortable: true },
  { title: 'Country', key: 'country', sortable: true },
  { title: 'City/Building', key: 'city_building', sortable: true },
  { title: 'Unit', key: 'unit', sortable: true },
  { title: 'Compartment', key: 'compartment', sortable: true },
  { title: 'Shelf', key: 'shelf', sortable: true },
  { title: t('inventory.productCount'), key: 'product_count', sortable: true, align: 'center' },
  { title: 'Sale', key: 'sale', sortable: true, align: 'center' },
  { title: 'Special Spot', key: 'special_spot', sortable: true, align: 'center' },
  { title: 'Status', key: 'is_active', sortable: true, align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' }
];

const productHeaders = [
  { title: 'Slot Code', key: 'slot_code', sortable: true },
  { title: 'SKU', key: 'sku', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Quantity', key: 'quantity', sortable: true, align: 'center' },
  { title: 'Reservation Status', key: 'reservation_status', sortable: true, align: 'center' },
  { title: 'Batch Number', key: 'batch_number', sortable: true },
  { title: 'Date Stored', key: 'date_stored', sortable: true }
];

// Computed properties
const locationProductCounts = computed(() => {
  const counts = {};
  
  // Initialize counts for all locations
  inventoryStore.getStorageLocations.forEach(location => {
    counts[location.id] = 0;
  });
  
  // Count products in each location based on boxes
  inventoryStore.getBoxes.forEach(box => {
    if (box.storage_location) {
      const locationId = box.storage_location.id;
      if (!counts[locationId]) {
        counts[locationId] = 0;
      }
      // Increment by 1 for each box in the location
      // This is a simplification - ideally we'd count actual products
      counts[locationId]++;
    }
  });
  
  return counts;
});

const locationsWithProductCount = computed(() => {
  return inventoryStore.getStorageLocations.map(location => {
    return {
      ...location,
      product_count: locationProductCounts.value[location.id] || 0
    };
  });
});

const filteredLocations = computed(() => {
  let locations = locationsWithProductCount.value;
  
  if (!searchQuery.value) {
    return locations;
  }
  
  const query = searchQuery.value.toLowerCase();
  return locations.filter(location => {
    return (
      location.name.toLowerCase().includes(query) ||
      location.location_code?.toLowerCase().includes(query) ||
      location.country.toLowerCase().includes(query) ||
      location.city_building.toLowerCase().includes(query) ||
      location.unit.toLowerCase().includes(query) ||
      location.compartment.toLowerCase().includes(query) ||
      location.shelf.toLowerCase().includes(query)
    );
  });
});

const filteredBoxes = computed(() => {
  if (!productSearchQuery.value) {
    return inventoryStore.getProductsByLocation;
  }
  
  const query = productSearchQuery.value.toLowerCase();
  return inventoryStore.getProductsByLocation.filter(box => {
    // Check if any product in any slot matches the search query
    return box.slots.some(slot => {
      return slot.products.some(product => {
        return (
          product.sku.toLowerCase().includes(query) ||
          product.name.toLowerCase().includes(query) ||
          (product.batch_number && product.batch_number.toLowerCase().includes(query)) ||
          product.reservation_status.toLowerCase().includes(query)
        );
      });
    });
  });
});

// Methods
const fetchData = async () => {
  await inventoryStore.fetchStorageLocations();
  await inventoryStore.fetchBoxes(1, 1000); // Fetch all boxes to get accurate product counts
};

const refreshData = async () => {
  await fetchData();
};

const viewLocationDetails = (location) => {
  selectedLocation.value = location;
  locationDialog.value = true;
};

const viewInventoryAtLocation = async (location) => {
  selectedLocation.value = location;
  productsDialog.value = true;
  await inventoryStore.fetchProductsByLocation(location.id);
};

const closeProductsDialog = () => {
  productsDialog.value = false;
  productSearchQuery.value = '';
  inventoryStore.clearProductsByLocation();
};

const refreshProductsData = () => {
  if (selectedLocation.value) {
    inventoryStore.fetchProductsByLocation(selectedLocation.value.id);
  }
};

const getProductsInBox = (box) => {
  // Flatten products from all slots in the box and add slot_code to each product
  const products = [];
  box.slots.forEach(slot => {
    slot.products.forEach(product => {
      products.push({
        ...product,
        slot_code: slot.slot_code
      });
    });
  });
  return products;
};

const getTotalProductsInBox = (box) => {
  // Count total products in all slots
  let count = 0;
  box.slots.forEach(slot => {
    count += slot.products.length;
  });
  return count;
};

const getStatusColor = (status) => {
  switch (status) {
    case 'AVAILABLE':
      return 'success';
    case 'RESERVED':
      return 'warning';
    case 'ALLOCATED':
      return 'info';
    case 'PICKED':
      return 'error';
    default:
      return 'grey';
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

// Add a method to get a more accurate product count for a specific location
const getAccurateProductCount = async (locationId) => {
  try {
    // Fetch products for this location
    await inventoryStore.fetchProductsByLocation(locationId);
    
    // Count total products across all boxes and slots
    let count = 0;
    inventoryStore.getProductsByLocation.forEach(box => {
      box.slots.forEach(slot => {
        count += slot.products.length;
      });
    });
    
    // Update the product count for this location
    const updatedLocation = locationsWithProductCount.value.find(loc => loc.id === locationId);
    if (updatedLocation) {
      updatedLocation.product_count = count;
    }
    
    // Clear products by location to free memory
    inventoryStore.clearProductsByLocation();
    
    return count;
  } catch (error) {
    console.error(`Error fetching product count for location ${locationId}:`, error);
    return 0;
  }
};

// Add a method to refresh the product count for a specific location
const refreshProductCount = async (location) => {
  refreshingLocationId.value = location.id;
  try {
    const count = await getAccurateProductCount(location.id);
    // Update the UI with the new count
    location.product_count = count;
    notificationsStore.showSuccess(`Product count updated for ${location.name}`);
  } catch (error) {
    notificationsStore.showError(`Failed to update product count: ${error.message}`);
  } finally {
    refreshingLocationId.value = null;
  }
};

// Lifecycle hooks
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.v-data-table :deep(th) {
  font-weight: 600;
  white-space: nowrap;
}

.v-data-table :deep(td) {
  padding: 8px 16px;
}

.v-expansion-panel-title {
  padding: 12px 16px;
}

.v-expansion-panel-text__wrapper {
  padding: 0;
}
</style> 