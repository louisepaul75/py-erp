<template>
  <footer class="footer mt-auto py-3 bg-light border-top" :class="{ 'with-debug-panel': isDev, 'with-expanded-debug': isDebugPanelExpanded }">
    <div class="container">
      <div class="row">
        <div class="col-md-6">
          <p class="mb-0 text-muted">&copy; {{ currentYear }} pyERP. All rights reserved.</p>
        </div>
        <div class="col-md-6 text-md-end">
          <p class="mb-0 text-muted">Version {{ appVersion }}</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';

// Get current year for copyright
const currentYear = computed(() => new Date().getFullYear());

// App version
const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0';

// Check if in development mode
const currentPort = computed(() => typeof window !== 'undefined' ? window.location.port : '');
const isDevServer = computed(() => currentPort.value === '3000');

// Development environment detection
const isDev = computed(() => {
  const devServer = isDevServer.value;
  const devMode = import.meta.env.DEV || import.meta.env.MODE === 'development';
  return devServer || devMode;
});

// Track debug panel expanded state
const isDebugPanelExpanded = ref(false);

// Define a custom event type
interface DebugPanelToggleEvent extends CustomEvent {
  detail: {
    expanded: boolean;
  };
}

// Event listener for debug panel expansion
const handleDebugPanelToggle = (event: Event) => {
  const customEvent = event as DebugPanelToggleEvent;
  if (customEvent.detail && typeof customEvent.detail.expanded === 'boolean') {
    isDebugPanelExpanded.value = customEvent.detail.expanded;
  }
};

onMounted(() => {
  window.addEventListener('debug-panel-toggle', handleDebugPanelToggle);
});

onUnmounted(() => {
  window.removeEventListener('debug-panel-toggle', handleDebugPanelToggle);
});
</script>

<style scoped>
.footer {
  position: relative;
  z-index: 10001; /* Higher z-index than debug panel to ensure it's above */
  flex-shrink: 0;
  /* Ensure footer is not positioned over the debug panel */
  margin-bottom: 0;
}

/* Remove margin bottom when debug panel is active since we want the footer above it */
.footer.with-debug-panel {
  margin-bottom: 0;
}

/* Remove margin when debug panel is expanded */
.footer.with-expanded-debug {
  margin-bottom: 0;
}
</style>
