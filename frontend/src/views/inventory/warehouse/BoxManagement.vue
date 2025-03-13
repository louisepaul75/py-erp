<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h6">
              {{ $t('inventory.boxManagement') }} / {{ $t('inventory.schuettenverwaltung') }}
            </span>
            <v-btn color="primary" @click="refreshData">
              <v-icon left>mdi-refresh</v-icon>
              {{ $t('common.refresh') }}
            </v-btn>
          </v-card-title>

          <v-tabs v-model="activeTab">
            <v-tab value="boxes">{{ $t('inventory.boxes') }}</v-tab>
            <v-tab value="boxTypes">{{ $t('inventory.boxTypes') }}</v-tab>
          </v-tabs>

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
                
                <v-data-table
                  :headers="boxHeaders"
                  :items="inventoryStore.getBoxes"
                  :loading="inventoryStore.isBoxesLoading"
                  :items-per-page="inventoryStore.getBoxesPagination.pageSize"
                  :page="inventoryStore.getBoxesPagination.page"
                  :server-items-length="inventoryStore.getBoxesPagination.total"
                  @update:page="handlePageChange"
                  @update:items-per-page="handlePageSizeChange"
                  class="elevation-1"
                >
                  <!-- Status column -->
                  <template v-slot:item.status="{ item }">
                    <v-chip
                      :color="getStatusColor(item.status)"
                      small
                    >
                      {{ item.status }}
                    </v-chip>
                  </template>

                  <!-- Purpose column -->
                  <template v-slot:item.purpose="{ item }">
                    <v-chip
                      :color="getPurposeColor(item.purpose)"
                      small
                    >
                      {{ item.purpose }}
                    </v-chip>
                  </template>

                  <!-- Storage Location column -->
                  <template v-slot:item.storage_location="{ item }">
                    <span v-if="item.storage_location">{{ item.storage_location.name }}</span>
                    <span v-else class="text-caption">{{ $t('inventory.noLocation') }}</span>
                  </template>

                  <!-- Actions column -->
                  <template v-slot:item.actions="{ item }">
                    <v-btn icon small color="primary" @click="viewBox(item)">
                      <v-icon small>mdi-eye</v-icon>
                    </v-btn>
                    <v-btn icon small color="secondary" @click="editBox(item)">
                      <v-icon small>mdi-pencil</v-icon>
                    </v-btn>
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
                      {{ selectedBox.status }}
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
                      {{ selectedBox.purpose }}
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
                  <v-list-item-subtitle>{{ selectedBox.available_slots }}</v-list-item-subtitle>
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
      boxTypeHeaders: [
        { text: this.$t('inventory.name'), value: 'name', sortable: true },
        { text: this.$t('inventory.dimensions'), value: 'dimensions', sortable: false },
        { text: this.$t('inventory.weightCapacity'), value: 'weight_capacity', sortable: true },
        { text: this.$t('inventory.slotCount'), value: 'slot_count', sortable: true },
        { text: this.$t('common.actions'), value: 'actions', sortable: false, align: 'center' }
      ],
      boxHeaders: [
        { text: this.$t('inventory.code'), value: 'code', sortable: true },
        { text: this.$t('inventory.boxType'), value: 'box_type.name', sortable: true },
        { text: this.$t('inventory.location'), value: 'storage_location', sortable: true },
        { text: this.$t('inventory.status'), value: 'status', sortable: true },
        { text: this.$t('inventory.purpose'), value: 'purpose', sortable: true },
        { text: this.$t('inventory.availableSlots'), value: 'available_slots', sortable: true },
        { text: this.$t('common.actions'), value: 'actions', sortable: false, align: 'center' }
      ],
      detailDialog: false,
      selectedBoxType: null as BoxType | null,
      boxDetailDialog: false,
      selectedBox: null as Box | null
    };
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
      const colors = {
        AVAILABLE: 'success',
        IN_USE: 'primary',
        RESERVED: 'warning',
        DAMAGED: 'error',
        RETIRED: 'grey'
      };
      return colors[status as keyof typeof colors] || 'grey';
    },
    getPurposeColor(purpose: string): string {
      const colors = {
        STORAGE: 'blue',
        PICKING: 'green',
        TRANSPORT: 'orange',
        WORKSHOP: 'purple'
      };
      return colors[purpose as keyof typeof colors] || 'grey';
    }
  }
});
</script>

<style scoped>
.v-data-table ::v-deep th {
  font-weight: bold !important;
}
</style> 