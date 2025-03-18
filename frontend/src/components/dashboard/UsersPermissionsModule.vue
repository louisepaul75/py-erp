<template>
  <v-card class="dashboard-module">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-account-group" class="mr-2"></v-icon>
      Benutzer & Berechtigungen
      <v-spacer></v-spacer>
      <v-btn
        v-if="authStore.isAdmin"
        color="primary"
        variant="text"
        size="small"
        to="/users-permissions"
        prepend-icon="mdi-cog"
      >
        Verwalten
      </v-btn>
    </v-card-title>

    <v-card-text>
      <div v-if="loading" class="d-flex justify-center align-center pa-4">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <div v-else>
        <!-- Quick Stats -->
        <div class="d-flex flex-wrap gap-4 mb-4">
          <v-card
            v-for="stat in stats"
            :key="stat.title"
            variant="outlined"
            class="flex-grow-1"
            min-width="120"
          >
            <v-card-text class="text-center">
              <div class="text-h5 mb-1">{{ stat.value }}</div>
              <div class="text-caption text-medium-emphasis">{{ stat.title }}</div>
            </v-card-text>
          </v-card>
        </div>

        <!-- Quick Actions -->
        <div class="d-flex flex-wrap gap-2">
          <v-btn
            v-for="action in quickActions"
            :key="action.title"
            :to="action.to"
            :prepend-icon="action.icon"
            variant="tonal"
            size="small"
            class="flex-grow-1"
          >
            {{ action.title }}
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import usersApi from '@/services/users';

const authStore = useAuthStore();
const loading = ref(true);
const stats = ref([
  { title: 'Aktive Benutzer', value: 0 },
  { title: 'Gruppen', value: 0 },
  { title: 'Rollen', value: 0 }
]);

const quickActions = [
  { title: 'Benutzer', to: '/users-permissions/users', icon: 'mdi-account-multiple' },
  { title: 'Gruppen', to: '/users-permissions/groups', icon: 'mdi-account-group' },
  { title: 'Rollen', to: '/users-permissions/roles', icon: 'mdi-shield-account' }
];

const loadStats = async () => {
  try {
    // Get active users count
    const usersResponse = await usersApi.getUsers({ is_active: true });
    stats.value[0].value = usersResponse.data.count || 0;

    // Get groups count
    const groupsResponse = await usersApi.getGroups();
    stats.value[1].value = groupsResponse.data.count || 0;

    // Get roles count
    const rolesResponse = await usersApi.getRoles();
    stats.value[2].value = rolesResponse.data.count || 0;
  } catch (error) {
    console.error('Error loading user stats:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadStats();
});
</script>

<style scoped>
.dashboard-module {
  height: 100%;
}

.gap-4 {
  gap: 1rem;
}

.gap-2 {
  gap: 0.5rem;
}
</style> 