<template>
  <div class="sales-list">
    <h1 class="text-h4 mb-4">Sales Orders</h1>

    <!-- Search and filter form -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              label="Search orders..."
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-magnify"
              @input="debounceSearch"
              hide-details
            ></v-text-field>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedStatus"
              :items="statusOptions"
              label="Status"
              variant="outlined"
              density="comfortable"
              @update:model-value="loadSalesOrders"
              hide-details
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="2">
            <v-text-field
              v-model="dateFrom"
              label="From"
              type="date"
              variant="outlined"
              density="comfortable"
              @update:model-value="loadSalesOrders"
              hide-details
            ></v-text-field>
          </v-col>
          
          <v-col cols="12" md="2">
            <v-text-field
              v-model="dateTo"
              label="To"
              type="date"
              variant="outlined"
              density="comfortable"
              @update:model-value="loadSalesOrders"
              hide-details
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Loading indicator -->
    <div v-if="loading" class="d-flex justify-center my-6">
      <v-progress-circular
        indeterminate
        color="primary"
        size="64"
      ></v-progress-circular>
    </div>

    <!-- Error message -->
    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="mb-6"
    >
      {{ error }}
    </v-alert>

    <!-- Sales orders table -->
    <v-card v-else>
      <v-data-table
        :headers="headers"
        :items="salesOrders"
        :items-per-page="pageSize"
        class="elevation-1"
        :loading="loading"
      >
        <template v-slot:item.order_date="{ item }">
          {{ formatDate(item.order_date) }}
        </template>
        
        <template v-slot:item.total_amount="{ item }">
          {{ formatCurrency(item.total_amount) }}
        </template>
        
        <template v-slot:item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            text-color="white"
            size="small"
          >
            {{ capitalizeFirst(item.status) }}
          </v-chip>
        </template>
        
        <template v-slot:item.actions="{ item }">
          <v-btn
            size="small"
            color="primary"
            variant="text"
            @click="viewOrderDetails(item.id)"
          >
            View
          </v-btn>
          
          <v-btn
            v-if="item.status === 'draft'"
            size="small"
            color="secondary"
            variant="text"
            @click="editOrder(item.id)"
          >
            Edit
          </v-btn>
        </template>
      </v-data-table>
      
      <!-- Pagination -->
      <v-card-actions v-if="salesOrders.length > 0" class="justify-center">
        <v-pagination
          v-model="currentPage"
          :length="totalPages"
          @update:model-value="changePage"
          rounded="circle"
        ></v-pagination>
      </v-card-actions>
    </v-card>

    <!-- No results message -->
    <v-alert
      v-if="salesOrders.length === 0 && !loading && !error"
      type="info"
      variant="tonal"
      class="mt-6"
    >
      No sales orders found matching your criteria.
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { salesApi } from '@/services/api';

// Define types
interface SalesOrder {
  id: number;
  order_number: string;
  order_date: string;
  customer_name: string;
  total_amount: number;
  status: 'draft' | 'confirmed' | 'invoiced' | 'completed' | 'canceled';
}

// Router
const router = useRouter();

// Table headers
const headers = [
  { title: 'Order #', key: 'order_number' },
  { title: 'Date', key: 'order_date' },
  { title: 'Customer', key: 'customer_name' },
  { title: 'Total', key: 'total_amount' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false }
];

// Status options
const statusOptions = [
  { title: 'All Statuses', value: '' },
  { title: 'Draft', value: 'draft' },
  { title: 'Confirmed', value: 'confirmed' },
  { title: 'Invoiced', value: 'invoiced' },
  { title: 'Completed', value: 'completed' },
  { title: 'Canceled', value: 'canceled' }
];

// State
const salesOrders = ref<SalesOrder[]>([]);
const loading = ref(true);
const error = ref('');
const searchQuery = ref('');
const selectedStatus = ref('');
const dateFrom = ref('');
const dateTo = ref('');
const currentPage = ref(1);
const totalOrders = ref(0);
const pageSize = ref(10);

// Computed
const totalPages = computed(() => Math.ceil(totalOrders.value / pageSize.value));

// Search debounce
let searchTimeout: number | null = null;

const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1; // Reset to first page on new search
    loadSalesOrders();
  }, 300) as unknown as number;
};

// Load sales orders with current filters
const loadSalesOrders = async () => {
  loading.value = true;
  error.value = '';

  try {
    const params = {
      page: currentPage.value,
      q: searchQuery.value,
      status: selectedStatus.value,
      date_from: dateFrom.value,
      date_to: dateTo.value,
    };

    const response = await salesApi.getSalesOrders(params);
    salesOrders.value = response.data.results;
    totalOrders.value = response.data.count;
  } catch (err) {
    console.error('Error loading sales orders:', err);
    error.value = 'Failed to load sales orders. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Change page
const changePage = (page: number) => {
  currentPage.value = page;
  loadSalesOrders();
};

// View order details
const viewOrderDetails = (id: number) => {
  router.push({ name: 'SalesOrderDetail', params: { id } });
};

// Edit order
const editOrder = (id: number) => {
  router.push({ name: 'SalesOrderEdit', params: { id } });
};

// Get status color
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'draft': return 'grey';
    case 'confirmed': return 'blue';
    case 'invoiced': return 'orange';
    case 'completed': return 'green';
    case 'canceled': return 'red';
    default: return 'grey';
  }
};

// Format date
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

// Format currency
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount);
};

// Capitalize first letter
const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Initialize component
onMounted(() => {
  loadSalesOrders();
});
</script>

<style scoped>
.sales-list {
  padding: 20px 0;
}
</style>
