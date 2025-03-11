<template>
  <v-app :theme="themeStore.isDark ? 'dark' : 'light'">
    <template v-if="!isInitializing">
      <!-- Navigation -->
      <Navbar />
      <!-- Main Content -->
      <v-main>
        <v-container class="py-4">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </v-container>
      </v-main>
      <!-- Debug Panel - Place before footer in DOM order -->
      <DebugPanel />
      <!-- Footer - Must be last to appear at the bottom -->
      <Footer />
    </template>
    <template v-else>
      <v-container class="d-flex align-center justify-center" style="height: 100vh">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-container>
    </template>
  </v-app>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from './store/auth';
import { useThemeStore } from './store/theme';
import { useRouter, useRoute } from 'vue-router';
import Navbar from './components/layout/Navbar.vue';
import Footer from './components/layout/Footer.vue';
import DebugPanel from './components/debug/DebugPanel.vue';

// Initialize auth store and router
const authStore = useAuthStore();
const themeStore = useThemeStore();
const router = useRouter();
const route = useRoute();
const isInitializing = ref(true);

// App version
const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0';

// Initialize auth state when app is mounted
onMounted(async () => {
  try {
    await authStore.init();

    // After initialization, if we're on the login page and authenticated,
    // redirect to the intended destination or home
    if (route.name === 'Login' && authStore.isAuthenticated) {
      const redirectPath = (route.query.redirect as string) || '/';
      await router.replace(redirectPath);
    }
    // If we're on a protected route and not authenticated, router guard will handle redirect
  } finally {
    isInitializing.value = false;
  }
});
</script>
<style>
/* Global styles */
:root {
  --primary-color: #d2bc9b;
  --primary-hover: #c0aa89;
  --text-color: #343a40;
  --light-bg: #f8f9fa;
  --border-color: #e9ecef;
}

html,
body {
  height: 100%;
  color: var(--text-color);
}

body {
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  /* Ensure proper stacking context */
  position: relative;
  overflow-x: hidden;
}

/* Transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
