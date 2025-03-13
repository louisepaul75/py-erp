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
          <v-card-text>
            <v-alert
              v-if="inventoryStore.getBoxTypesError"
              type="error"
              class="mb-4"
              dismissible
            >
              {{ inventoryStore.getBoxTypesError }}
            </v-alert>
            
            <v-data-table
              :headers="headers"
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
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useInventoryStore } from '@/store/inventory';
import type { BoxType } from '@/services/inventory';

export default defineComponent({
  name: 'BoxManagement',
  setup() {
    const inventoryStore = useInventoryStore();
    return { inventoryStore };
  },
  data() {
    return {
      headers: [
        { text: this.$t('inventory.name'), value: 'name', sortable: true },
        { text: this.$t('inventory.dimensions'), value: 'dimensions', sortable: false },
        { text: this.$t('inventory.weightCapacity'), value: 'weight_capacity', sortable: true },
        { text: this.$t('inventory.slotCount'), value: 'slot_count', sortable: true },
        { text: this.$t('common.actions'), value: 'actions', sortable: false, align: 'center' }
      ],
      detailDialog: false,
      selectedBoxType: null as BoxType | null
    };
  },
  created() {
    this.fetchBoxTypes();
  },
  methods: {
    async fetchBoxTypes() {
      await this.inventoryStore.fetchBoxTypes();
    },
    formatDimensions(item: BoxType) {
      if (!item.length || !item.width || !item.height) {
        return '-';
      }
      return `${item.length} × ${item.width} × ${item.height} cm`;
    },
    refreshData() {
      this.fetchBoxTypes();
    },
    viewBoxType(item: BoxType) {
      this.selectedBoxType = item;
      this.detailDialog = true;
    },
    editBoxType(item: BoxType) {
      // This would be implemented in a future update
      console.log('Edit box type:', item);
      console.info(this.$t('common.featureNotImplemented'));
    }
  }
});
</script>

<style scoped>
.v-data-table ::v-deep th {
  font-weight: bold !important;
}
</style> 