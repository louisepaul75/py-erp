<template>
  <div class="login-container">
    <div class="card login-card">
      <div class="card-header bg-primary text-white">
        <h2 class="mb-0">Login</h2>
      </div>
      <div class="card-body">
        <div v-if="authStore.error" class="alert alert-danger">
          {{ authStore.error }}
        </div>
        
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input 
              type="text" 
              class="form-control" 
              id="username" 
              v-model="credentials.username" 
              required
              autocomplete="username"
            >
          </div>
          
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password" 
              v-model="credentials.password" 
              required
              autocomplete="current-password"
            >
          </div>
          
          <div class="d-grid gap-2">
            <button 
              type="submit" 
              class="btn btn-primary" 
              :disabled="authStore.isLoading"
            >
              <span v-if="authStore.isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Login
            </button>
          </div>
        </form>
        
        <div class="mt-3 text-center">
          <a href="/accounts/password_reset/">Forgot password?</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../store/auth';
import { LoginCredentials } from '../../services/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Initialize credentials
const credentials = ref<LoginCredentials>({
  username: '',
  password: ''
});

// Handle login form submission
const handleLogin = async () => {
  try {
    await authStore.login(credentials.value);
    
    // Redirect to the intended destination or home
    const redirectPath = route.query.redirect as string || '/';
    router.push(redirectPath);
  } catch (error) {
    // Error is already handled in the store
    console.error('Login failed:', error);
  }
};

// Clear any previous errors when component is mounted
onMounted(() => {
  authStore.clearError();
});
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style> 