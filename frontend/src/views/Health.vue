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
        
        <!-- Database Visualization Animation -->
        <div class="db-visualization">
          <canvas 
            ref="dbCanvas" 
            class="db-canvas"
            width="600" 
            height="100">
          </canvas>
          <div class="canvas-legend">
            <div class="legend-item">
              <span>Speed: Average query time ({{ formatNumber(dbStats?.performance?.avg_query_time) }} ms)</span>
            </div>
            <div class="legend-item">
              <span>Blocks: System health + Transaction volume</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Connection Status Section -->
      <div class="connection-section">
        <h2>Connection Status</h2>
        <div v-if="Object.keys(filteredHealthResults || {}).length === 0" class="no-status">
          No connection status data available
        </div>
        <div v-if="filteredHealthResults && Object.keys(filteredHealthResults).length > 0" class="status-cards">
          <div v-for="(result, componentKey) in filteredHealthResults" :key="componentKey"
               :class="['status-card', result.status]">
            <div class="status-card-header">
              <div class="component-name">
                {{ getComponentDisplayName(componentKey) }}
              </div>
              <span :class="['status-indicator', result.status]"></span>
            </div>
            <div class="status-details">
              {{ result.details }}
            </div>
            <div class="status-meta">
              <div v-if="result.response_time !== undefined">
                Response Time: {{ (Number(result.response_time) || 0).toFixed(2) }} ms
              </div>
              <div v-if="result.timestamp">
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
import api from '@/services/api';

export default {
  name: 'HealthView',
  data() {
    return {
      loading: false,
      message: '',
      messageType: 'success',
      healthResults: {},
      systemInfo: {
        environment: 'development',
        version: 'unknown'
      },
      lastUpdated: null,
      // Animation properties
      animationFrameId: null,
      squares: [],
      canvas: null,
      ctx: null,
      // Database statistics
      dbStats: {
        transactions: {
          committed: 0,
          rolled_back: 0,
          active: 0
        },
        queries: {
          select_count: 0,
          insert_count: 0,
          update_count: 0,
          delete_count: 0
        },
        performance: {
          avg_query_time: 0,
          cache_hit_ratio: 0
        },
        disk: {
          size_mb: 0
        }
      },
      // For animation updates
      lastTransactionCount: 0,
      dbStatsInterval: null,
      isDatabaseStatsExpanded: false,
      isDatabaseValidationExpanded: false
    };
  },
  computed: {
    overallStatus() {
      const statuses = Object.values(this.healthResults || {}).map(result => result?.status || 'unknown');

      if (statuses.includes('error')) {
        return 'error';
      } else if (statuses.includes('warning')) {
        return 'warning';
      } else if (statuses.every(status => status === 'success')) {
        return 'success';
      } else {
        return 'unknown';
      }
    },
    // Get database response time from health results
    dbResponseTime() {
      if (this.healthResults && this.healthResults.database && this.healthResults.database.response_time) {
        return this.healthResults.database.response_time;
      }
      return 100; // Default response time if not available
    },
    filteredHealthResults() {
      if (!this.healthResults) return {};
      return Object.fromEntries(
        Object.entries(this.healthResults).filter(([key]) => key !== 'database')
      );
    }
  },
  mounted() {
    this.refreshHealthChecks();
    // Auto refresh every 5 minutes
    this.autoRefreshInterval = setInterval(() => {
      this.refreshHealthChecks();
    }, 5 * 60 * 1000);
    
    // Initialize canvas animation
    this.$nextTick(() => {
      this.setupCanvas();
    });
    
    // Set up database statistics polling
    this.fetchDatabaseStats();
    this.dbStatsInterval = setInterval(() => {
      this.fetchDatabaseStats();
    }, 10000); // Poll every 10 seconds
  },
  beforeUnmount() {
    clearInterval(this.autoRefreshInterval);
    clearInterval(this.dbStatsInterval);
    // Cancel the animation frame when component is unmounted
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  },
  watch: {
    // Watch for changes in healthResults to update the animation
    healthResults: {
      handler() {
        this.updateAnimation();
      },
      deep: true
    }
  },
  methods: {
    async refreshHealthChecks() {
      this.loading = true;
      this.message = '';

      try {
        // Try to get basic health check
        try {
          const basicHealthResponse = await api.get('/api/health/', {
            timeout: 30000 // Increased from 15000 to 30000 ms
          });
          this.systemInfo = {
            environment: basicHealthResponse.data?.environment || 'development',
            version: basicHealthResponse.data?.version || 'unknown'
          };
        } catch (error) {
          console.error('Basic health check error:', error);
          // Add specific logging for timeout errors
          if (error.code === 'ECONNABORTED') {
            console.error('Health check request timed out. Consider increasing the timeout or optimizing the server response.');
          }
          this.systemInfo = {
            environment: 'Unknown (API Unavailable)',
            version: 'Unknown'
          };
        }

        // Try to get detailed health checks
        try {
          const response = await api.get('/api/monitoring/health-checks/', {
            timeout: 30000 // Increased from 15000 to 30000 ms
          });

          if (response.data && response.data.success) {
            // Create a new object to avoid reference issues
            const newHealthResults = {};

            // Process the results - always expect an array format
            const results = response.data.results;
            if (Array.isArray(results)) {
              // First, find the main database result and validation result
              const dbResult = results.find(result => result.component === 'database');
              const dbValidationResult = results.find(result => result.component === 'database_validation');
              
              // If we have a database result, add it first with validation as a nested property
              if (dbResult) {
                newHealthResults['database'] = {
                  status: dbResult.status,
                  details: dbResult.details,
                  response_time: dbResult.response_time,
                  timestamp: dbResult.timestamp,
                  // Add validation as a nested property if it exists
                  validation: dbValidationResult ? {
                    status: dbValidationResult.status,
                    details: dbValidationResult.details,
                    response_time: dbValidationResult.response_time,
                    timestamp: dbValidationResult.timestamp
                  } : null
                };
              }

              // Then add all other non-database results
              results.forEach(result => {
                if (result && result.component && 
                    !['database', 'database_validation'].includes(result.component)) {
                  const componentKey = result.component;
                  newHealthResults[componentKey] = {
                    status: result.status,
                    details: result.details,
                    response_time: result.response_time,
                    timestamp: result.timestamp,
                    // Store the original component name as a type property to avoid 'component' naming conflict
                    type: componentKey
                  };
                }
              });

              // Replace healthResults with the new object
              this.healthResults = newHealthResults;
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
              throw new Error('Invalid response format: results must be an array');
            }
          } else {
            throw new Error(response.data?.error || 'Unknown error');
          }
        } catch (error) {
          console.error('Health checks error:', error);
          
          // Add specific logging for timeout errors
          if (error.code === 'ECONNABORTED') {
            console.error('Health check detailed request timed out. Consider increasing the timeout or optimizing the server response.');
          }
          
          // Show error in UI
          this.message = `Failed to update status: ${error.message}`;
          this.messageType = 'error';
          
          // Set mock data for testing UI
          this.healthResults = {
            'database': {
              status: 'error',
              details: 'Database connection failed',
              response_time: 0,
              timestamp: new Date(),
              validation: {
                status: 'error',
                details: 'Database validation not available',
                response_time: 0,
                timestamp: new Date()
              }
            },
            'legacy_erp': {
              status: 'warning',
              details: 'Cannot verify Legacy ERP status',
              response_time: 0,
              timestamp: new Date()
            },
            'pictures_api': {
              status: 'warning',
              details: 'Cannot verify Pictures API status',
              response_time: 0,
              timestamp: new Date()
            }
          };
        }
      } catch (error) {
        console.error('Unexpected error in health check:', error);
        this.message = 'Failed to update status: ' + (error?.message || 'Unknown error');
        this.messageType = 'error';
      } finally {
        this.loading = false;
      }
    },
    async fetchDatabaseStats() {
      try {
        const response = await api.get('/api/monitoring/db-stats/', {
          timeout: 10000 // 10 second timeout
        });
        if (response.data.success && response.data.stats) {
          // Store previous transaction count for animation
          this.lastTransactionCount = this.getTotalTransactions();
          
          // Create a new stats object with default values
          const newStats = {
            transactions: {
              committed: 0,
              rolled_back: 0,
              active: 0
            },
            queries: {
              select_count: 0,
              insert_count: 0,
              update_count: 0,
              delete_count: 0
            },
            performance: {
              avg_query_time: 0,
              cache_hit_ratio: 0
            },
            disk: {
              size_mb: 0
            }
          };
          
          const stats = response.data.stats;
          
          // Safely update nested properties with type conversion
          if (stats.transactions) {
            newStats.transactions.committed = Number(stats.transactions.committed) || 0;
            newStats.transactions.rolled_back = Number(stats.transactions.rolled_back) || 0;
            newStats.transactions.active = Number(stats.transactions.active) || 0;
          }
          
          if (stats.queries) {
            newStats.queries.select_count = Number(stats.queries.select_count) || 0;
            newStats.queries.insert_count = Number(stats.queries.insert_count) || 0;
            newStats.queries.update_count = Number(stats.queries.update_count) || 0;
            newStats.queries.delete_count = Number(stats.queries.delete_count) || 0;
          }
          
          if (stats.performance) {
            newStats.performance.avg_query_time = Number(stats.performance.avg_query_time) || 0;
            newStats.performance.cache_hit_ratio = Number(stats.performance.cache_hit_ratio) || 0;
          }
          
          if (stats.disk) {
            newStats.disk.size_mb = Number(stats.disk.size_mb) || 0;
          }
          
          // Update the component state with the new stats
          this.dbStats = newStats;
          
          // Update animation if transaction count changed
          if (this.getTotalTransactions() !== this.lastTransactionCount) {
            this.updateAnimation();
          }
        }
      } catch (error) {
        console.error('Error fetching database statistics:', error);
      }
    },
    getTotalTransactions() {
      return (this.dbStats?.transactions?.committed || 0) + 
             (this.dbStats?.transactions?.rolled_back || 0) + 
             (this.dbStats?.transactions?.active || 0);
    },
    getTotalQueries() {
      return (this.dbStats?.queries?.select_count || 0) + 
             (this.dbStats?.queries?.insert_count || 0) + 
             (this.dbStats?.queries?.update_count || 0) + 
             (this.dbStats?.queries?.delete_count || 0);
    },
    getComponentDisplayName(key) {
      // Convert snake_case or camelCase to Title Case with spaces
      return key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
    },
    formatTimestamp(timestamp) {
      if (!timestamp) return 'Unknown';
      
      if (typeof timestamp === 'string') {
        timestamp = new Date(timestamp);
      }

      return timestamp.toLocaleString();
    },
    formatNumber(value, decimals = 2) {
      // Convert to number if it's not already
      const num = Number(value);
      // Check if it's a valid number
      if (isNaN(num)) return '0';
      // Format with specified decimal places
      return num.toFixed(decimals);
    },
    
    // Animation methods
    setupCanvas() {
      try {
        this.canvas = this.$refs.dbCanvas;
        if (!this.canvas) {
          console.warn('Canvas element not found');
          return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        if (!this.ctx) {
          console.warn('Could not get canvas context');
          return;
        }
        
        this.initializeSquares();
        this.animate();
      } catch (error) {
        console.error('Error setting up canvas:', error);
      }
    },
    
    initializeSquares() {
      try {
        // Clear existing squares
        this.squares = [];
        
        if (!this.canvas || !this.ctx) return;
        
        // Number of squares based on status: success=10, warning=7, error=3, unknown=5
        let numSquares = 5; // default for unknown
        if (this.overallStatus === 'success') {
          numSquares = 10;
        } else if (this.overallStatus === 'warning') {
          numSquares = 7;
        } else if (this.overallStatus === 'error') {
          numSquares = 3;
        }
        
        // Add more squares based on transaction count (max additional 10)
        const transactionCount = this.getTotalTransactions();
        if (transactionCount > 0) {
          // Add 1 square for every 100 transactions, up to 10 more squares
          numSquares += Math.min(10, Math.floor(transactionCount / 100));
        }
        
        // Get colors based on status
        const colors = this.getStatusColors(this.overallStatus);
        
        // Create squares in a line formation
        const spacing = this.canvas.width / numSquares;
        const yPosition = this.canvas.height / 2 - 10; // Center vertically
        
        for (let i = 0; i < numSquares; i++) {
          // Distribute squares evenly across the canvas width
          const xPosition = i * spacing;
          
          this.squares.push({
            x: xPosition,
            y: yPosition,
            size: 20,
            color: colors[i % colors.length]
          });
        }
      } catch (error) {
        console.error('Error initializing squares:', error);
      }
    },
    
    updateAnimation() {
      // Only recreate squares if the overall status has changed or transaction count changed significantly
      if (this.canvas && this.ctx) {
        this.initializeSquares();
      }
    },
    
    animate() {
      try {
        if (!this.canvas || !this.ctx || !this.squares || this.squares.length === 0) {
          // Request next frame even if we can't animate now
          this.animationFrameId = requestAnimationFrame(this.animate);
          return;
        }
        
        // Clear the canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Calculate speed factor using detailed stats
        let speedFactor = 2; // Default speed
        
        // Use avg_query_time if available (faster queries = faster animation)
        if (this.dbStats?.performance?.avg_query_time > 0) {
          // Scale: 1-10ms = fastest, >300ms = slowest
          speedFactor = Math.max(1, Math.min(5, 100 / (this.dbStats.performance.avg_query_time + 10)));
        } else if (this.dbResponseTime > 0) {
          // Fallback to basic response time if detailed stats not available
          speedFactor = Math.max(1, Math.min(5, 200 / this.dbResponseTime));
        }
        
        // Add boost based on active transactions
        if (this.dbStats?.transactions?.active > 0) {
          speedFactor += Math.min(2, this.dbStats.transactions.active / 5);
        }
        
        // Update and draw squares
        this.squares.forEach(square => {
          // Move square from left to right
          square.x += speedFactor;
          
          // Wrap around when reaching right edge
          if (square.x > this.canvas.width) {
            square.x = -square.size;
          }
          
          // Draw square
          this.ctx.fillStyle = square.color;
          this.ctx.fillRect(square.x, square.y, square.size, square.size);
        });
        
        // Continue animation loop
        this.animationFrameId = requestAnimationFrame(this.animate);
      } catch (error) {
        console.error('Error in animation loop:', error);
        // Ensure we continue the animation loop even if there's an error
        this.animationFrameId = requestAnimationFrame(this.animate);
      }
    },
    
    getStatusColors(status) {
      switch (status) {
        case 'success':
          return ['rgba(40, 167, 69, 0.7)', 'rgba(40, 167, 69, 0.5)', 'rgba(40, 167, 69, 0.3)'];
        case 'warning':
          return ['rgba(255, 193, 7, 0.7)', 'rgba(255, 193, 7, 0.5)', 'rgba(255, 193, 7, 0.3)'];
        case 'error':
          return ['rgba(220, 53, 69, 0.7)', 'rgba(220, 53, 69, 0.5)', 'rgba(220, 53, 69, 0.3)'];
        default:
          return ['rgba(108, 117, 125, 0.7)', 'rgba(108, 117, 125, 0.5)', 'rgba(108, 117, 125, 0.3)'];
      }
    },
    toggleDatabaseStats() {
      this.isDatabaseStatsExpanded = !this.isDatabaseStatsExpanded;
    },
    toggleDatabaseValidation() {
      this.isDatabaseValidationExpanded = !this.isDatabaseValidationExpanded;
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
  margin-bottom: 20px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

/* Database Visualization Styles */
.db-visualization {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.db-visualization h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #333;
}

.db-canvas {
  width: 100%;
  height: 100px;
  margin-bottom: 10px;
}

.canvas-legend {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-top: 10px;
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

.no-status {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  color: #6c757d;
  font-style: italic;
  margin-bottom: 20px;
  border: 1px dashed #dee2e6;
}

.db-stats-toggle {
  margin-top: 15px;
  padding: 10px 0;
  border-top: 1px solid #eee;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  color: #333;
}

.db-stats-toggle:hover {
  color: #007bff;
}

.db-stats {
  margin-top: 15px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-box {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #e9ecef;
}

.stat-box h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

.stat-numbers {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.toggle-icon {
  font-size: 12px;
  color: #666;
  transition: transform 0.2s ease;
}

.db-validation-section {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 10px;
}

.db-validation-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 5px 0;
  font-weight: 500;
  color: #555;
}

.db-validation-details {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.validation-status {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}

.validation-status.success {
  color: #28a745;
}

.validation-status.warning {
  color: #ffc107;
}

.validation-status.error {
  color: #dc3545;
}

.validation-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
  margin-top: 5px;
}

.validation-status.success .validation-indicator {
  background-color: #28a745;
}

.validation-status.warning .validation-indicator {
  background-color: #ffc107;
}

.validation-status.error .validation-indicator {
  background-color: #dc3545;
}

.validation-meta {
  font-size: 0.85em;
  color: #6c757d;
  margin-top: 5px;
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
  
  .db-canvas {
    height: 80px;
  }
  
  .canvas-legend {
    flex-direction: column;
    gap: 5px;
  }
  
  .db-stats {
    grid-template-columns: 1fr;
  }
}
</style>
