<template>
  <v-footer
    app
    class="pa-3 bg-grey-lighten-4"
    :class="{ 'with-debug-panel': isDev, 'with-expanded-debug': isDebugPanelExpanded }"
  >
    <v-container>
      <v-row>
        <v-col cols="12" md="6">
          <p class="text-body-2 text-medium-emphasis mb-0">&copy; {{ currentYear }} pyERP. All rights reserved.</p>
        </v-col>
        <v-col cols="12" md="6" class="text-md-end d-flex justify-end align-center">
          <router-link to="/Health" class="health-status mr-3" :title="healthStatusText">
            <span class="status-dot" :class="healthStatusClass"></span>
          </router-link>
          <p class="text-body-2 text-medium-emphasis mb-0">Version {{ appVersion }}</p>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

// Get current year for copyright
const currentYear = computed(() => new Date().getFullYear());

// App version
const appVersion = ref('');

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

// Health status
const healthStatus = ref('unknown');
const healthStatusText = computed(() => {
  switch (healthStatus.value) {
    case 'success':
      return 'All systems operational';
    case 'warning':
      return 'Some systems experiencing issues';
    case 'error':
      return 'Critical systems are down';
    default:
      return 'System status unknown';
  }
});

const healthStatusClass = computed(() => {
  return {
    'success': healthStatus.value === 'success',
    'warning': healthStatus.value === 'warning',
    'error': healthStatus.value === 'error',
    'unknown': healthStatus.value === 'unknown'
  };
});

// Fetch version and health status
const fetchHealthStatus = async () => {
  try {
    const response = await axios.get('/api/health/', {
      timeout: 5000
    });
    appVersion.value = response.data.version || 'unknown';
    healthStatus.value = response.data.status === 'healthy' ? 'success' : response.data.status;
  } catch (error) {
    console.error('Failed to fetch health status:', error);
    healthStatus.value = 'error';
  }
};

interface DebugPanelToggleEvent extends CustomEvent {
  detail: {
    expanded: boolean;
  };
}

const handleDebugPanelToggle = (event: Event) => {
  const customEvent = event as DebugPanelToggleEvent;
  if (customEvent.detail && typeof customEvent.detail.expanded === 'boolean') {
    isDebugPanelExpanded.value = customEvent.detail.expanded;
  }
};

interface HealthCheckResult {
  status: string;
  details?: string;
  response_time?: number;
  timestamp?: string;
}

interface DetailedHealthResponse {
  success: boolean;
  results: HealthCheckResult[];
}

let healthCheckInterval: number;

onMounted(() => {
  window.addEventListener('debug-panel-toggle', handleDebugPanelToggle);
  fetchHealthStatus();
  healthCheckInterval = window.setInterval(fetchHealthStatus, 60000); // Check every minute
});

onUnmounted(() => {
  window.removeEventListener('debug-panel-toggle', handleDebugPanelToggle);
  clearInterval(healthCheckInterval);
});
</script>

<style scoped>
.v-footer {
  position: relative;
  z-index: 10001; /* Higher z-index than debug panel to ensure it's above */
}

.health-status {
  text-decoration: none;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.status-dot.success {
  background-color: #28a745;
}

.status-dot.warning {
  background-color: #ffc107;
}

.status-dot.error {
  background-color: #dc3545;
}

.status-dot.unknown {
  background-color: #6c757d;
}
</style>
