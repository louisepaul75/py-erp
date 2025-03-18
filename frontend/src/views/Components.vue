<template>
  <div class="components-page">
    <h1>UI Components Style Guide</h1>
    <p class="subtitle">Reference for all UI components used in the pyERP project</p>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('buttons')">
        <h2>Buttons</h2>
        <v-icon :icon="expandedSections.buttons ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.buttons" class="section-content">
          <div class="component-group">
            <div class="component-item">
              <h3>Primary Button</h3>
              <app-button color="primary">Primary Button</app-button>
              <code>app-button color="primary"</code>
            </div>
            <div class="component-item">
              <h3>Secondary Button</h3>
              <app-button color="secondary">Secondary Button</app-button>
              <code>app-button color="secondary"</code>
            </div>
            <div class="component-item">
              <h3>Outlined Button</h3>
              <app-button variant="outlined" color="primary">Outlined Button</app-button>
              <code>app-button variant="outlined" color="primary"</code>
            </div>
            <div class="component-item">
              <h3>Text Button</h3>
              <app-button variant="text" color="primary">Text Button</app-button>
              <code>app-button variant="text" color="primary"</code>
            </div>
            <div class="component-item">
              <h3>Icon Button</h3>
              <app-button icon="mdi-plus" color="primary"></app-button>
              <code>app-button icon="mdi-plus" color="primary"</code>
            </div>
            <div class="component-item">
              <h3>Button with Icons</h3>
              <div class="d-flex gap-4">
                <app-button prepend-icon="mdi-download">Download</app-button>
                <app-button append-icon="mdi-arrow-right">Next</app-button>
                <app-button icon="mdi-refresh"></app-button>
              </div>
              <code>app-button prepend-icon="mdi-[icon-name]" or append-icon="mdi-[icon-name]"</code>
            </div>
          </div>
        </div>
      </v-expand-transition>
    </div>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('icons')">
        <h2>Icons</h2>
        <v-icon :icon="expandedSections.icons ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.icons" class="section-content">
          <div class="component-group">
            <div class="component-item">
              <h3>Basic Icons</h3>
              <div class="d-flex gap-4">
                <app-icon icon="mdi-home"></app-icon>
                <app-icon icon="mdi-account"></app-icon>
                <app-icon icon="mdi-cog"></app-icon>
                <app-icon icon="mdi-bell"></app-icon>
              </div>
              <code>app-icon icon="mdi-[icon-name]"</code>
            </div>
            <div class="component-item">
              <h3>Colored Icons</h3>
              <div class="d-flex gap-4">
                <app-icon color="primary" icon="mdi-check-circle"></app-icon>
                <app-icon color="error" icon="mdi-alert-circle"></app-icon>
                <app-icon color="warning" icon="mdi-alert"></app-icon>
                <app-icon color="success" icon="mdi-check"></app-icon>
              </div>
              <code>app-icon color="[color]" icon="mdi-[icon-name]"</code>
            </div>
            <div class="component-item">
              <h3>Icon Sizes</h3>
              <div class="d-flex align-center gap-4">
                <app-icon size="x-small" icon="mdi-star"></app-icon>
                <app-icon size="small" icon="mdi-star"></app-icon>
                <app-icon icon="mdi-star"></app-icon>
                <app-icon size="large" icon="mdi-star"></app-icon>
                <app-icon size="x-large" icon="mdi-star"></app-icon>
              </div>
              <code>app-icon size="[x-small|small|default|large|x-large]"</code>
            </div>
          </div>
        </div>
      </v-expand-transition>
    </div>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('textFields')">
        <h2>Text Fields</h2>
        <v-icon :icon="expandedSections.textFields ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.textFields" class="section-content">
          <div class="component-group">
            <div class="component-item">
              <h3>Basic Input</h3>
              <app-text-field label="Basic Input" placeholder="Enter text"></app-text-field>
              <code>app-text-field label="Basic Input" placeholder="Enter text"</code>
            </div>
            <div class="component-item">
              <h3>With Icon</h3>
              <app-text-field label="With Icon" prepend-icon="mdi-account"></app-text-field>
              <code>app-text-field label="With Icon" prepend-icon="mdi-account"</code>
            </div>
            <div class="component-item">
              <h3>Required Field</h3>
              <app-text-field label="Required Field" required></app-text-field>
              <code>app-text-field label="Required Field" required</code>
            </div>
            <div class="component-item">
              <h3>Textarea</h3>
              <app-textarea label="Textarea" rows="3"></app-textarea>
              <code>app-textarea label="Textarea" rows="3"</code>
            </div>
          </div>
        </div>
      </v-expand-transition>
    </div>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('cards')">
        <h2>Cards</h2>
        <v-icon :icon="expandedSections.cards ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.cards" class="section-content">
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
      </v-expand-transition>
    </div>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('dataDisplay')">
        <h2>Data Display</h2>
        <v-icon :icon="expandedSections.dataDisplay ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.dataDisplay" class="section-content">
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
            
            <div class="component-item wide">
              <h3>Searchable Data Table (Small)</h3>
              <app-data-table
                :headers="tableHeaders"
                :items="tableItems"
                size="small"
                searchable
              ></app-data-table>
              <code>app-data-table size="small" searchable</code>
            </div>
            
            <div class="component-item wide">
              <h3>Searchable Data Table (Default)</h3>
              <app-data-table
                :headers="tableHeaders"
                :items="tableItems"
                searchable
              ></app-data-table>
              <code>app-data-table searchable</code>
            </div>
            
            <div class="component-item wide">
              <h3>Searchable Data Table (Large)</h3>
              <app-data-table
                :headers="tableHeaders"
                :items="tableItems"
                size="large"
                searchable
              ></app-data-table>
              <code>app-data-table size="large" searchable</code>
            </div>
            
            <div class="component-item wide">
              <h3>Filterable Data Table</h3>
              <app-filter-table
                :headers="filterTableHeaders"
                :items="tableItems"
              ></app-filter-table>
              <code>app-filter-table with filterable headers</code>
            </div>
            
            <div class="component-item wide">
              <h3>Server-side Data Table</h3>
              <app-server-table
                :headers="tableHeaders"
                :items="tableItems.slice(0, serverTableOptions.itemsPerPage)"
                :total-items="tableItems.length"
                :loading="serverTableLoading"
                @update:options="handleServerTableOptions"
                @search="handleServerTableSearch"
              ></app-server-table>
              <code>app-server-table with server-side pagination, sorting, and search</code>
            </div>
          </div>
        </div>
      </v-expand-transition>
    </div>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('chartCards')">
        <h2>Chart Cards</h2>
        <v-icon :icon="expandedSections.chartCards ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.chartCards" class="section-content">
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
      </v-expand-transition>
    </div>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('metricsCards')">
        <h2>Metrics Cards</h2>
        <v-icon :icon="expandedSections.metricsCards ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.metricsCards" class="section-content">
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
      </v-expand-transition>
    </div>

    <div class="component-section">
      <div class="section-header" @click="toggleSection('colorPalette')">
        <h2>Color Palette</h2>
        <v-icon :icon="expandedSections.colorPalette ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-icon>
      </div>
      
      <v-expand-transition>
        <div v-show="expandedSections.colorPalette" class="section-content">
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
                <app-button color="primary">Primary Button</app-button>
                <v-chip color="success">Success Chip</v-chip>
                <v-alert color="warning" variant="tonal" class="mt-2">Warning Alert</v-alert>
                <code>color="[color]"</code>
              </div>
            </div>
          </div>
        </div>
      </v-expand-transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Chart, registerables } from 'chart.js';
import { 
  AppButton, 
  AppDataTable, 
  AppFilterTable, 
  AppServerTable,
  AppIcon,
  AppTextField,
  AppTextarea
} from '@/components/ui';

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

// Enhanced headers with filter options
const filterTableHeaders = [
  { title: 'ID', key: 'id', filterable: false },
  { title: 'Name', key: 'name', filterType: 'text' },
  { 
    title: 'Status', 
    key: 'status', 
    filterType: 'select',
    filterOptions: [
      { title: 'Active', value: 'Active' },
      { title: 'Pending', value: 'Pending' },
      { title: 'Inactive', value: 'Inactive' }
    ]
  },
  { title: 'Email', key: 'email', filterType: 'text' },
  { title: 'Date', key: 'date', filterType: 'date' }
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
  { id: 6, name: 'Diana Miller', email: 'diana@example.com', status: 'Pending', date: '2023-03-12' },
  { id: 7, name: 'Edward Davis', email: 'edward@example.com', status: 'Active', date: '2023-01-25' },
  { id: 8, name: 'Fiona Clark', email: 'fiona@example.com', status: 'Inactive', date: '2023-02-05' },
  { id: 9, name: 'George White', email: 'george@example.com', status: 'Pending', date: '2023-03-18' },
  { id: 10, name: 'Hannah Green', email: 'hannah@example.com', status: 'Active', date: '2023-01-30' },
  { id: 11, name: 'Ian Black', email: 'ian@example.com', status: 'Active', date: '2023-02-12' },
  { id: 12, name: 'Julia Reed', email: 'julia@example.com', status: 'Inactive', date: '2023-03-22' }
];

// Server table options
const serverTableOptions = ref({
  page: 1,
  itemsPerPage: 5,
  sortBy: []
});
const serverTableLoading = ref(false);
const serverTableSearch = ref('');

// Handle server table options change
function handleServerTableOptions(options) {
  serverTableOptions.value = options;
  simulateServerRequest();
}

// Handle server table search
function handleServerTableSearch(query) {
  serverTableSearch.value = query;
  serverTableOptions.value.page = 1; // Reset to first page on new search
  simulateServerRequest();
}

// Simulate server request with loading state
function simulateServerRequest() {
  serverTableLoading.value = true;
  setTimeout(() => {
    serverTableLoading.value = false;
  }, 500);
}

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

// Section data for collapsible sections
const expandedSections = ref({
  buttons: true,
  icons: false,
  textFields: false,
  cards: false,
  dataDisplay: false,
  chartCards: false,
  metricsCards: false,
  colorPalette: false
});

// Toggle section expanded state
function toggleSection(key) {
  expandedSections.value[key] = !expandedSections.value[key];
}
</script>

<style scoped>
.components-page {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #ffffff;
}

h1 {
  font-size: 2rem;
  margin-bottom: 8px;
  color: var(--v-primary-base);
  font-weight: 500;
}

.subtitle {
  font-size: 1.1rem;
  color: rgba(0, 0, 0, 0.6);
  margin-bottom: 32px;
}

.component-section {
  margin-bottom: 24px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-radius: 8px;
}

.section-header:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.section-content {
  padding: 0 24px 24px 24px;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 0;
  color: #333;
  font-weight: 500;
}

.component-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 28px;
  margin-top: 20px;
}

.component-item {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  transition: box-shadow 0.2s ease;
}

.component-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}

.component-item h3 {
  font-size: 1.05rem;
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.87);
}

.component-item code {
  display: block;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  margin-top: 16px;
  font-size: 0.9rem;
  color: #333;
  word-break: break-all;
}

.d-flex {
  display: flex;
}

.gap-4 {
  gap: 16px;
}

.align-center {
  align-items: center;
}

/* Button specific styles */
:deep(.app-button) {
  margin: 4px;
}

:deep(.v-btn) {
  text-transform: none !important;
  letter-spacing: normal !important;
}

:deep(.v-btn__content) {
  font-weight: 500;
  white-space: nowrap;
}

:deep(.v-icon) {
  font-size: 20px;
}

.color-swatch {
  width: 100%;
  height: 80px;
  border-radius: 4px;
  margin-bottom: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.color-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.color-usage {
  font-size: 0.9rem;
  color: rgba(0, 0, 0, 0.6);
}

.subsection-title {
  font-size: 1.2rem;
  margin-top: 24px;
  margin-bottom: 16px;
}

.section-description {
  font-size: 1rem;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

.example-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 28px;
}

.example-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Table component styles */
:deep(.v-data-table) {
  border-radius: 4px;
  overflow: hidden;
}

:deep(.app-data-table),
:deep(.app-filter-table),
:deep(.app-server-table) {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  overflow: hidden;
}

:deep(.v-text-field .v-field__outline),
:deep(.v-textarea .v-field__outline) {
  --v-field-border-width: 1px;
}

.component-item.wide {
  grid-column: span 2;
}

/* Make sure wide items don't break layout on smaller screens */
@media (max-width: 768px) {
  .component-item.wide {
    grid-column: auto;
  }
  
  .component-group {
    grid-template-columns: 1fr;
  }
}
</style>
