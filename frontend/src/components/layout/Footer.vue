<template>
  <footer class="footer mt-auto py-3 bg-light border-top" :class="{ 'with-debug-panel': isDev, 'with-expanded-debug': isDebugPanelExpanded }">
    <div class="container">
      <div class="row">
        <div class="col-md-6">
          <p class="mb-0 text-muted">&copy; {{ currentYear }} pyERP. All rights reserved.</p>
        </div>
        <div class="col-md-6 text-md-end d-flex justify-content-end align-items-center">
          <router-link to="/Health" class="health-status me-3" :title="healthStatusText">
            <span class="status-dot" :class="healthStatusClass"></span>
          </router-link>
          <p class="mb-0 text-muted">Version {{ appVersion }}</p>
        </div>
      </div>
    </div>
  </footer>
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
    const basicHealth = await axios.get('/health/', {
      timeout: 5000
    });

    // Set version from health check response
    appVersion.value = basicHealth.data.version || 'unknown';

    // If basic health check shows unhealthy, set error status
    if (basicHealth.data.status === 'unhealthy') {
      healthStatus.value = 'error';
      return;
    }

    // Then try the detailed health check
    try {
      const detailedHealth = await axios.get<DetailedHealthResponse>('/monitoring/health-checks/', {
        timeout: 5000
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
      } else {
        healthStatus.value = 'success';
      }
    } catch (detailedError) {
      console.warn('Detailed health check failed:', detailedError);
      // If detailed check fails but basic check passed, show warning
      healthStatus.value = 'warning';
    }
  } catch (error: any) {
    console.error('Health check failed:', error);
    // Set error status for any health check failure
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
