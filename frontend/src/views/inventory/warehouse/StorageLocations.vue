<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h6">
              {{ $t('inventory.storageLocations') }}
            </span>
            <v-btn color="primary" @click="refreshData">
              <v-icon left>mdi-refresh</v-icon>
              {{ $t('common.refresh') }}
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="locations"
              :loading="loading"
              :items-per-page="10"
              :footer-props="{
                'items-per-page-options': [10, 25, 50, 100],
              }"
              class="elevation-1"
            >
              <!-- Status column -->
              <template v-slot:item.is_active="{ item }">
                <v-chip
                  :color="item.is_active ? 'success' : 'error'"
                  small
                  label
                >
                  {{ item.is_active ? $t('common.active') : $t('common.inactive') }}
                </v-chip>
              </template>
              
              <!-- Actions column -->
              <template v-slot:item.actions="{ item }">
                <v-btn icon small color="primary" @click="viewLocation(item)">
                  <v-icon small>mdi-eye</v-icon>
                </v-btn>
                <v-btn icon small color="secondary" @click="editLocation(item)">
                  <v-icon small>mdi-pencil</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import api from '@/services/api';
import { useAuthStore } from '@/store/auth';
import { useNotificationsStore } from '@/store/notifications';

export default {
  name: 'StorageLocations',
  setup() {
    const authStore = useAuthStore();
    const notificationsStore = useNotificationsStore();
    return { authStore, notificationsStore };
  },
  data() {
    return {
      locations: [],
      loading: false,
      headers: [
        { text: this.$t('inventory.name'), value: 'name', sortable: true },
        { text: this.$t('inventory.locationCode'), value: 'location_code', sortable: true },
        { text: this.$t('inventory.country'), value: 'country', sortable: true },
        { text: this.$t('inventory.cityBuilding'), value: 'city_building', sortable: true },
        { text: this.$t('common.status'), value: 'is_active', sortable: true },
        { text: this.$t('common.actions'), value: 'actions', sortable: false, align: 'center' }
      ]
    };
  },
  created() {
    // Ensure auth is initialized before fetching data
    if (this.authStore.initialized) {
      this.fetchLocations();
    } else {
      this.authStore.init().then(() => {
        this.fetchLocations();
      });
    }
  },
  methods: {
    async fetchLocations() {
      this.loading = true;
      try {
        const response = await api.get('/inventory/storage-locations/');
        this.locations = response.data;
      } catch (error) {
        console.error('Error fetching storage locations:', error);
        this.notificationsStore.addNotification({
          type: 'error',
          message: this.$t('inventory.errorFetchingLocations')
        });
      } finally {
        this.loading = false;
      }
    },
    refreshData() {
      this.fetchLocations();
    },
    viewLocation(item) {
      // This would be implemented in a future update
      console.log('View location:', item);
      this.notificationsStore.addNotification({
        type: 'info',
        message: this.$t('common.featureNotImplemented')
      });
    },
    editLocation(item) {
      // This would be implemented in a future update
      console.log('Edit location:', item);
      this.notificationsStore.addNotification({
        type: 'info',
        message: this.$t('common.featureNotImplemented')
      });
    }
  }
};
</script>

<style scoped>
.v-data-table ::v-deep th {
  font-weight: bold !important;
}
</style> 