<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <!-- Simple header with tabs and refresh -->
          <v-card-title class="d-flex justify-space-between align-center px-4">
            <div class="d-flex align-center">
              <v-tabs v-model="activeTab">
                <v-tab value="boxes" class="text-none">
                  <v-icon left>mdi-package-variant</v-icon>
                  {{ $t('inventory.boxes') }}
                </v-tab>
                <v-tab value="boxTypes" class="text-none">
                  <v-icon left>mdi-package-variant-closed</v-icon>
                  {{ $t('inventory.boxTypes') }}
                </v-tab>
              </v-tabs>
            </div>
            <v-btn color="primary" @click="refreshData" class="ml-4">
              <v-icon left>mdi-refresh</v-icon>
              {{ $t('common.refresh') }}
            </v-btn>
          </v-card-title>

          <v-divider />

          <v-card-text>
            <!-- Box Types Tab -->
            <v-window v-model="activeTab">
              <v-window-item value="boxes">
                <v-alert
                  v-if="inventoryStore.getBoxesError"
                  type="error"
                  class="mb-4"
                  dismissible
                >
                  {{ inventoryStore.getBoxesError }}
                </v-alert>
                
                <!-- Search and filter controls -->
                <v-card class="mb-4">
                  <v-card-text class="py-2">
                    <v-row align="center">
                      <v-col cols="12" sm="4">
                        <v-text-field
                          v-model="searchQuery"
                          :label="$t('common.search')"
                          prepend-icon="mdi-magnify"
                          hide-details
                          clearable
                          @input="handleSearch"
                          dense
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12" sm="3">
                        <v-select
                          v-model="statusFilter"
                          :items="statusOptions"
                          :label="$t('inventory.status')"
                          prepend-icon="mdi-filter-variant"
                          hide-details
                          clearable
                          @change="handleFilterChange"
                          dense
                        ></v-select>
                      </v-col>
                      <v-col cols="12" sm="3">
                        <v-select
                          v-model="purposeFilter"
                          :items="purposeOptions"
                          :label="$t('inventory.purpose')"
                          prepend-icon="mdi-filter-variant"
                          hide-details
                          clearable
                          @change="handleFilterChange"
                          dense
                        ></v-select>
                      </v-col>
                      <v-col cols="12" sm="2" class="d-flex justify-end">
                        <v-btn 
                          color="primary" 
                          text 
                          @click="resetFilters"
                          :disabled="!hasActiveFilters"
                        >
                          <v-icon left>mdi-filter-remove</v-icon>
                          {{ $t('common.reset') }}
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
                
                <v-data-table
                  :headers="boxHeaders"
                  :items="filteredBoxes"
                  :loading="inventoryStore.isBoxesLoading"
                  :items-per-page="inventoryStore.getBoxesPagination.pageSize"
                  :page="inventoryStore.getBoxesPagination.page"
                  :server-items-length="inventoryStore.getBoxesPagination.total"
                  :footer-props="{
                    'items-per-page-options': [10, 25, 50, 100],
                    showFirstLastPage: true,
                  }"
                  :no-data-text="$t('common.noResults')"
                  :no-results-text="$t('common.noResults')"
                  multi-sort
                  @update:page="handlePageChange"
                  @update:items-per-page="handlePageSizeChange"
                  @update:sort-by="handleSortChange"
                  class="elevation-2"
                  fixed-header
                  hide-default-header
                >
                  <template v-slot:header>
                    <thead class="v-data-table-header">
                      <tr>
                        <th class="text-left">{{ $t('inventory.boxCode') }}</th>
                        <th class="text-left">{{ $t('inventory.boxType') }}</th>
                        <th class="text-left">{{ $t('inventory.storageLocation') }}</th>
                        <th class="text-center">{{ $t('inventory.status') }}</th>
                        <th class="text-center">{{ $t('inventory.purpose') }}</th>
                        <th class="text-center">{{ $t('inventory.availableSlots') }}</th>
                        <th class="text-center">{{ $t('common.actions') }}</th>
                      </tr>
                    </thead>
                  </template>
                  
                  <template v-slot:top>
                    <v-toolbar flat class="mb-1">
                      <v-toolbar-title class="text-subtitle-1 font-weight-bold">{{ $t('inventory.boxes') }}</v-toolbar-title>
                      <v-spacer></v-spacer>
                      <v-btn color="primary" x-small class="mr-2">
                        <v-icon small left>mdi-plus</v-icon>
                        {{ $t('common.create') }}
                      </v-btn>
                      <v-btn color="secondary" x-small>
                        <v-icon small left>mdi-export-variant</v-icon>
                        {{ $t('common.export') }}
                      </v-btn>
                    </v-toolbar>
                  </template>
                  
                  <!-- Status column -->
                  <template v-slot:item.status="{ item }">
                    <v-chip
                      :color="getStatusColor(item.status)"
                      x-small
                      label
                      class="text-capitalize"
                    >
                      {{ $t(`inventory.status.${item.status.toLowerCase()}`) }}
                    </v-chip>
                  </template>

                  <!-- Purpose column -->
                  <template v-slot:item.purpose="{ item }">
                    <v-chip
                      :color="getPurposeColor(item.purpose)"
                      x-small
                      label
                      class="text-capitalize"
                    >
                      {{ $t(`inventory.purpose.${item.purpose.toLowerCase()}`) }}
                    </v-chip>
                  </template>

                  <!-- Storage Location column -->
                  <template v-slot:item.storage_location="{ item }">
                    <span v-if="item.storage_location">{{ item.storage_location.name }}</span>
                    <span v-else class="text-caption grey--text">{{ $t('inventory.noLocation') }}</span>
                  </template>

                  <!-- Available Slots column -->
                  <template v-slot:item.available_slots="{ item }">
                    <v-chip
                      :color="item.available_slots > 0 ? 'success' : 'error'"
                      x-small
                      label
                      outlined
                    >
                      {{ item.available_slots }}
                    </v-chip>
                  </template>

                  <!-- Actions column -->
                  <template v-slot:item.actions="{ item }">
                    <div class="d-flex justify-center">
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-btn
                            icon
                            x-small
                            color="primary"
                            class="mr-1"
                            v-bind="attrs"
                            v-on="{ ...on }"
                            @click="viewBox(item)"
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
                            color="secondary"
                            v-bind="attrs"
                            v-on="{ ...on }"
                            @click="editBox(item)"
                          >
                            <v-icon x-small>mdi-pencil</v-icon>
                          </v-btn>
                        </template>
                        <span>{{ $t('common.edit') }}</span>
                      </v-tooltip>
                    </div>
                  </template>
                </v-data-table>
              </v-window-item>

              <v-window-item value="boxTypes">
                <v-alert
                  v-if="inventoryStore.getBoxTypesError"
                  type="error"
                  class="mb-4"
                  dismissible
                >
                  {{ inventoryStore.getBoxTypesError }}
                </v-alert>
                
                <v-data-table
                  :headers="boxTypeHeaders"
                  :items="inventoryStore.getBoxTypes"
                  :loading="inventoryStore.isBoxTypesLoading"
                  :items-per-page="10"
                  :footer-props="{
                    'items-per-page-options': [10, 25, 50, 100],
                  }"
                  class="elevation-1"
                >
                  <!-- Dimensions column -->
                  <template v-slot:item.dimensions="{ item }">
                    {{ formatDimensions(item) }}
                  </template>
                  
                  <!-- Weight capacity column -->
                  <template v-slot:item.weight_capacity="{ item }">
                    <span v-if="item.weight_capacity">{{ item.weight_capacity }} kg</span>
                    <span v-else>-</span>
                  </template>
                  
                  <!-- Actions column -->
                  <template v-slot:item.actions="{ item }">
                    <v-btn icon small color="primary" @click="viewBoxType(item)">
                      <v-icon small>mdi-eye</v-icon>
                    </v-btn>
                    <v-btn icon small color="secondary" @click="editBoxType(item)">
                      <v-icon small>mdi-pencil</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Box Type Detail Dialog -->
    <v-dialog v-model="detailDialog" max-width="600px">
      <v-card v-if="selectedBoxType">
        <v-card-title class="text-h5 primary--text">
          {{ selectedBoxType.name }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <p class="text-body-1">{{ selectedBoxType.description || $t('common.noDescription') }}</p>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-ruler</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.dimensions') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDimensions(selectedBoxType) }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-weight</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.weightCapacity') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ selectedBoxType.weight_capacity ? `${selectedBoxType.weight_capacity} kg` : '-' }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-grid</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.slotCount') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedBoxType.slot_count }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-format-list-numbered</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.slotNamingScheme') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedBoxType.slot_naming_scheme }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="detailDialog = false">
            {{ $t('common.close') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Box Detail Dialog -->
    <v-dialog v-model="boxDetailDialog" max-width="600px">
      <v-card v-if="selectedBox">
        <v-card-title class="text-h5 primary--text">
          {{ selectedBox.code }}
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <p class="text-body-1">{{ selectedBox.notes || $t('common.noNotes') }}</p>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-package-variant</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.boxType') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedBox.box_type.name }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-map-marker</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.location') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ selectedBox.storage_location ? selectedBox.storage_location.name : $t('inventory.noLocation') }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-information</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.status') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip :color="getStatusColor(selectedBox.status)" small>
                      {{ $t(`inventory.status.${selectedBox.status.toLowerCase()}`) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-flag</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.purpose') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip :color="getPurposeColor(selectedBox.purpose)" small>
                      {{ $t(`inventory.purpose.${selectedBox.purpose.toLowerCase()}`) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-grid</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.availableSlots') }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip
                      :color="selectedBox.available_slots > 0 ? 'success' : 'error'"
                      small
                      label
                      outlined
                    >
                      {{ selectedBox.available_slots }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
            <v-col cols="6">
              <v-list-item>
                <v-list-item-icon>
                  <v-icon>mdi-barcode</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ $t('inventory.barcode') }}</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedBox.barcode || '-' }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="boxDetailDialog = false">
            {{ $t('common.close') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useInventoryStore } from '@/store/inventory';
import type { BoxType, Box } from '@/services/inventory';

export default defineComponent({
  name: 'BoxManagement',
  setup() {
    const inventoryStore = useInventoryStore();
    return { inventoryStore };
  },
  data() {
    return {
      activeTab: 'boxes',
      searchQuery: '',
      statusFilter: null,
      purposeFilter: null,
      sortBy: ['code'],
      sortDesc: [false],
      boxTypeHeaders: [
        { text: this.$t('inventory.name'), value: 'name', sortable: true },
        { text: this.$t('inventory.dimensions'), value: 'dimensions', sortable: false },
        { text: this.$t('inventory.weightCapacity'), value: 'weight_capacity', sortable: true },
        { text: this.$t('inventory.slotCount'), value: 'slot_count', sortable: true },
        { text: this.$t('common.actions'), value: 'actions', sortable: false, align: 'center' }
      ],
      boxHeaders: [
        { 
          text: this.$t('inventory.boxCode'),
          value: 'code',
          sortable: true,
          align: 'start',
          width: '120'
        },
        { 
          text: this.$t('inventory.boxType'),
          value: 'box_type.name',
          sortable: true,
          width: '200'
        },
        { 
          text: this.$t('inventory.storageLocation'),
          value: 'storage_location',
          sortable: true,
          width: '200'
        },
        { 
          text: this.$t('inventory.status'),
          value: 'status',
          sortable: true,
          align: 'center',
          width: '120'
        },
        { 
          text: this.$t('inventory.purpose'),
          value: 'purpose',
          sortable: true,
          align: 'center',
          width: '120'
        },
        { 
          text: this.$t('inventory.availableSlots'),
          value: 'available_slots',
          sortable: true,
          align: 'center',
          width: '100'
        },
        { 
          text: this.$t('common.actions'),
          value: 'actions',
          sortable: false,
          align: 'center',
          width: '120',
          filterable: false
        }
      ],
      detailDialog: false,
      selectedBoxType: null as BoxType | null,
      boxDetailDialog: false,
      selectedBox: null as Box | null
    };
  },
  computed: {
    statusOptions() {
      return [
        { text: this.$t('inventory.status.available'), value: 'AVAILABLE' },
        { text: this.$t('inventory.status.in_use'), value: 'IN_USE' },
        { text: this.$t('inventory.status.reserved'), value: 'RESERVED' },
        { text: this.$t('inventory.status.damaged'), value: 'DAMAGED' },
        { text: this.$t('inventory.status.retired'), value: 'RETIRED' }
      ];
    },
    purposeOptions() {
      return [
        { text: this.$t('inventory.purpose.storage'), value: 'STORAGE' },
        { text: this.$t('inventory.purpose.picking'), value: 'PICKING' },
        { text: this.$t('inventory.purpose.transport'), value: 'TRANSPORT' },
        { text: this.$t('inventory.purpose.workshop'), value: 'WORKSHOP' }
      ];
    },
    filteredBoxes() {
      if (!this.searchQuery && !this.statusFilter && !this.purposeFilter) {
        return this.inventoryStore.getBoxes;
      }
      
      return this.inventoryStore.getBoxes.filter(box => {
        // Filter by search query
        const matchesSearch = !this.searchQuery || 
          box.code.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          box.box_type.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (box.storage_location && box.storage_location.name.toLowerCase().includes(this.searchQuery.toLowerCase()));
        
        // Filter by status
        const matchesStatus = !this.statusFilter || box.status === this.statusFilter;
        
        // Filter by purpose
        const matchesPurpose = !this.purposeFilter || box.purpose === this.purposeFilter;
        
        return matchesSearch && matchesStatus && matchesPurpose;
      });
    },
    hasActiveFilters() {
      return this.searchQuery || this.statusFilter || this.purposeFilter;
    }
  },
  created() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      await Promise.all([
        this.inventoryStore.fetchBoxTypes(),
        this.inventoryStore.fetchBoxes()
      ]);
    },
    handlePageChange(page: number) {
      this.inventoryStore.fetchBoxes(page);
    },
    handlePageSizeChange(pageSize: number) {
      this.inventoryStore.fetchBoxes(1, pageSize);
    },
    formatDimensions(item: BoxType) {
      if (!item.length || !item.width || !item.height) {
        return '-';
      }
      return `${item.length} × ${item.width} × ${item.height} cm`;
    },
    refreshData() {
      this.fetchData();
    },
    viewBoxType(item: BoxType) {
      this.selectedBoxType = item;
      this.detailDialog = true;
    },
    editBoxType(item: BoxType) {
      // This would be implemented in a future update
      console.log('Edit box type:', item);
      console.info(this.$t('common.featureNotImplemented'));
    },
    viewBox(item: Box) {
      this.selectedBox = item;
      this.boxDetailDialog = true;
    },
    editBox(item: Box) {
      // This would be implemented in a future update
      console.log('Edit box:', item);
      console.info(this.$t('common.featureNotImplemented'));
    },
    getStatusColor(status: string): string {
      const statusMap = {
        AVAILABLE: { color: 'success', text: this.$t('inventory.status.available') },
        IN_USE: { color: 'primary', text: this.$t('inventory.status.in_use') },
        RESERVED: { color: 'warning', text: this.$t('inventory.status.reserved') },
        DAMAGED: { color: 'error', text: this.$t('inventory.status.damaged') },
        RETIRED: { color: 'grey', text: this.$t('inventory.status.retired') }
      };
      return statusMap[status as keyof typeof statusMap]?.color || 'grey';
    },
    getPurposeColor(purpose: string): string {
      const purposeMap = {
        STORAGE: { color: 'blue', text: this.$t('inventory.purpose.storage') },
        PICKING: { color: 'green', text: this.$t('inventory.purpose.picking') },
        TRANSPORT: { color: 'orange', text: this.$t('inventory.purpose.transport') },
        WORKSHOP: { color: 'purple', text: this.$t('inventory.purpose.workshop') }
      };
      return purposeMap[purpose as keyof typeof purposeMap]?.color || 'grey';
    },
    handleSearch() {
      // Client-side filtering is handled by the computed property
      // For server-side, you would call the API with search params
    },
    handleFilterChange() {
      // Client-side filtering is handled by the computed property
      // For server-side, you would call the API with filter params
    },
    resetFilters() {
      this.searchQuery = '';
      this.statusFilter = null;
      this.purposeFilter = null;
    },
    handleSortChange(sortBy: string[]) {
      this.sortBy = sortBy;
      // For server-side sorting, you would call the API with sort params
    }
  }
});
</script>

<style scoped>
.v-data-table {
  border-radius: 4px;
}

.v-data-table-header th {
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  white-space: nowrap;
  background-color: #f5f5f5;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  height: 48px !important;
  color: rgba(0, 0, 0, 0.8) !important;
  padding: 0 16px !important;
  border-bottom: thin solid rgba(0, 0, 0, 0.12);
}

.v-data-table ::v-deep td {
  height: 40px !important;
  border-bottom: thin solid rgba(0, 0, 0, 0.12);
  font-size: 0.875rem !important;
}

.v-chip {
  font-weight: 500 !important;
}

.v-chip.v-size--x-small {
  height: 20px;
  font-size: 0.75rem !important;
}

.v-toolbar {
  border-bottom: thin solid rgba(0, 0, 0, 0.12);
}

.v-btn--icon.v-size--x-small {
  width: 20px;
  height: 20px;
}

.v-btn--icon.v-size--x-small .v-icon {
  font-size: 16px;
}
</style> 