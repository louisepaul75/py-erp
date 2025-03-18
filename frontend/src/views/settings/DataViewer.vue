<template>
  <v-container fluid class="pa-4">
    <v-card class="mx-auto" elevation="3">
      <!-- Header -->
      <v-card-title class="text-h5 font-weight-bold py-4 px-4">
        Data Viewer
        <v-card-subtitle class="pt-1">View and download data from database tables.</v-card-subtitle>
      </v-card-title>

      <v-card-text>
        <!-- Table Selection -->
        <v-row>
          <v-col cols="12" sm="8" md="9">
            <v-select
              v-model="selectedTable"
              :items="availableTables"
              label="Select a Table"
              variant="outlined"
              density="comfortable"
              placeholder="-- Select a table --"
              @update:model-value="loadTableData"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4" md="3" class="d-flex align-center">
            <v-btn 
              prepend-icon="mdi-refresh" 
              variant="outlined" 
              @click="refreshTables"
              class="mt-sm-0 mt-n3"
            >
              Refresh
            </v-btn>
          </v-col>
        </v-row>

        <!-- Error State -->
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          closable
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <!-- Loading State -->
        <div v-if="loading" class="d-flex justify-center align-center py-10">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <span class="ml-2 text-medium-emphasis">Loading...</span>
        </div>

        <div v-if="selectedTable && !loading">
          <!-- Search and Filter -->
          <v-row>
            <v-col cols="12" sm="8" md="9">
              <v-text-field
                v-model="searchQuery"
                label="Search"
                variant="outlined"
                density="comfortable"
                placeholder="Search in all fields"
                prepend-inner-icon="mdi-magnify"
                @input="debounceSearch"
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4" md="3">
              <v-select
                v-model="filterField"
                :items="columns"
                label="Filter by Field"
                variant="outlined"
                density="comfortable"
                placeholder="All fields"
                hide-details
              >
                <template v-slot:prepend-item>
                  <v-list-item
                    title="All fields"
                    value=""
                    @click="filterField = ''"
                  ></v-list-item>
                  <v-divider class="mt-2"></v-divider>
                </template>
              </v-select>
            </v-col>
          </v-row>

          <!-- Data Table -->
          <div class="my-4">
            <div class="d-flex flex-column flex-sm-row justify-space-between align-md-center mb-4">
              <div class="text-medium-emphasis text-subtitle-2 mb-2 mb-sm-0">
                Showing {{ filteredData.length }} of {{ tableData.length }} records
              </div>
              <v-btn
                @click="downloadData"
                color="primary"
                prepend-icon="mdi-download"
              >
                Download CSV
              </v-btn>
            </div>

            <v-data-table
              :headers="columns.map(column => ({ title: column, key: column, sortable: true }))"
              :items="paginatedData"
              :items-per-page="pageSize"
              :page="currentPage"
              @update:page="currentPage = $event"
              @update:sort-by="updateSort"
              class="elevation-1"
              hover
            >
              <template v-slot:no-data>
                <div class="text-center pa-5">No data available</div>
              </template>
            </v-data-table>

            <!-- Pagination is handled by v-data-table above -->
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';
import api from '@/services/api';

export default {
  name: 'DataViewer',
  setup() {
    // States
    const availableTables = ref([]);
    const selectedTable = ref('');
    const tableData = ref([]);
    const columns = ref([]);
    const loading = ref(false);
    const error = ref('');
    const searchQuery = ref('');
    const filterField = ref('');
    const currentPage = ref(1);
    const pageSize = ref(10);
    const sortColumn = ref('');
    const sortDirection = ref('asc');

    // Fetch available tables
    const fetchTables = async () => {
      loading.value = true;
      error.value = '';
      try {
        const response = await api.get('/admin/database/tables/');
        if (response.data && response.data.tables) {
          availableTables.value = response.data.tables;
        } else {
          error.value = 'Failed to fetch tables list';
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to fetch tables';
        console.error('Error fetching tables:', err);
      } finally {
        loading.value = false;
      }
    };

    // Load table data
    const loadTableData = async () => {
      if (!selectedTable.value) return;
      
      loading.value = true;
      error.value = '';
      currentPage.value = 1;
      sortColumn.value = '';
      sortDirection.value = 'asc';
      
      try {
        const response = await api.get(`/admin/database/table-data/${selectedTable.value}/`);
        if (response.data && response.data.data) {
          tableData.value = response.data.data;
          
          // Extract columns from the first row
          if (tableData.value.length > 0) {
            columns.value = Object.keys(tableData.value[0]);
          } else {
            columns.value = [];
          }
        } else {
          error.value = 'Failed to fetch table data';
          tableData.value = [];
          columns.value = [];
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to fetch table data';
        console.error('Error fetching table data:', err);
        tableData.value = [];
        columns.value = [];
      } finally {
        loading.value = false;
      }
    };

    // Refresh tables list
    const refreshTables = () => {
      fetchTables();
    };

    // Filtered data based on search query and filter field
    const filteredData = computed(() => {
      if (!searchQuery.value) return tableData.value;
      
      const query = searchQuery.value.toLowerCase();
      return tableData.value.filter(row => {
        if (filterField.value) {
          // Search in specific field
          const value = row[filterField.value];
          return value !== null && String(value).toLowerCase().includes(query);
        } else {
          // Search in all fields
          return Object.values(row).some(value => 
            value !== null && String(value).toLowerCase().includes(query)
          );
        }
      });
    });

    // Sorted data
    const sortedData = computed(() => {
      if (!sortColumn.value) return filteredData.value;

      return [...filteredData.value].sort((a, b) => {
        const aValue = a[sortColumn.value];
        const bValue = b[sortColumn.value];

        // Handle null values
        if (aValue === null && bValue === null) return 0;
        if (aValue === null) return 1;
        if (bValue === null) return -1;

        // Handle numeric values
        if (!isNaN(aValue) && !isNaN(bValue)) {
          return sortDirection.value === 'asc' 
            ? Number(aValue) - Number(bValue) 
            : Number(bValue) - Number(aValue);
        }

        // Handle string values
        return sortDirection.value === 'asc'
          ? String(aValue).localeCompare(String(bValue))
          : String(bValue).localeCompare(String(aValue));
      });
    });

    // Pagination
    const totalPages = computed(() => 
      Math.ceil(sortedData.value.length / pageSize.value)
    );

    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      return sortedData.value.slice(start, end);
    });

    // Updated for Vuetify data-table
    const updateSort = (event) => {
      if (event.length > 0) {
        sortColumn.value = event[0].key;
        sortDirection.value = event[0].order;
      } else {
        sortColumn.value = '';
        sortDirection.value = 'asc';
      }
    };

    // Debounced search
    let searchTimeout;
    const debounceSearch = () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentPage.value = 1; // Reset to first page when searching
      }, 300);
    };

    // Download data as CSV
    const downloadData = () => {
      if (!tableData.value.length) return;
      
      // Prepare CSV content
      const csvContent = [
        // Headers
        columns.value.join(','),
        // Data rows
        ...filteredData.value.map(row => 
          columns.value.map(col => {
            // Handle special characters and null values
            const value = row[col] === null ? '' : String(row[col]);
            // Escape quotes and wrap in quotes if contains commas, quotes, or newlines
            if (value.includes('"') || value.includes(',') || value.includes('\n')) {
              return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
          }).join(',')
        )
      ].join('\n');
      
      // Create a blob and download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedTable.value}_data.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };

    // Reset pagination when filter changes
    watch([searchQuery, filterField], () => {
      currentPage.value = 1;
    });

    // Fetch tables on component mount
    onMounted(() => {
      fetchTables();
    });

    return {
      availableTables,
      selectedTable,
      tableData,
      columns,
      loading,
      error,
      searchQuery,
      filterField,
      currentPage,
      pageSize,
      sortColumn,
      sortDirection,
      filteredData,
      paginatedData,
      totalPages,
      loadTableData,
      refreshTables,
      updateSort,
      debounceSearch,
      downloadData
    };
  }
};
</script> 