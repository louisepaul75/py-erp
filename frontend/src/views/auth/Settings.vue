<template>
  <div class="settings-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-white bg-primary">
            <h2>User Settings</h2>
          </v-card-title>
          
          <v-card-text>
            <div v-if="authStore.isLoading" class="text-center py-4">
              <v-progress-circular
                indeterminate
                color="primary"
                size="64"
              ></v-progress-circular>
            </div>

            <div v-else-if="authStore.user">
              <v-alert
                type="info"
                variant="tonal"
                class="mb-4"
              >
                This is the settings page where you can manage your account preferences.
              </v-alert>

              <v-tabs v-model="activeTab" class="mb-6">
                <v-tab value="account">Account</v-tab>
                <v-tab value="appearance">Appearance</v-tab>
                <v-tab value="notifications">Notifications</v-tab>
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
                      <v-list-item-subtitle>{{ authStore.isAdmin ? 'Administrator' : 'User' }}</v-list-item-subtitle>
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
                        <v-icon :icon="themeStore.isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'" class="mr-3"></v-icon>
                      </template>
                      <v-list-item-title>Theme</v-list-item-title>
                      <v-list-item-subtitle>{{ themeStore.isDark ? 'Dark Mode' : 'Light Mode' }}</v-list-item-subtitle>
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
                  <v-alert
                    type="info"
                    variant="tonal"
                    class="mb-4"
                  >
                    Notification settings will be implemented in a future update.
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
import { ref } from 'vue';
import { useAuthStore } from '../../store/auth';
import { useThemeStore } from '../../store/theme';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const activeTab = ref('account');
</script>

<style scoped>
.settings-container {
  padding: 20px 0;
}
</style> 