<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5 py-3">
            {{ $t('inventory.warehouseManagement') }} / {{ $t('inventory.lagerverwaltung') }}
          </v-card-title>
          <v-tabs v-model="activeTab" background-color="secondary" dark>
            <v-tab :to="{ name: 'StorageLocations' }">
              {{ $t('inventory.storageLocations') }}
            </v-tab>
            <v-tab :to="{ name: 'BoxManagement' }">
              {{ $t('inventory.boxManagement') }} / {{ $t('inventory.schuettenverwaltung') }}
            </v-tab>
            <v-tab :to="{ name: 'WarehouseMap' }">
              {{ $t('inventory.warehouseMap') }}
            </v-tab>
          </v-tabs>
          <v-card-text class="pa-0">
            <router-view></router-view>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'WarehouseManagement',
  data() {
    return {
      activeTab: null
    };
  },
  created() {
    // Set the active tab based on the current route
    const currentRoute = this.$route.name;
    if (currentRoute === 'StorageLocations') {
      this.activeTab = 0;
    } else if (currentRoute === 'BoxManagement') {
      this.activeTab = 1;
    } else if (currentRoute === 'WarehouseMap') {
      this.activeTab = 2;
    }
  }
};
</script>

<style scoped>
.v-tab {
  text-transform: none;
  font-weight: 500;
}
</style> 