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

// Check health status
const checkHealthStatus = async () => {
  try {
    // First try the basic health check
    const basicHealth = await axios.get('/api/health/', {
      timeout: 60000, // Increased from 15000 to 60000 ms (60 seconds)
    });

    // Set version from health check response
    appVersion.value = basicHealth.data.version || 'unknown';

    if (basicHealth.data.status === 'unhealthy') {
      healthStatus.value = 'error';
      return;
    }

    // Then try the detailed health check
    try {
      const detailedHealth = await axios.get<DetailedHealthResponse>('/api/monitoring/health-checks/', {
        timeout: 60000, // Increased from 30000 to 60000 ms (60 seconds)
      });

      if (!detailedHealth.data.success) {
        healthStatus.value = 'warning';
        return;
      }

      const statuses = detailedHealth.data.results.map((result: HealthCheckResult) => result.status);

      if (statuses.includes('error')) {
        healthStatus.value = 'error';
      } else if (statuses.includes('warning')) {
        healthStatus.value = 'warning';
      } else if (statuses.every((status: string) => status === 'success')) {
        healthStatus.value = 'success';
      } else {
        healthStatus.value = 'unknown';
      }
    } catch (detailedError: any) {
      console.warn('Detailed health check failed:', detailedError);
      // If detailed check fails but basic check succeeded, show warning
      healthStatus.value = 'warning';
      
      // Add more detailed logging for network errors
      if (detailedError.code === 'ECONNABORTED') {
        console.error('Health check request timed out. Consider increasing the timeout or optimizing the server response.');
      }
    }
  } catch (error) {
    console.error('Health check failed:', error);
    healthStatus.value = 'error';
  }
};

let healthCheckInterval: number;

onMounted(() => {
  window.addEventListener('debug-panel-toggle', handleDebugPanelToggle);
  checkHealthStatus();
  healthCheckInterval = window.setInterval(checkHealthStatus, 60000); // Check every minute
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
