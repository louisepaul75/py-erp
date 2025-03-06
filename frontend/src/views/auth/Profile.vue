<template>
  <div class="profile-container">
    <div class="row">
      <div class="col-md-8 offset-md-2">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h2 class="mb-0">User Profile</h2>
          </div>
          <div class="card-body">
            <div v-if="authStore.isLoading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="authStore.user">
              <!-- Profile Information Form -->
              <form @submit.prevent="updateProfile">
                <div v-if="message" :class="['alert', messageType === 'success' ? 'alert-success' : 'alert-danger']">
                  {{ message }}
                </div>

                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    :value="authStore.user.username"
                    disabled
                  >
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="profileData.email"
                    required
                  >
                </div>

                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="first_name" class="form-label">First Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="first_name"
                      v-model="profileData.first_name"
                    >
                  </div>

                  <div class="col-md-6 mb-3">
                    <label for="last_name" class="form-label">Last Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="last_name"
                      v-model="profileData.last_name"
                    >
                  </div>
                </div>

                <div class="d-grid gap-2">
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="isUpdating"
                  >
                    <span v-if="isUpdating" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Update Profile
                  </button>
                </div>
              </form>

              <!-- Password Change Form -->
              <hr class="my-4">
              <h3>Change Password</h3>

              <form @submit.prevent="changePassword">
                <div v-if="passwordMessage" :class="['alert', passwordMessageType === 'success' ? 'alert-success' : 'alert-danger']">
                  {{ passwordMessage }}
                </div>

                <div class="mb-3">
                  <label for="old_password" class="form-label">Current Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="old_password"
                    v-model="passwordData.oldPassword"
                    required
                  >
                </div>

                <div class="mb-3">
                  <label for="new_password" class="form-label">New Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="new_password"
                    v-model="passwordData.newPassword"
                    required
                  >
                </div>

                <div class="mb-3">
                  <label for="confirm_password" class="form-label">Confirm New Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="confirm_password"
                    v-model="passwordData.confirmPassword"
                    required
                  >
                </div>

                <div class="d-grid gap-2">
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="isChangingPassword"
                  >
                    <span v-if="isChangingPassword" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Change Password
                  </button>
                </div>
              </form>
            </div>

            <div v-else class="alert alert-warning">
              You need to be logged in to view your profile.
            </div>
          </div>
        </div>
      </div>
    </div>
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
