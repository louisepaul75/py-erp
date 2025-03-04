<template>
  <div class="logout-container">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h2 class="mb-0">Logging Out</h2>
      </div>
      <div class="card-body text-center">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p>Logging you out...</p>
      </div>
    </div>
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

.card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style> 