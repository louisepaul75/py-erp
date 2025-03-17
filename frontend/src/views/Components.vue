<template>
  <div class="components-page">
    <h1>UI Components Style Guide</h1>
    <p class="subtitle">Reference for all UI components used in the pyERP project</p>

    <div class="component-section">
      <h2>Buttons</h2>
      <div class="component-group">
        <div class="component-item">
          <h3>Primary Button</h3>
          <v-btn color="primary">Primary Button</v-btn>
          <code>v-btn color="primary"</code>
        </div>
        <div class="component-item">
          <h3>Secondary Button</h3>
          <v-btn color="secondary">Secondary Button</v-btn>
          <code>v-btn color="secondary"</code>
        </div>
        <div class="component-item">
          <h3>Outlined Button</h3>
          <v-btn variant="outlined" color="primary">Outlined Button</v-btn>
          <code>v-btn variant="outlined" color="primary"</code>
        </div>
        <div class="component-item">
          <h3>Text Button</h3>
          <v-btn variant="text" color="primary">Text Button</v-btn>
          <code>v-btn variant="text" color="primary"</code>
        </div>
        <div class="component-item">
          <h3>Icon Button</h3>
          <v-btn icon="mdi-plus" color="primary"></v-btn>
          <code>v-btn icon="mdi-plus" color="primary"</code>
        </div>
      </div>
    </div>

    <div class="component-section">
      <h2>Icons</h2>
      <div class="component-group">
        <div class="component-item">
          <h3>Basic Icons</h3>
          <div class="d-flex gap-4">
            <v-icon icon="mdi-home"></v-icon>
            <v-icon icon="mdi-account"></v-icon>
            <v-icon icon="mdi-cog"></v-icon>
            <v-icon icon="mdi-bell"></v-icon>
          </div>
          <code>v-icon icon="mdi-[icon-name]"</code>
        </div>
        <div class="component-item">
          <h3>Colored Icons</h3>
          <div class="d-flex gap-4">
            <v-icon color="primary" icon="mdi-check-circle"></v-icon>
            <v-icon color="error" icon="mdi-alert-circle"></v-icon>
            <v-icon color="warning" icon="mdi-alert"></v-icon>
            <v-icon color="success" icon="mdi-check"></v-icon>
          </div>
          <code>v-icon color="[color]" icon="mdi-[icon-name]"</code>
        </div>
        <div class="component-item">
          <h3>Icon Sizes</h3>
          <div class="d-flex align-center gap-4">
            <v-icon size="x-small" icon="mdi-star"></v-icon>
            <v-icon size="small" icon="mdi-star"></v-icon>
            <v-icon icon="mdi-star"></v-icon>
            <v-icon size="large" icon="mdi-star"></v-icon>
            <v-icon size="x-large" icon="mdi-star"></v-icon>
          </div>
          <code>v-icon size="[x-small|small|default|large|x-large]"</code>
        </div>
        <div class="component-item">
          <h3>Button with Icons</h3>
          <div class="d-flex gap-4">
            <v-btn prepend-icon="mdi-download">Download</v-btn>
            <v-btn append-icon="mdi-arrow-right">Next</v-btn>
            <v-btn icon="mdi-refresh"></v-btn>
          </div>
          <code>v-btn prepend-icon="mdi-[icon-name]" or append-icon="mdi-[icon-name]"</code>
        </div>
      </div>
    </div>

    <div class="component-section">
      <h2>Text Fields</h2>
      <div class="component-group">
        <div class="component-item">
          <h3>Basic Input</h3>
          <v-text-field label="Basic Input" placeholder="Enter text"></v-text-field>
          <code>v-text-field label="Basic Input" placeholder="Enter text"</code>
        </div>
        <div class="component-item">
          <h3>With Icon</h3>
          <v-text-field label="With Icon" prepend-icon="mdi-account"></v-text-field>
          <code>v-text-field label="With Icon" prepend-icon="mdi-account"</code>
        </div>
        <div class="component-item">
          <h3>Required Field</h3>
          <v-text-field label="Required Field" required></v-text-field>
          <code>v-text-field label="Required Field" required</code>
        </div>
        <div class="component-item">
          <h3>Textarea</h3>
          <v-textarea label="Textarea" rows="3"></v-textarea>
          <code>v-textarea label="Textarea" rows="3"</code>
        </div>
      </div>
    </div>

    <div class="component-section">
      <h2>Cards</h2>
      <div class="component-group">
        <div class="component-item wide">
          <h3>Basic Card</h3>
          <v-card>
            <v-card-title>Card Title</v-card-title>
            <v-card-text>
              This is the content of the card. It can contain any information that needs to be
              displayed.
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary">Action</v-btn>
            </v-card-actions>
          </v-card>
          <code>v-card with v-card-title, v-card-text, and v-card-actions</code>
        </div>
        <div class="component-item wide">
          <h3>Elevated Card</h3>
          <v-card elevation="4">
            <v-card-title>Elevated Card</v-card-title>
            <v-card-text> This card has an elevation of 4, giving it a shadow effect. </v-card-text>
          </v-card>
          <code>v-card elevation="4"</code>
        </div>
      </div>
    </div>

    <div class="component-section">
      <h2>Data Display</h2>
      <div class="component-group">
        <div class="component-item wide">
          <h3>Simple Table</h3>
          <v-table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>John Doe</td>
                <td>john@example.com</td>
                <td>Active</td>
              </tr>
              <tr>
                <td>Jane Smith</td>
                <td>jane@example.com</td>
                <td>Pending</td>
              </tr>
            </tbody>
          </v-table>
          <code>v-table with thead and tbody</code>
        </div>

        <div class="component-item wide">
          <h3>Data Table</h3>
          <v-data-table
            :headers="tableHeaders"
            :items="tableItems"
            :items-per-page="5"
            class="elevation-1"
          ></v-data-table>
          <code>v-data-table with headers, items, and pagination</code>
        </div>

        <div class="component-item wide">
          <h3>Data Table with Sorting and Selection</h3>
          <v-data-table
            :headers="tableHeaders"
            :items="tableItems"
            :items-per-page="5"
            class="elevation-1"
            show-select
            item-value="id"
          ></v-data-table>
          <code>v-data-table with sorting and selection</code>
        </div>
      </div>
    </div>

    <div class="component-section">
      <h2>Chart Cards</h2>
      <div class="component-group">
        <div class="component-item wide">
          <h3>Line Chart Card</h3>
          <v-card class="pa-4">
            <v-card-title>Monthly Sales Performance</v-card-title>
            <v-card-subtitle>Last 6 months</v-card-subtitle>
            <v-card-text>
              <v-sheet height="300">
                <canvas ref="lineChartRef"></canvas>
              </v-sheet>
            </v-card-text>
          </v-card>
          <code>v-card with canvas for Chart.js line chart</code>
        </div>

        <div class="component-item wide">
          <h3>Bar Chart Card</h3>
          <v-card class="pa-4">
            <v-card-title>Product Sales Comparison</v-card-title>
            <v-card-subtitle>Top 5 products</v-card-subtitle>
            <v-card-text>
              <v-sheet height="300">
                <canvas ref="barChartRef"></canvas>
              </v-sheet>
            </v-card-text>
          </v-card>
          <code>v-card with canvas for Chart.js bar chart</code>
        </div>

        <div class="component-item wide">
          <h3>Pie Chart Card</h3>
          <v-card class="pa-4">
            <v-card-title>Revenue Distribution</v-card-title>
            <v-card-subtitle>By product category</v-card-subtitle>
            <v-card-text>
              <v-sheet height="300">
                <canvas ref="pieChartRef"></canvas>
              </v-sheet>
            </v-card-text>
          </v-card>
          <code>v-card with canvas for Chart.js pie chart</code>
        </div>

        <div class="component-item">
          <h3>Mini Chart Card</h3>
          <v-card class="pa-2">
            <v-card-title class="text-subtitle-1">Weekly Traffic</v-card-title>
            <v-card-text class="pt-0">
              <v-sheet height="100">
                <canvas ref="miniChartRef"></canvas>
              </v-sheet>
            </v-card-text>
          </v-card>
          <code>v-card with mini chart for trend visualization</code>
        </div>
      </div>
    </div>

    <div class="component-section">
      <h2>Metrics Cards</h2>
      <div class="component-group">
        <div class="component-item">
          <h3>Basic Metric Card</h3>
          <v-card class="pa-4">
            <v-card-title class="text-subtitle-1 pb-0">Total Revenue</v-card-title>
            <v-card-text>
              <div class="d-flex align-center justify-space-between">
                <div class="text-h5 font-weight-bold">$128,430</div>
                <v-icon color="primary" size="x-large">mdi-currency-usd</v-icon>
              </div>
            </v-card-text>
          </v-card>
          <code>v-card with metric value and icon</code>
        </div>

        <div class="component-item">
          <h3>Metric Card with Trend</h3>
          <v-card class="pa-4">
            <v-card-title class="text-subtitle-1 pb-0">New Users</v-card-title>
            <v-card-text>
              <div class="d-flex align-center justify-space-between">
                <div>
                  <div class="text-h5 font-weight-bold">2,845</div>
                  <div class="d-flex align-center">
                    <v-icon color="success" size="small">mdi-arrow-up</v-icon>
                    <span class="text-success text-caption ml-1">12% increase</span>
                  </div>
                </div>
                <v-icon color="info" size="x-large">mdi-account-multiple</v-icon>
              </div>
            </v-card-text>
          </v-card>
          <code>v-card with metric value, trend indicator, and icon</code>
        </div>

        <div class="component-item">
          <h3>Metric Card with Progress</h3>
          <v-card class="pa-4">
            <v-card-title class="text-subtitle-1 pb-0">Task Completion</v-card-title>
            <v-card-text>
              <div class="d-flex flex-column">
                <div class="d-flex align-center justify-space-between mb-2">
                  <div class="text-h5 font-weight-bold">68%</div>
                  <v-icon color="warning" size="x-large">mdi-clipboard-check</v-icon>
                </div>
                <v-progress-linear color="warning" height="8" :model-value="68"></v-progress-linear>
              </div>
            </v-card-text>
          </v-card>
          <code>v-card with metric value, progress bar, and icon</code>
        </div>

        <div class="component-item">
          <h3>Comparison Metric Card</h3>
          <v-card class="pa-4">
            <v-card-title class="text-subtitle-1 pb-0">Sales Conversion</v-card-title>
            <v-card-text>
              <div class="d-flex flex-column">
                <div class="d-flex align-center justify-space-between">
                  <div class="text-h5 font-weight-bold">24.5%</div>
                  <v-chip color="success" size="small">+3.2%</v-chip>
                </div>
                <div class="d-flex align-center mt-2">
                  <span class="text-caption text-medium-emphasis mr-2">Previous: 21.3%</span>
                  <v-icon color="success" size="x-small">mdi-trending-up</v-icon>
                </div>
              </div>
            </v-card-text>
          </v-card>
          <code>v-card with current value, comparison chip, and previous value</code>
        </div>
      </div>
    </div>

    <div class="component-section">
      <h2>Color Palette</h2>
      <p class="section-description">The pyERP color system uses a consistent palette to create visual hierarchy, ensure accessibility, and maintain brand consistency.</p>
      
      <h3 class="subsection-title">Brand Colors</h3>
      <div class="color-grid">
        <div class="color-item primary">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Primary</h3>
            <code>color="primary"</code>
            <p class="color-usage">Used for primary actions, key navigation elements, and highlighting important information.</p>
          </div>
        </div>
        <div class="color-item secondary">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Secondary</h3>
            <code>color="secondary"</code>
            <p class="color-usage">Used for secondary actions, supporting elements, and alternative emphasis.</p>
          </div>
        </div>
      </div>

      <h3 class="subsection-title mt-6">System Colors</h3>
      <div class="color-grid">
        <div class="color-item success">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Success</h3>
            <code>color="success"</code>
            <p class="color-usage">Indicates successful actions, completions, and positive states.</p>
          </div>
        </div>
        <div class="color-item info">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Info</h3>
            <code>color="info"</code>
            <p class="color-usage">Used for informational messages, help text, and neutral states.</p>
          </div>
        </div>
        <div class="color-item warning">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Warning</h3>
            <code>color="warning"</code>
            <p class="color-usage">Indicates warnings, pending actions, or states requiring attention.</p>
          </div>
        </div>
        <div class="color-item error">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Error</h3>
            <code>color="error"</code>
            <p class="color-usage">Used for error states, destructive actions, and critical alerts.</p>
          </div>
        </div>
      </div>

      <h3 class="subsection-title mt-6">Background Colors</h3>
      <div class="color-grid">
        <div class="color-item bg-surface">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Surface</h3>
            <code>bg-color="surface"</code>
            <p class="color-usage">Default background for cards and elevated surfaces.</p>
          </div>
        </div>
        <div class="color-item bg-background">
          <div class="color-swatch"></div>
          <div class="color-info">
            <h3>Background</h3>
            <code>bg-color="background"</code>
            <p class="color-usage">Main application background color.</p>
          </div>
        </div>
      </div>

      <h3 class="subsection-title mt-6">Usage Examples</h3>
      <div class="example-grid">
        <div class="example-item">
          <h4>Text Colors</h4>
          <div class="d-flex flex-column gap-2">
            <span class="text-primary">Primary Text</span>
            <span class="text-secondary">Secondary Text</span>
            <span class="text-success">Success Text</span>
            <span class="text-error">Error Text</span>
            <code>text-[color]</code>
          </div>
        </div>
        <div class="example-item">
          <h4>Background Colors</h4>
          <div class="d-flex flex-column gap-2">
            <div class="pa-2 bg-primary text-white">Primary Background</div>
            <div class="pa-2 bg-secondary text-white">Secondary Background</div>
            <div class="pa-2 bg-success text-white">Success Background</div>
            <div class="pa-2 bg-error text-white">Error Background</div>
            <code>bg-[color]</code>
          </div>
        </div>
        <div class="example-item">
          <h4>Component Examples</h4>
          <div class="d-flex flex-column gap-2">
            <v-btn color="primary">Primary Button</v-btn>
            <v-chip color="success">Success Chip</v-chip>
            <v-alert color="warning" variant="tonal" class="mt-2">Warning Alert</v-alert>
            <code>color="[color]"</code>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Chart, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

// Data for tables
const tableHeaders = [
  { title: 'ID', key: 'id' },
  { title: 'Name', key: 'name' },
  { title: 'Email', key: 'email' },
  { title: 'Status', key: 'status' },
  { title: 'Date', key: 'date' }
];

const tableItems = [
  { id: 1, name: 'John Doe', email: 'john@example.com', status: 'Active', date: '2023-01-15' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'Pending', date: '2023-02-20' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'Inactive', date: '2023-01-10' },
  { id: 4, name: 'Alice Brown', email: 'alice@example.com', status: 'Active', date: '2023-03-05' },
  {
    id: 5,
    name: 'Charlie Wilson',
    email: 'charlie@example.com',
    status: 'Active',
    date: '2023-02-28'
  },
  { id: 6, name: 'Diana Miller', email: 'diana@example.com', status: 'Pending', date: '2023-03-12' }
];

// Sample data for charts
const salesData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Monthly Sales',
      data: [65000, 89000, 76000, 92000, 85000, 98000],
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.3,
      fill: false
    }
  ]
};

const productData = {
  labels: ['Laptops', 'Smartphones', 'Tablets', 'Accessories', 'Software'],
  datasets: [
    {
      label: 'Product Sales',
      data: [42000, 38000, 27000, 18000, 15000],
      backgroundColor: [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)'
      ],
      borderColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 206, 86)',
        'rgb(75, 192, 192)',
        'rgb(153, 102, 255)'
      ],
      borderWidth: 1
    }
  ]
};

const revenueData = {
  labels: ['Hardware', 'Software', 'Services', 'Support', 'Training'],
  datasets: [
    {
      data: [35, 25, 20, 15, 5],
      backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 206, 86)',
        'rgb(75, 192, 192)',
        'rgb(153, 102, 255)'
      ]
    }
  ]
};

const trafficData = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      label: 'Daily Traffic',
      data: [1200, 1350, 1450, 1300, 1500, 1100, 950],
      fill: true,
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderColor: 'rgb(54, 162, 235)',
      tension: 0.4,
      pointRadius: 0
    }
  ]
};

// References for chart canvases
const lineChartRef = ref(null);
const barChartRef = ref(null);
const pieChartRef = ref(null);
const miniChartRef = ref(null);

// Chart configuration options
const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  }
};

const miniChartOptions = {
  ...defaultOptions,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    x: {
      display: false
    },
    y: {
      display: false
    }
  }
};

// Setup charts when component is mounted
onMounted(() => {
  // Line chart
  if (lineChartRef.value) {
    new Chart(lineChartRef.value, {
      type: 'line',
      data: salesData,
      options: defaultOptions
    });
  }

  // Bar chart
  if (barChartRef.value) {
    new Chart(barChartRef.value, {
      type: 'bar',
      data: productData,
      options: defaultOptions
    });
  }

  // Pie chart
  if (pieChartRef.value) {
    new Chart(pieChartRef.value, {
      type: 'pie',
      data: revenueData,
      options: defaultOptions
    });
  }

  // Mini chart
  if (miniChartRef.value) {
    new Chart(miniChartRef.value, {
      type: 'line',
      data: trafficData,
      options: miniChartOptions
    });
  }
});
</script>

<style scoped>
.components-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.subtitle {
  color: #666;
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.component-section {
  margin-bottom: 3rem;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff;
}

.component-section h2 {
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.component-group {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.component-item {
  flex: 1 1 300px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.component-item.wide {
  flex: 1 1 600px;
}

.component-item h3 {
  margin-bottom: 10px;
  font-size: 1rem;
}

.component-item code {
  margin-top: 10px;
  display: block;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #333;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.color-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: white;
}

.color-swatch {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.color-item.primary .color-swatch {
  background-color: rgb(210, 188, 155); /* #d2bc9b */
}

.color-item.secondary .color-swatch {
  background-color: rgb(52, 58, 64); /* #343a40 */
}

.color-item.success .color-swatch {
  background-color: rgb(76, 175, 80); /* #4CAF50 */
}

.color-item.info .color-swatch {
  background-color: rgb(33, 150, 243); /* #2196F3 */
}

.color-item.warning .color-swatch {
  background-color: rgb(251, 140, 0); /* #FB8C00 */
}

.color-item.error .color-swatch {
  background-color: rgb(176, 0, 32); /* #B00020 */
}

.color-item.bg-surface .color-swatch {
  background-color: rgb(255, 255, 255); /* #ffffff */
  border: 1px solid #eee;
}

.color-item.bg-background .color-swatch {
  background-color: rgb(248, 249, 250); /* #f8f9fa */
  border: 1px solid #eee;
}

.color-info {
  flex: 1;
}

.color-info h3 {
  margin-bottom: 8px;
  font-weight: 600;
}

.color-usage {
  font-size: 0.875rem;
  color: #666;
  margin-top: 8px;
  line-height: 1.4;
}

.subsection-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.section-description {
  font-size: 1rem;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

.example-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 24px;
}

.example-item {
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: white;
}

.example-item h4 {
  margin-bottom: 16px;
  font-weight: 600;
}
</style>
