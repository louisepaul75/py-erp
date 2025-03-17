<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 py-4 primary--text">
            {{ $t('inventory.title') }}
          </v-card-title>
          <v-tabs v-model="activeTab" background-color="primary" dark>
            <v-tab :to="{ name: 'InventoryDashboard' }">
              {{ $t('inventory.dashboard') }}
            </v-tab>
            <v-tab :to="{ name: 'WarehouseManagement' }">
              {{ $t('inventory.warehouseManagement') }}
            </v-tab>
            <v-tab :to="{ name: 'ProductInventory' }">
              {{ $t('inventory.productInventory') }}
            </v-tab>
            <v-tab :to="{ name: 'InventoryMovements' }">
              {{ $t('inventory.movements') }}
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
  name: 'InventoryBase',
  data() {
    return {
      activeTab: null
    };
  },
  created() {
    // Set the active tab based on the current route
    const currentRoute = this.$route.name;
    if (currentRoute === 'InventoryDashboard') {
      this.activeTab = 0;
    } else if (currentRoute === 'WarehouseManagement') {
      this.activeTab = 1;
    } else if (currentRoute === 'ProductInventory') {
      this.activeTab = 2;
    } else if (currentRoute === 'InventoryMovements') {
      this.activeTab = 3;
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