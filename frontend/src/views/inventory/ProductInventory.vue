<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6">
            {{ $t('inventory.productInventory') }}
          </v-card-title>
          
          <v-tabs v-model="activeTab" background-color="secondary" dark>
            <v-tab value="overview">
              {{ $t('inventory.overview') }}
            </v-tab>
            <v-tab value="storage-locations">
              {{ $t('inventory.storageLocations') }}
            </v-tab>
            <v-tab value="movements">
              {{ $t('inventory.productMovements') }}
            </v-tab>
          </v-tabs>
          
          <v-window v-model="activeTab">
            <!-- Overview Tab -->
            <v-window-item value="overview">
              <v-card-text class="text-center py-5">
                <v-icon size="64" color="grey lighten-1">mdi-cube-outline</v-icon>
                <h3 class="mt-4">{{ $t('common.comingSoon') }}</h3>
                <p class="text-body-1 mt-2">
                  {{ $t('inventory.productInventoryDescription') }}
                </p>
              </v-card-text>
            </v-window-item>
            
            <!-- Storage Locations Tab -->
            <v-window-item value="storage-locations">
              <storage-locations-tab />
            </v-window-item>
            
            <!-- Movements Tab -->
            <v-window-item value="movements">
              <v-card-text class="text-center py-5">
                <v-icon size="64" color="grey lighten-1">mdi-swap-horizontal</v-icon>
                <h3 class="mt-4">{{ $t('common.comingSoon') }}</h3>
                <p class="text-body-1 mt-2">
                  {{ $t('inventory.movementsDescription') }}
                </p>
              </v-card-text>
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import StorageLocationsTab from './product/StorageLocationsTab.vue';

export default {
  name: 'ProductInventory',
  components: {
    StorageLocationsTab
  },
  data() {
    return {
      activeTab: 'storage-locations' // Default to storage locations tab
    };
  }
};
</script>

<style scoped>
.v-tab {
  text-transform: none;
  font-weight: 500;
}
</style> 