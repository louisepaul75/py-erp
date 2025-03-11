<template>
  <div>
    <h1 class="text-h4 font-weight-bold mb-6">Sales Orders</h1>

    <!-- Loading and Error States -->
    <v-alert v-if="error" type="error" variant="tonal" class="mb-6">
      {{ error }}
    </v-alert>

    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-6"
    ></v-progress-linear>

    <!-- Sales Orders Table -->
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
          <v-chip :color="getStatusColor(item.status)" text-color="white" size="small">
            {{ capitalizeFirst(item.status) }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn size="small" color="primary" variant="text" @click="viewOrderDetails(item.id)">
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { salesApi } from '@/services/api';

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
const salesOrders = ref<any[]>([]);
const loading = ref(true);
const error = ref('');
const currentPage = ref(1);
const totalOrders = ref(0);
const pageSize = ref(10);

// Computed
const totalPages = computed(() => Math.ceil(totalOrders.value / pageSize.value));

// Load sales orders
const loadSalesOrders = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await salesApi.getSalesOrders({
      page: currentPage.value,
      page_size: pageSize.value
    });
    salesOrders.value = response.data.results;
    totalOrders.value = response.data.count;
  } catch (err) {
    console.error('Error loading sales orders:', err);
    error.value = 'Failed to load sales orders. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Navigation
const viewOrderDetails = (orderId: number) => {
  router.push({ name: 'SalesOrderDetail', params: { id: orderId } });
};

const editOrder = (orderId: number) => {
  router.push({ name: 'SalesOrderEdit', params: { id: orderId } });
};

// Page change handler
const changePage = () => {
  loadSalesOrders();
};

// Utility functions
const formatDate = (date: string) => {
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(date));
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'draft':
      return 'grey';
    case 'confirmed':
      return 'blue';
    case 'invoiced':
      return 'orange';
    case 'completed':
      return 'green';
    case 'canceled':
      return 'red';
    default:
      return 'grey';
  }
};

const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Initialize component
onMounted(() => {
  loadSalesOrders();
});
</script>

<style scoped>
.v-data-table {
  background: white !important;
}

.v-data-table-header th {
  white-space: nowrap;
  font-weight: 600 !important;
}

.v-data-table .v-table__wrapper > table {
  padding: 0.5rem;
}
</style>
