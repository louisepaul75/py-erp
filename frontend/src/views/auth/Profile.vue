<template>
  <div class="profile-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-white bg-primary">
            <h2>{{ $t('common.profile') }}</h2>
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
              <!-- Profile Information Form -->
              <v-form @submit.prevent="updateProfile" class="mt-4">
                <v-alert
                  v-if="message"
                  :type="messageType === 'success' ? 'success' : 'error'"
                  variant="tonal"
                  class="mb-4"
                >
                  {{ message }}
                </v-alert>

                <v-text-field
                  v-model="authStore.user.username"
                  :label="$t('auth.username')"
                  disabled
                  variant="outlined"
                  class="mb-2"
                ></v-text-field>

                <v-text-field
                  v-model="profileData.email"
                  :label="$t('auth.email')"
                  type="email"
                  required
                  variant="outlined"
                  class="mb-2"
                ></v-text-field>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.first_name"
                      :label="$t('auth.firstName')"
                      variant="outlined"
                    ></v-text-field>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.last_name"
                      :label="$t('auth.lastName')"
                      variant="outlined"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-btn
                  type="submit"
                  color="primary"
                  block
                  :loading="isUpdating"
                  :disabled="isUpdating"
                  class="mt-4"
                >
                  Update Profile
                </v-btn>
              </v-form>

              <!-- Password Change Form -->
              <v-divider class="my-6"></v-divider>
              <h3 class="text-h5 mb-4">{{ $t('auth.changePassword') }}</h3>

              <v-form @submit.prevent="changePassword">
                <v-alert
                  v-if="passwordMessage"
                  :type="passwordMessageType === 'success' ? 'success' : 'error'"
                  variant="tonal"
                  class="mb-4"
                >
                  {{ passwordMessage }}
                </v-alert>

                <v-text-field
                  v-model="passwordData.oldPassword"
                  :label="$t('auth.currentPassword')"
                  type="password"
                  required
                  variant="outlined"
                  class="mb-2"
                ></v-text-field>

                <v-text-field
                  v-model="passwordData.newPassword"
                  :label="$t('auth.newPassword')"
                  type="password"
                  required
                  variant="outlined"
                  class="mb-2"
                ></v-text-field>

                <v-text-field
                  v-model="passwordData.confirmPassword"
                  :label="$t('auth.confirmPassword')"
                  type="password"
                  required
                  variant="outlined"
                  class="mb-4"
                ></v-text-field>

                <v-btn
                  type="submit"
                  color="primary"
                  block
                  :loading="isChangingPassword"
                  :disabled="isChangingPassword"
                >
                  Change Password
                </v-btn>
              </v-form>
            </div>

            <v-alert
              v-else
              type="warning"
              variant="tonal"
              class="mt-4"
            >
              You need to be logged in to view your profile.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../../store/auth';
import { User } from '../../services/auth';

const authStore = useAuthStore();

// Profile data
const profileData = ref({
  email: '',
  first_name: '',
  last_name: ''
});

// Password change data
const passwordData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// UI state
const isUpdating = ref(false);
const isChangingPassword = ref(false);
const message = ref('');
const messageType = ref('success');
const passwordMessage = ref('');
const passwordMessageType = ref('success');

// Initialize profile data when component is mounted
onMounted(() => {
  if (authStore.user) {
    profileData.value.email = authStore.user.email;
    profileData.value.first_name = authStore.user.first_name;
    profileData.value.last_name = authStore.user.last_name;
  }
});

// Update profile
const updateProfile = async () => {
  isUpdating.value = true;
  message.value = '';

  try {
    await authStore.updateProfile(profileData.value as Partial<User>);
    message.value = 'Profile updated successfully';
    messageType.value = 'success';
  } catch (error: any) {
    message.value = error.response?.data?.detail || 'Failed to update profile';
    messageType.value = 'error';
  } finally {
    isUpdating.value = false;
  }
};

// Change password
const changePassword = async () => {
  // Validate passwords match
  if (passwordData.value.newPassword !== passwordData.value.confirmPassword) {
    passwordMessage.value = 'New passwords do not match';
    passwordMessageType.value = 'error';
    return;
  }

  isChangingPassword.value = true;
  passwordMessage.value = '';

  try {
    await authStore.changePassword(
      passwordData.value.oldPassword,
      passwordData.value.newPassword
    );

    // Clear password fields
    passwordData.value.oldPassword = '';
    passwordData.value.newPassword = '';
    passwordData.value.confirmPassword = '';

    passwordMessage.value = 'Password changed successfully';
    passwordMessageType.value = 'success';
  } catch (error: any) {
    passwordMessage.value = error.response?.data?.detail || 'Failed to change password';
    passwordMessageType.value = 'error';
  } finally {
    isChangingPassword.value = false;
  }
};
</script>

<style scoped>
.profile-container {
  padding: 20px;
}
</style>
