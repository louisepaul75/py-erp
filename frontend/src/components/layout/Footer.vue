<template>
  <v-footer
    app
    :class="[
      'pa-3', 
      { 'with-debug-panel': isDev, 'with-expanded-debug': isDebugPanelExpanded },
      themeStore.isDark ? 'bg-surface' : 'bg-grey-lighten-4'
    ]"
  >
    <v-container>
      <v-row>
        <v-col cols="12" md="6">
          <p class="text-body-2 text-medium-emphasis mb-0">&copy; {{ currentYear }} pyERP. All rights reserved.</p>
        </v-col>
        <v-col cols="12" md="6" class="text-md-end d-flex justify-end align-center">
          <p class="text-body-2 text-medium-emphasis mb-0 mr-3">Version {{ appVersion }}</p>
          <router-link to="/Health" class="health-status" :title="healthStatusText">
            <span class="status-dot" :class="healthStatusClass"></span>
          </router-link>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useThemeStore } from '../../store/theme';
import api from '@/services/api';

// Get theme store
const themeStore = useThemeStore();

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
    const response = await api.get('/monitoring/health-checks/', {
      timeout: 120000
    });
    
    if (response.data && response.data.success) {
      // Get version from first result that has it
      const firstResult = response.data.results[0] as HealthCheckResult;
      appVersion.value = firstResult?.version || 'unknown';

      // Determine overall status from all components
      const statuses = response.data.results.map((result: HealthCheckResult) => result.status);
      if (statuses.includes('error')) {
        healthStatus.value = 'error';
      } else if (statuses.includes('warning')) {
        healthStatus.value = 'warning';
      } else if (statuses.every((status: string) => status === 'success')) {
        healthStatus.value = 'success';
      } else {
        healthStatus.value = 'unknown';
      }
    } else {
      throw new Error('Invalid response format');
    }
  } catch (error: any) {
    console.error('Failed to fetch health status:', error);
    healthStatus.value = 'error';
    
    // Add specific handling for timeout errors
    if (error.code === 'ECONNABORTED') {
      console.warn('Health check request timed out. Health status might still be good, but the request took too long to complete.');
    }
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
  version?: string;
  component?: string;
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
  display: flex;
  align-items: center;
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

/* Dark mode specific styles */
:deep(.v-theme--dark) .text-medium-emphasis {
  color: rgba(255, 255, 255, 0.7) !important;
}
</style>
