<!-- Debug Panel Component -->
<template>
  <div class="debug-panel" v-if="isDev">
    <div class="debug-header" @click="toggleExpanded">
      <div class="debug-badge">DEV MODE (Port: {{ currentPort }})</div>
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

// Get current port
const currentPort = computed(() => typeof window !== 'undefined' ? window.location.port : '');
const isDevServer = computed(() => currentPort.value === '3000');

// More comprehensive development environment detection
const isDevelopment = computed(() => {
  const devServer = isDevServer.value;
  const devMode = import.meta.env.DEV || import.meta.env.MODE === 'development';
  console.log('Development detection:', {
    devServer,
    devMode,
    port: currentPort.value,
    env: import.meta.env
  });
  return devServer || devMode;
});

// Make isDev reactive using computed
const isDev = isDevelopment;

const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0';
const nodeEnv = import.meta.env.MODE;

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
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
});
</script>

<style scoped>
.debug-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ff9800;
  color: white;
  z-index: 9999;
  font-family: monospace;
  box-shadow: 0 -2px 5px rgba(0,0,0,0.2);
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