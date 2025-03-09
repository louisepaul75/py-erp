<!-- Debug Panel Component -->
<template>
  <div class="debug-panel" v-if="isDev">
    <div class="debug-header" @click="toggleExpanded">
      <div class="debug-badge">DEV MODE (Port: {{ currentPort }}) - {{ currentBranch || 'Unknown Branch' }}</div>
      <div class="debug-chevron" :class="{ 'expanded': isExpanded }">▼</div>
    </div>
    <div class="debug-content" v-if="isExpanded">
      <div class="debug-info">
        <div class="debug-section">
          <h4>Environment Info</h4>
          <p>App Version: {{ appVersion }}</p>
          <p>Vue Version: {{ vueVersion }}</p>
          <p>Node Env: {{ nodeEnv }}</p>
          <p>Dev Server: {{ isDevServer ? 'Yes' : 'No' }}</p>
          <p>Docker: {{ isDocker ? 'Yes' : 'No' }}</p>
          <p>Branch: {{ currentBranch || 'Unknown' }}</p>
        </div>
        <div class="debug-section">
          <h4>Performance</h4>
          <p>Page Load Time: {{ pageLoadTime }}ms</p>
          <p>Memory Usage: {{ memoryUsage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { version as vueVersion } from 'vue';

const isExpanded = ref(false);
const pageLoadTime = ref(0);
const memoryUsage = ref('');
const currentBranch = ref('');

// Get current port
const currentPort = computed(() => typeof window !== 'undefined' ? window.location.port : '');
const isDevServer = computed(() => currentPort.value === '5173');

// Check if running in Docker
const isDocker = computed(() => {
  // Check for common Docker environment indicators
  return typeof window !== 'undefined' && (
    window.location.hostname === 'localhost' ||
    window.location.hostname.includes('docker') ||
    window.location.hostname.match(/^(\d{1,3}\.){3}\d{1,3}$/) // IP address format
  );
});

// More comprehensive development environment detection
const isDevelopment = computed(() => {
  const devServer = isDevServer.value;
  const devMode = import.meta.env.DEV || import.meta.env.MODE === 'development';
  console.log('Development detection:', {
    devServer,
    devMode,
    port: currentPort.value,
    env: import.meta.env,
    docker: isDocker.value
  });
  return devServer || devMode;
});

// Make isDev reactive using computed
const isDev = isDevelopment;

const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0';
const nodeEnv = import.meta.env.MODE;

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;

  // Dispatch custom event for the footer to listen to
  window.dispatchEvent(new CustomEvent('debug-panel-toggle', {
    detail: {
      expanded: isExpanded.value
    }
  }));
};

// Get current branch name
const fetchBranchName = async () => {
  try {
    const response = await fetch('http://localhost:8050/api/git/branch');
    const data = await response.json();
    currentBranch.value = data.branch;
  } catch (error) {
    console.error('Failed to fetch branch name:', error);
    currentBranch.value = 'Unknown';
  }
};

onMounted(() => {
  console.log('Debug Panel mounted. Development mode:', isDev.value);

  // Calculate page load time
  if (typeof window !== 'undefined' && window.performance) {
    const perfData = window.performance.timing;
    pageLoadTime.value = perfData.loadEventEnd - perfData.navigationStart;
  }

  // Get memory usage if available
  if (typeof window !== 'undefined' && window.performance && (performance as any).memory) {
    const memory = (performance as any).memory;
    memoryUsage.value = `${Math.round(memory.usedJSHeapSize / 1048576)}MB / ${Math.round(memory.jsHeapSizeLimit / 1048576)}MB`;
  } else {
    memoryUsage.value = 'Not available';
  }

  // Fetch branch name
  fetchBranchName();
});
</script>

<style scoped>
.debug-panel {
  position: fixed;
  bottom: 60px; /* Move up by 60px to be clearly visible above the footer */
  left: 0;
  right: 0;
  background: #ff9800;
  color: white;
  z-index: 10000; /* Lower z-index than footer to ensure it's below */
  font-family: monospace;
  box-shadow: 0 -2px 5px rgba(0,0,0,0.2);
  /* Force hardware acceleration to fix stacking issues in some environments */
  transform: translateZ(0);
  will-change: transform;
  border-radius: 4px 4px 0 0; /* Add rounded corners at the top */
  margin: 0 10px; /* Add some margin on the sides */
  max-width: calc(100% - 20px); /* Ensure it respects the margins */
}

.debug-header {
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.debug-badge {
  font-weight: bold;
  font-size: 14px;
}

.debug-chevron {
  transition: transform 0.3s ease;
  font-size: 12px;
}

.debug-chevron.expanded {
  transform: rotate(180deg);
}

.debug-content {
  background: #fff;
  color: #333;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  max-height: 300px;
  overflow-y: auto;
}

.debug-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.debug-section {
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.debug-section h4 {
  margin: 0 0 10px 0;
  color: #ff9800;
  font-size: 14px;
}

.debug-section p {
  margin: 5px 0;
  font-size: 12px;
}
</style>
