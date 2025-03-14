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
                    dense
                    outlined
                    class="mr-2"
                    style="max-width: 300px; display: inline-block"
                  ></v-text-field>
                  <v-btn color="primary" @click="refreshData">
                    <v-icon left>mdi-refresh</v-icon>
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
                    x-small
                    label
                  >
                    {{ item.is_active ? $t('common.active') : $t('common.inactive') }}
                  </v-chip>
                </template>
                
                <!-- Sale column -->
                <template v-slot:item.sale="{ item }">
                  <v-icon
                    :color="item.sale ? 'success' : 'grey'"
                    small
                  >
                    {{ item.sale ? 'mdi-check-circle' : 'mdi-cancel' }}
                  </v-icon>
                </template>
                
                <!-- Special spot column -->
                <template v-slot:item.special_spot="{ item }">
                  <v-icon
                    :color="item.special_spot ? 'warning' : 'grey'"
                    small
                  >
                    {{ item.special_spot ? 'mdi-star' : 'mdi-star-outline' }}
                  </v-icon>
                </template>
                
                <!-- Actions column -->
                <template v-slot:item.actions="{ item }">
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn 
                        icon 
                        x-small 
                        color="primary" 
                        v-bind="attrs"
                        v-on="on"
                        @click="viewLocationDetails(item)"
                      >
                        <v-icon x-small>mdi-eye</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ $t('common.view') }}</span>
                  </v-tooltip>
                  
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn 
                        icon 
                        x-small 
                        color="info" 
                        v-bind="attrs"
                        v-on="on"
                        @click="viewInventoryAtLocation(item)"
                      >
                        <v-icon x-small>mdi-package-variant</v-icon>
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
              <v-list dense>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-barcode</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ $t('inventory.locationCode') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedLocation.location_code || '-' }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-map-marker</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ $t('inventory.location') }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ selectedLocation.country }}, {{ selectedLocation.city_building }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-view-grid</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ $t('inventory.position') }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ $t('inventory.unit') }}: {{ selectedLocation.unit }}, 
                      {{ $t('inventory.compartment') }}: {{ selectedLocation.compartment }}, 
                      {{ $t('inventory.shelf') }}: {{ selectedLocation.shelf }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-information</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ $t('common.status') }}</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip
                        :color="selectedLocation.is_active ? 'success' : 'error'"
                        x-small
                        label
                      >
                        {{ selectedLocation.is_active ? $t('common.active') : $t('common.inactive') }}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-tag</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ $t('inventory.flags') }}</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip
                        :color="selectedLocation.sale ? 'success' : 'grey'"
                        x-small
                        label
                        class="mr-1"
                      >
                        {{ $t('inventory.saleLocation') }}
                      </v-chip>
                      <v-chip
                        :color="selectedLocation.special_spot ? 'warning' : 'grey'"
                        x-small
                        label
                      >
                        {{ $t('inventory.specialSpot') }}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item v-if="selectedLocation.description">
                  <v-list-item-icon>
                    <v-icon>mdi-text</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ $t('common.description') }}</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedLocation.description }}</v-list-item-subtitle>
                  </v-list-item-content>
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
  </v-container>
</template>

<script>
import { defineComponent } from 'vue';
import { useInventoryStore } from '@/store/inventory';
import { useNotificationsStore } from '@/store/notifications';

export default defineComponent({
  name: 'StorageLocationsTab',
  setup() {
    const inventoryStore = useInventoryStore();
    const notificationsStore = useNotificationsStore();
    return { inventoryStore, notificationsStore };
  },
  data() {
    return {
      searchQuery: '',
      locationDialog: false,
      selectedLocation: null,
      headers: [
        { text: this.$t('inventory.name'), value: 'name', sortable: true },
        { text: this.$t('inventory.locationCode'), value: 'location_code', sortable: true },
        { text: this.$t('inventory.country'), value: 'country', sortable: true },
        { text: this.$t('inventory.cityBuilding'), value: 'city_building', sortable: true },
        { text: this.$t('inventory.unit'), value: 'unit', sortable: true },
        { text: this.$t('inventory.compartment'), value: 'compartment', sortable: true },
        { text: this.$t('inventory.shelf'), value: 'shelf', sortable: true },
        { text: this.$t('inventory.sale'), value: 'sale', sortable: true, align: 'center' },
        { text: this.$t('inventory.specialSpot'), value: 'special_spot', sortable: true, align: 'center' },
        { text: this.$t('common.status'), value: 'is_active', sortable: true, align: 'center' },
        { text: this.$t('common.actions'), value: 'actions', sortable: false, align: 'center' }
      ]
    };
  },
  computed: {
    filteredLocations() {
      if (!this.searchQuery) {
        return this.inventoryStore.getStorageLocations;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.inventoryStore.getStorageLocations.filter(location => {
        return (
          location.name.toLowerCase().includes(query) ||
          location.location_code.toLowerCase().includes(query) ||
          location.country.toLowerCase().includes(query) ||
          location.city_building.toLowerCase().includes(query) ||
          location.unit.toLowerCase().includes(query) ||
          location.compartment.toLowerCase().includes(query) ||
          location.shelf.toLowerCase().includes(query)
        );
      });
    }
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.inventoryStore.fetchStorageLocations();
    },
    refreshData() {
      this.fetchData();
    },
    viewLocationDetails(location) {
      this.selectedLocation = location;
      this.locationDialog = true;
    },
    viewInventoryAtLocation(location) {
      // This would be implemented in a future update to show products at this location
      console.log('View inventory at location:', location);
      this.notificationsStore.addNotification({
        type: 'info',
        message: this.$t('common.featureNotImplemented')
      });
    }
  }
});
</script>

<style scoped>
.v-data-table ::v-deep th {
  font-weight: bold !important;
}
</style> 