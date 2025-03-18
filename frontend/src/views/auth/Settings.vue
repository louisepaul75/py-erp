<template>
  <div class="settings-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-white bg-primary">
            <h2>{{ authStore.isAdmin ? 'Admin Dashboard' : 'User Settings' }}</h2>
          </v-card-title>

          <v-card-text>
            <div v-if="authStore.isLoading" class="text-center py-4">
              <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            </div>

            <div v-else-if="authStore.user">
              <v-alert type="info" variant="tonal" class="mb-4">
                {{
                  authStore.isAdmin
                    ? 'Welcome to the Admin Dashboard. Here you can manage system settings and user accounts.'
                    : 'This is the settings page where you can manage your account preferences.'
                }}
              </v-alert>

              <v-tabs v-model="activeTab" class="mb-6">
                <v-tab value="account">Account</v-tab>
                <v-tab value="appearance">Appearance</v-tab>
                <v-tab value="notifications">Notifications</v-tab>
                <v-tab v-if="authStore.isAdmin" value="users">Users</v-tab>
                <v-tab v-if="authStore.isAdmin" value="system">System</v-tab>
              </v-tabs>

              <v-window v-model="activeTab">
                <!-- Account Settings Tab -->
                <v-window-item value="account">
                  <h3 class="text-h5 mb-4">Account Settings</h3>
                  <v-list>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon icon="mdi-account" class="mr-3"></v-icon>
                      </template>
                      <v-list-item-title>Username</v-list-item-title>
                      <v-list-item-subtitle>{{ authStore.user.username }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon icon="mdi-email" class="mr-3"></v-icon>
                      </template>
                      <v-list-item-title>Email</v-list-item-title>
                      <v-list-item-subtitle>{{ authStore.user.email }}</v-list-item-subtitle>
                    </v-list-item>

                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon icon="mdi-shield-account" class="mr-3"></v-icon>
                      </template>
                      <v-list-item-title>Role</v-list-item-title>
                      <v-list-item-subtitle>{{
                        authStore.isAdmin ? 'Administrator' : 'User'
                      }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>

                  <v-divider class="my-4"></v-divider>

                  <v-btn
                    color="primary"
                    variant="outlined"
                    prepend-icon="mdi-account-edit"
                    to="/profile"
                  >
                    Edit Profile
                  </v-btn>
                </v-window-item>

                <!-- Appearance Settings Tab -->
                <v-window-item value="appearance">
                  <h3 class="text-h5 mb-4">Appearance Settings</h3>
                  <v-list>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon
                          :icon="themeStore.isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'"
                          class="mr-3"
                        ></v-icon>
                      </template>
                      <v-list-item-title>Theme</v-list-item-title>
                      <v-list-item-subtitle>{{
                        themeStore.isDark ? 'Dark Mode' : 'Light Mode'
                      }}</v-list-item-subtitle>
                      <template v-slot:append>
                        <v-switch
                          v-model="themeStore.isDark"
                          hide-details
                          inset
                          density="compact"
                          color="primary"
                          @click="themeStore.toggleTheme"
                        ></v-switch>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-window-item>

                <!-- Notifications Settings Tab -->
                <v-window-item value="notifications">
                  <h3 class="text-h5 mb-4">Notification Settings</h3>
                  <v-alert type="info" variant="tonal" class="mb-4">
                    Notification settings will be implemented in a future update.
                  </v-alert>
                </v-window-item>

                <!-- Admin Only: Users Management Tab -->
                <v-window-item v-if="authStore.isAdmin" value="users">
                  <h3 class="text-h5 mb-4">User Management</h3>
                  
                  <UserPermissionsDashboard />
                </v-window-item>

                <!-- Admin Only: System Settings Tab -->
                <v-window-item v-if="authStore.isAdmin" value="system">
                  <h3 class="text-h5 mb-4">System Settings</h3>

                  <!-- External Connections -->
                  <ExternalConnectionsSettings class="mb-6" />

                  <!-- Email Settings Card -->
                  <v-card variant="outlined" class="mb-6">
                    <v-card-title>
                      <v-icon icon="mdi-email" class="mr-2"></v-icon>
                      Email Settings
                    </v-card-title>
                    <v-card-text>
                      <p class="mb-4">
                        Configure email settings for the system, including SMTP server configuration
                        for sending emails.
                      </p>
                      <v-btn
                        color="primary"
                        variant="outlined"
                        prepend-icon="mdi-email-outline"
                        to="/settings/smtp"
                      >
                        SMTP Settings
                      </v-btn>
                    </v-card-text>
                  </v-card>

                  <v-row>
                    <v-col cols="12" md="6">
                      <v-card variant="outlined" class="mb-4">
                        <v-card-title>
                          <v-icon icon="mdi-database" class="mr-2"></v-icon>
                          Database Status
                        </v-card-title>
                        <v-card-text>
                          <v-list density="compact">
                            <v-list-item>
                              <v-list-item-title>Connection</v-list-item-title>
                              <template v-slot:append>
                                <v-chip color="success" size="small">Connected</v-chip>
                              </template>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title>Last Backup</v-list-item-title>
                              <template v-slot:append>
                                <span>2023-06-15 03:45 AM</span>
                              </template>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title>Size</v-list-item-title>
                              <template v-slot:append>
                                <span>1.2 GB</span>
                              </template>
                            </v-list-item>
                          </v-list>
                          <v-btn
                            color="primary"
                            variant="outlined"
                            class="mt-3"
                            prepend-icon="mdi-backup-restore"
                          >
                            Backup Now
                          </v-btn>
                        </v-card-text>
                      </v-card>
                    </v-col>

                    <v-col cols="12" md="6">
                      <v-card variant="outlined" class="mb-4">
                        <v-card-title>
                          <v-icon icon="mdi-server" class="mr-2"></v-icon>
                          System Health
                          <span v-if="hostResources.last_updated" class="text-caption ml-auto">
                            Last updated: {{ formatTimestamp(hostResources.last_updated) }}
                          </span>
                        </v-card-title>
                        <v-card-text>
                          <v-list density="compact">
                            <v-list-item>
                              <v-list-item-title>CPU Usage</v-list-item-title>
                              <template v-slot:append>
                                <div class="d-flex align-center" style="min-width: 120px">
                                  <v-progress-linear
                                    :model-value="hostResources.cpu_usage"
                                    :color="getResourceColor(hostResources.cpu_usage)"
                                    height="8"
                                    class="mt-1 flex-grow-1"
                                  ></v-progress-linear>
                                  <span class="ml-2">{{ hostResources.cpu_usage }}%</span>
                                </div>
                              </template>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title>Memory Usage</v-list-item-title>
                              <template v-slot:append>
                                <div class="d-flex align-center" style="min-width: 120px">
                                  <v-progress-linear
                                    :model-value="hostResources.memory_usage"
                                    :color="getResourceColor(hostResources.memory_usage)"
                                    height="8"
                                    class="mt-1 flex-grow-1"
                                  ></v-progress-linear>
                                  <span class="ml-2">{{ hostResources.memory_usage }}%</span>
                                </div>
                              </template>
                            </v-list-item>
                            <v-list-item>
                              <v-list-item-title>Disk Space</v-list-item-title>
                              <template v-slot:append>
                                <div class="d-flex align-center" style="min-width: 120px">
                                  <v-progress-linear
                                    :model-value="hostResources.disk_usage"
                                    :color="getResourceColor(hostResources.disk_usage)"
                                    height="8"
                                    class="mt-1 flex-grow-1"
                                  ></v-progress-linear>
                                  <span class="ml-2">{{ hostResources.disk_usage }}%</span>
                                </div>
                              </template>
                            </v-list-item>
                          </v-list>
                          <v-btn
                            color="primary"
                            variant="outlined"
                            class="mt-3"
                            prepend-icon="mdi-refresh"
                            @click="refreshHostResources"
                            :loading="hostResources.loading"
                          >
                            Refresh
                          </v-btn>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>

                  <v-alert type="info" variant="tonal" class="mt-4">
                    This is a placeholder. System management functionality will be implemented in a
                    future update.
                  </v-alert>
                </v-window-item>
              </v-window>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../../store/auth';
import { useThemeStore } from '../../store/theme';
import api from '../../services/api';
import ExternalConnectionsSettings from '../../components/ExternalConnectionsSettings.vue';
import UserPermissionsDashboard from '../../components/UserPermissionsDashboard.vue';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const activeTab = ref('account');

// Host resources state
interface HostResources {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  last_updated: Date | null;
  loading: boolean;
}

const hostResources = ref<HostResources>({
  cpu_usage: 35,
  memory_usage: 68,
  disk_usage: 42,
  last_updated: null,
  loading: false
});

// Function to get color based on resource usage
const getResourceColor = (value: number) => {
  if (value < 60) return 'success';
  if (value < 80) return 'warning';
  return 'error';
};

// Function to format timestamp
const formatTimestamp = (timestamp: Date | null) => {
  if (!timestamp) return 'Unknown';

  if (typeof timestamp === 'string') {
    timestamp = new Date(timestamp);
  }

  return timestamp.toLocaleString();
};

// Function to refresh host resources
const refreshHostResources = async () => {
  try {
    // Set loading state
    hostResources.value.loading = true;

    // Make API call to get host resources
    const response = await api.get('/monitoring/host-resources/', {
      timeout: 10000 // 10 second timeout
    });

    if (response.data && response.data.success) {
      // Extract data from the response
      const data = response.data.data;

      // Update host resources with data from API
      hostResources.value = {
        cpu_usage: data?.cpu?.percent || 35,
        memory_usage: data?.memory?.percent || 68,
        disk_usage: data?.disk?.percent || 42,
        last_updated: new Date(),
        loading: false
      };
    } else {
      throw new Error(response.data?.error || 'Failed to fetch host resources');
    }
  } catch (error) {
    console.error('Error fetching host resources:', error);
    // Keep existing values but update loading state
    hostResources.value.loading = false;
  }
};

// Fetch host resources when component is mounted
onMounted(() => {
  if (authStore.isAdmin) {
    refreshHostResources();
  }
});
</script>

<style scoped>
.settings-container {
  padding: 20px 0;
}

/* Override any hardcoded styles from Health.vue */
:deep(.v-card) {
  /* Use Vuetify's theme variables instead of hardcoded colors */
  background-color: inherit !important;
  color: inherit !important;
}

/* Ensure consistent card heights in the grid */
.v-row .v-col .v-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.v-row .v-col .v-card .v-card-text {
  flex-grow: 1;
}

/* Fix progress bar styling */
:deep(.v-progress-linear) {
  border-radius: 4px;
  overflow: hidden;
}
</style>
