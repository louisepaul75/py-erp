<template>
  <div class="health-page">
    <div class="health-container">
      <div class="header">
        <h1>System Health Status</h1>
        <div class="refresh-button">
          <button @click="refreshHealthChecks" :disabled="loading">
            <span v-if="!loading">↻</span>
            <span v-else class="loading-spinner"></span>
            Refresh
          </button>
        </div>
      </div>

      <div v-if="message" :class="['status-message', messageType]">
        {{ message }}
      </div>

      <!-- Overall Status Section -->
      <div class="overall-status-section">
        <div :class="['overall-status', overallStatus]">
          <div class="status-icon">
            <span v-if="overallStatus === 'success'">✓</span>
            <span v-else-if="overallStatus === 'warning'">⚠</span>
            <span v-else-if="overallStatus === 'error'">✗</span>
            <span v-else>?</span>
          </div>
          <div class="status-text">
            <h2>Overall System Status</h2>
            <p v-if="overallStatus === 'success'">All systems operational</p>
            <p v-else-if="overallStatus === 'warning'">Some systems experiencing issues</p>
            <p v-else-if="overallStatus === 'error'">Critical systems are down</p>
            <p v-else>Status unknown</p>
          </div>
        </div>
      </div>

      <!-- Connection Status Section -->
      <div class="connection-section">
        <h2>Connection Status</h2>
        <div class="status-cards">
          <div v-for="(result, component) in healthResults" :key="component"
               :class="['status-card', result ? result.status : 'unknown']">
            <div class="status-card-header">
              <div class="component-name">
                {{ getComponentDisplayName(component) }}
              </div>
              <span :class="['status-indicator', result ? result.status : 'unknown']"></span>
            </div>
            <div class="status-details">
              {{ result ? result.details : 'No health check data available' }}
            </div>
            <div class="status-meta">
              <div v-if="result && result.response_time">
                Response Time: {{ result.response_time.toFixed(2) }} ms
              </div>
              <div v-if="result && result.timestamp">
                {{ formatTimestamp(result.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Info Section -->
      <div class="additional-info-section">
        <h2>Additional Information</h2>
        <div class="info-card">
          <table>
            <tr>
              <td>Environment:</td>
              <td>{{ systemInfo.environment || 'Unknown' }}</td>
            </tr>
            <tr>
              <td>Version:</td>
              <td>{{ systemInfo.version || 'Unknown' }}</td>
            </tr>
            <tr>
              <td>Last Updated:</td>
              <td>{{ lastUpdated ? formatTimestamp(lastUpdated) : 'Never' }}</td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HealthView',
  data() {
    return {
      loading: false,
      message: '',
      messageType: 'success',
      healthResults: {},
      systemInfo: {
        environment: '',
        version: ''
      },
      lastUpdated: null
    };
  },
  computed: {
    overallStatus() {
      const statuses = Object.values(this.healthResults).map(result => result?.status || 'unknown');

      if (statuses.includes('error')) {
        return 'error';
      } else if (statuses.includes('warning')) {
        return 'warning';
      } else if (statuses.every(status => status === 'success')) {
        return 'success';
      } else {
        return 'unknown';
      }
    }
  },
  mounted() {
    this.refreshHealthChecks();
    // Auto refresh every 5 minutes
    this.autoRefreshInterval = setInterval(() => {
      this.refreshHealthChecks();
    }, 5 * 60 * 1000);
  },
  beforeUnmount() {
    clearInterval(this.autoRefreshInterval);
  },
  methods: {
    async refreshHealthChecks() {
      this.loading = true;
      this.message = '';

      try {
        // Get basic health check
        const basicHealthResponse = await axios.get('/api/health/');
        this.systemInfo = {
          environment: basicHealthResponse.data.environment,
          version: basicHealthResponse.data.version
        };

        // Get detailed health checks
        const response = await axios.get('/api/monitoring/health-checks/');

        if (response.data.success) {
          this.healthResults = {};

          // Process the results
          response.data.results.forEach(result => {
            this.healthResults[result.component] = result;
          });

          this.lastUpdated = new Date();
          this.message = 'Status updated successfully';
          this.messageType = 'success';

          // Hide success message after 3 seconds
          setTimeout(() => {
            if (this.messageType === 'success') {
              this.message = '';
            }
          }, 3000);
        } else {
          this.message = 'Failed to update status: ' + (response.data.error || 'Unknown error');
          this.messageType = 'error';
        }
      } catch (error) {
        this.message = 'Failed to update status: ' + (error.message || 'Unknown error');
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },
    getComponentDisplayName(component) {
      const displayNames = {
        'database': 'Database',
        'legacy_erp': 'Legacy ERP',
        'pictures_api': 'Pictures API',
        'database_validation': 'Database Validation'
      };

      return displayNames[component] || component;
    },
    formatTimestamp(timestamp) {
      if (typeof timestamp === 'string') {
        timestamp = new Date(timestamp);
      }

      return timestamp.toLocaleString();
    }
  }
};
</script>

<style scoped>
.health-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.health-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.refresh-button button {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.refresh-button button:hover {
  background-color: #e9ecef;
}

.refresh-button button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-top-color: #333;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-message {
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.status-message.success {
  background-color: rgba(40, 167, 69, 0.1);
  border: 1px solid rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.status-message.error {
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.overall-status-section {
  margin-bottom: 30px;
}

.overall-status {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
}

.overall-status.success {
  background-color: rgba(40, 167, 69, 0.1);
  border: 1px solid rgba(40, 167, 69, 0.2);
}

.overall-status.warning {
  background-color: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.overall-status.error {
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.2);
}

.overall-status.unknown {
  background-color: rgba(108, 117, 125, 0.1);
  border: 1px solid rgba(108, 117, 125, 0.2);
}

.status-icon {
  font-size: 32px;
  margin-right: 20px;
}

.overall-status.success .status-icon {
  color: #28a745;
}

.overall-status.warning .status-icon {
  color: #ffc107;
}

.overall-status.error .status-icon {
  color: #dc3545;
}

.overall-status.unknown .status-icon {
  color: #6c757d;
}

.status-text h2 {
  margin: 0 0 5px 0;
  font-size: 20px;
}

.status-text p {
  margin: 0;
  font-size: 16px;
}

.connection-section, .additional-info-section {
  margin-bottom: 30px;
}

.connection-section h2, .additional-info-section h2 {
  font-size: 20px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.status-card {
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-card.success {
  border-top: 4px solid #28a745;
}

.status-card.warning {
  border-top: 4px solid #ffc107;
}

.status-card.error {
  border-top: 4px solid #dc3545;
}

.status-card.unknown {
  border-top: 4px solid #6c757d;
}

.status-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f8f9fa;
}

.component-name {
  font-weight: bold;
  font-size: 16px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.success {
  background-color: #28a745;
}

.status-indicator.warning {
  background-color: #ffc107;
}

.status-indicator.error {
  background-color: #dc3545;
}

.status-indicator.unknown {
  background-color: #6c757d;
}

.status-details {
  padding: 15px;
  min-height: 80px;
  background-color: #fff;
  font-size: 14px;
  line-height: 1.5;
}

.status-meta {
  padding: 10px 15px;
  background-color: #f8f9fa;
  font-size: 12px;
  color: #6c757d;
  display: flex;
  justify-content: space-between;
}

.info-card {
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.info-card table {
  width: 100%;
  border-collapse: collapse;
}

.info-card td {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.info-card td:first-child {
  font-weight: bold;
  width: 150px;
}

.info-card tr:last-child td {
  border-bottom: none;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .refresh-button {
    margin-top: 10px;
  }

  .status-cards {
    grid-template-columns: 1fr;
  }
}
</style>
