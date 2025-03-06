<template>
  <div class="sales-list">
    <h1>Sales Orders</h1>

    <!-- Search and filter form -->
    <div class="filters">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search orders..."
          @input="debounceSearch"
        />
      </div>

      <div class="filter-options">
        <select v-model="selectedStatus" @change="loadSalesOrders">
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="confirmed">Confirmed</option>
          <option value="invoiced">Invoiced</option>
          <option value="completed">Completed</option>
          <option value="canceled">Canceled</option>
        </select>

        <div class="date-filter">
          <label>From:</label>
          <input
            type="date"
            v-model="dateFrom"
            @change="loadSalesOrders"
          />

          <label>To:</label>
          <input
            type="date"
            v-model="dateTo"
            @change="loadSalesOrders"
          />
        </div>
      </div>
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="loading">
      <p>Loading sales orders...</p>
    </div>

    <!-- Error message -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <!-- Sales orders table -->
    <div v-else class="sales-table-container">
      <table class="sales-table">
        <thead>
          <tr>
            <th>Order #</th>
            <th>Date</th>
            <th>Customer</th>
            <th>Total</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="order in salesOrders"
            :key="order.id"
            :class="{ 'highlight': order.status === 'draft' }"
          >
            <td>{{ order.order_number }}</td>
            <td>{{ formatDate(order.order_date) }}</td>
            <td>{{ order.customer_name }}</td>
            <td>{{ formatCurrency(order.total_amount) }}</td>
            <td>
              <span :class="'status-badge ' + order.status">
                {{ capitalizeFirst(order.status) }}
              </span>
            </td>
            <td class="actions">
              <button
                class="btn-view"
                @click="viewOrderDetails(order.id)"
              >
                View
              </button>
              <button
                v-if="order.status === 'draft'"
                class="btn-edit"
                @click="editOrder(order.id)"
              >
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No results message -->
    <div v-if="salesOrders.length === 0 && !loading" class="no-results">
      <p>No sales orders found matching your criteria.</p>
    </div>

    <!-- Pagination -->
    <div v-if="salesOrders.length > 0" class="pagination">
      <button
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        Previous
      </button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        Next
      </button>
    </div>
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

h1 {
  margin-bottom: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-box input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filter-options {
  display: flex;
  gap: 15px;
  align-items: center;
}

.filter-options select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.date-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-filter input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.loading, .error, .no-results {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.sales-table-container {
  overflow-x: auto;
  margin-bottom: 30px;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #eaeaea;
}

.sales-table th,
.sales-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eaeaea;
}

.sales-table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.sales-table tr:hover {
  background-color: #f5f5f5;
}

.sales-table tr.highlight {
  background-color: #fff8e1;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.draft {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.status-badge.confirmed {
  background-color: #e8f5e9;
  color: #1b5e20;
}

.status-badge.invoiced {
  background-color: #ede7f6;
  color: #4527a0;
}

.status-badge.completed {
  background-color: #e0f2f1;
  color: #004d40;
}

.status-badge.canceled {
  background-color: #ffebee;
  color: #b71c1c;
}

.actions {
  display: flex;
  gap: 8px;
}

.actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-view {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.btn-view:hover {
  background-color: #bbdefb;
}

.btn-edit {
  background-color: #fff8e1;
  color: #f57f17;
}

.btn-edit:hover {
  background-color: #ffecb3;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination button:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
