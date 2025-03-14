<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="6" lg="3">
        <v-card class="mx-auto" outlined>
          <v-list-item>
            <v-list-item-title>
              <div class="text-overline mb-4">{{ $t('inventory.totalBoxes') }}</div>
              <div class="text-h4 mb-1">
                <v-skeleton-loader type="text" width="50%" />
              </div>
              <div class="text-subtitle-1">{{ $t('inventory.boxesDescription') }}</div>
            </v-list-item-title>
            <template v-slot:append>
              <v-avatar size="60" color="primary" class="rounded">
                <v-icon dark>mdi-package-variant-closed</v-icon>
              </v-avatar>
            </template>
          </v-list-item>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" lg="3">
        <v-card class="mx-auto" outlined>
          <v-list-item>
            <v-list-item-title>
              <div class="text-overline mb-4">{{ $t('inventory.totalLocations') }}</div>
              <div class="text-h4 mb-1">
                <v-skeleton-loader type="text" width="50%" />
              </div>
              <div class="text-subtitle-1">{{ $t('inventory.locationsDescription') }}</div>
            </v-list-item-title>
            <template v-slot:append>
              <v-avatar size="60" color="secondary" class="rounded">
                <v-icon dark>mdi-map-marker-multiple</v-icon>
              </v-avatar>
            </template>
          </v-list-item>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" lg="3">
        <v-card class="mx-auto" outlined>
          <v-list-item>
            <v-list-item-title>
              <div class="text-overline mb-4">{{ $t('inventory.totalProducts') }}</div>
              <div class="text-h4 mb-1">
                <v-skeleton-loader type="text" width="50%" />
              </div>
              <div class="text-subtitle-1">{{ $t('inventory.productsDescription') }}</div>
            </v-list-item-title>
            <template v-slot:append>
              <v-avatar size="60" color="success" class="rounded">
                <v-icon dark>mdi-cube-outline</v-icon>
              </v-avatar>
            </template>
          </v-list-item>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" lg="3">
        <v-card class="mx-auto" outlined>
          <v-list-item>
            <v-list-item-title>
              <div class="text-overline mb-4">{{ $t('inventory.recentMovements') }}</div>
              <div class="text-h4 mb-1">
                <v-skeleton-loader type="text" width="50%" />
              </div>
              <div class="text-subtitle-1">{{ $t('inventory.movementsDescription') }}</div>
            </v-list-item-title>
            <template v-slot:append>
              <v-avatar size="60" color="warning" class="rounded">
                <v-icon dark>mdi-swap-horizontal</v-icon>
              </v-avatar>
            </template>
          </v-list-item>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>{{ $t('inventory.inventoryDashboard') }}</v-card-title>
          <v-card-text class="text-center py-5">
            <v-icon size="64" color="grey lighten-1">mdi-view-dashboard-outline</v-icon>
            <h3 class="mt-4">{{ $t('common.comingSoon') }}</h3>
            <p class="text-body-1 mt-2">
              {{ $t('inventory.dashboardDescription') }}
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'InventoryDashboard'
};
</script>

<style scoped>
.rounded {
  border-radius: 12px !important;
}
</style> 