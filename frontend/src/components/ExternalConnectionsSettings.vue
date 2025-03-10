<template>
  <v-card flat>
    <div class="px-6 py-4 border-b">
      <span class="text-h6 font-weight-medium">External Connections</span>
    </div>
    <v-card-text>
      <v-alert
        v-if="error"
        type="error"
        class="mb-4"
        density="comfortable"
        closable
      >
        {{ error }}
      </v-alert>
      
      <v-alert
        v-if="successMessage"
        type="success"
        class="mb-4"
        density="comfortable"
        closable
      >
        {{ successMessage }}
      </v-alert>

      <v-skeleton-loader
        v-if="loading"
        type="list-item-three-line"
        class="mb-4"
      ></v-skeleton-loader>
      
      <div v-else>
        <p class="text-body-2 text-grey-darken-1 mb-4">
          Toggle external connections to enable or disable external system integrations for this instance.
          These settings are stored in a local configuration file specific to this installation.
        </p>
        
        <v-list>
          <v-list-item v-for="(enabled, name) in connections" :key="name" class="mb-1 rounded">
            <template v-slot:prepend>
              <v-icon :color="enabled ? 'success' : 'grey'">
                {{ enabled ? 'mdi-connection' : 'mdi-connection-off' }}
              </v-icon>
            </template>
            
            <v-list-item-title class="font-weight-medium">
              {{ formatConnectionName(name) }}
            </v-list-item-title>
            
            <v-list-item-subtitle class="text-grey-darken-1">
              {{ enabled ? 'Enabled' : 'Disabled' }}
            </v-list-item-subtitle>

            <template v-slot:append>
              <v-switch
                :model-value="enabled"
                color="success"
                hide-details
                density="comfortable"
                :loading="pendingUpdates.includes(name)"
                @update:model-value="updateConnection(name, $event)"
              ></v-switch>
            </template>
          </v-list-item>

          <v-list-item v-if="Object.keys(connections).length === 0" class="mb-1 rounded">
            <v-list-item-title class="text-grey-darken-1">
              No external connections available
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { externalApiConnections } from '../services/api';

// State
const connections = ref({});
const loading = ref(true);
const error = ref(null);
const successMessage = ref(null);
const pendingUpdates = ref([]);

// Format connection name for display (convert snake_case to Title Case)
const formatConnectionName = (name) => {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Load connections
const loadConnections = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await externalApiConnections.getConnections();
    connections.value = response.data;
  } catch (err) {
    console.error('Failed to load connections:', err);
    error.value = 'Failed to load external connections. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Update a connection
const updateConnection = async (name, enabled) => {
  error.value = null;
  successMessage.value = null;
  pendingUpdates.value.push(name);
  
  try {
    const response = await externalApiConnections.updateConnection(name, enabled);
    connections.value = response.data;
    successMessage.value = `${formatConnectionName(name)} ${enabled ? 'enabled' : 'disabled'} successfully.`;
  } catch (err) {
    console.error(`Failed to update ${name}:`, err);
    error.value = `Failed to ${enabled ? 'enable' : 'disable'} ${formatConnectionName(name)}. Please try again.`;
    // Revert the UI state since the operation failed
    loadConnections();
  } finally {
    pendingUpdates.value = pendingUpdates.value.filter(item => item !== name);
  }
};

// Load connections on component mount
onMounted(loadConnections);
</script>

<style scoped>
.v-list-item {
  min-height: 60px;
}
</style> 