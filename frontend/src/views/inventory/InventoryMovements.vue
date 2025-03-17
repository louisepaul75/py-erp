<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6">
            {{ $t('inventory.movements') }}
          </v-card-title>
          <v-card-text class="text-center py-5">
            <v-icon size="64" color="grey lighten-1">mdi-swap-horizontal</v-icon>
            <h3 class="mt-4">{{ $t('common.comingSoon') }}</h3>
            <p class="text-body-1 mt-2">
              {{ $t('inventory.movementsPageDescription') }}
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'InventoryMovements'
};
</script>

<style scoped>
</style> 