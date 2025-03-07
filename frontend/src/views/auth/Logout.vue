<template>
  <div class="logout-container">
    <v-card class="mx-auto" max-width="400">
      <v-card-title class="text-white bg-primary">
        <h2>Logging Out</h2>
      </v-card-title>
      <v-card-text class="text-center pa-6">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
          class="mb-4"
        ></v-progress-circular>
        <p class="text-body-1">Logging you out...</p>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth';

const router = useRouter();
const authStore = useAuthStore();

onMounted(() => {
  // Logout the user
  authStore.logout();

  // Redirect to login page after a short delay
  setTimeout(() => {
    router.push({ name: 'Login' });
  }, 1000);
});
</script>

<style scoped>
.logout-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}
</style>
