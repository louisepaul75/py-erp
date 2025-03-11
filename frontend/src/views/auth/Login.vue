<template>
  <div class="login-container">
    <v-card class="login-card mx-auto" max-width="400">
      <v-card-title class="text-white bg-primary">
        <h2>{{ $t('common.login') }}</h2>
      </v-card-title>

      <v-card-text>
        <v-alert v-if="authStore.error" type="error" class="mt-4" variant="tonal">
          {{ authStore.error }}
        </v-alert>

        <v-form @submit.prevent="handleLogin" class="mt-4">
          <v-text-field
            v-model="credentials.username"
            :label="$t('auth.username')"
            id="username"
            required
            autocomplete="username"
            variant="outlined"
            class="mb-4"
          ></v-text-field>

          <v-text-field
            v-model="credentials.password"
            :label="$t('auth.password')"
            id="password"
            type="password"
            required
            autocomplete="current-password"
            variant="outlined"
            class="mb-6"
          ></v-text-field>

          <v-btn
            type="submit"
            color="primary"
            block
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
          >
            Login
          </v-btn>
        </v-form>

        <div class="text-center mt-4">
          <v-btn variant="text" color="primary" href="/accounts/password_reset/" size="small">
            Forgot password?
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
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

// Initialize credentials with the superuser we created
const credentials = ref<LoginCredentials>({
  username: 'arau.j',
  password: 'password'
});

// Handle login form submission
const handleLogin = async () => {
  try {
    await authStore.login(credentials.value);

    // Redirect to the intended destination or home
    const redirectPath = (route.query.redirect as string) || '/';
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
</style>
