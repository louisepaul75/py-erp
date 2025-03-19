<template>
  <div>
    <h1 class="text-h4 font-weight-bold mb-6">{{ $t('sales.records.title') }}</h1>

    <!-- Loading and Error States -->
    <v-progress-linear
      v-if="salesRecordsLoading"
      indeterminate
      color="primary"
      class="mb-6"
    ></v-progress-linear>

    <v-alert v-if="salesRecordsError" type="error" variant="tonal" class="mb-6">
      {{ salesRecordsError }}
    </v-alert>

    <!-- Sales Records Table -->
    <v-card v-if="!salesRecordsLoading">
      <v-data-table
        :headers="salesRecordsHeaders"
        :items="salesRecords"
        :items-per-page="recordsPageSize"
        class="elevation-1"
        :loading="salesRecordsLoading"
      >
        <template v-slot:item.record_date="{ item }">
          {{ formatDate(item.record_date) }}
        </template>

        <template v-slot:item.total_amount="{ item }">
          {{ formatCurrency(item.total_amount) }}
        </template>

        <template v-slot:item.payment_status="{ item }">
          <v-chip :color="getPaymentStatusColor(item.payment_status)" text-color="white" size="small">
            {{ $t(`sales.records.paymentStatus.${item.payment_status}`) }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn size="small" color="primary" variant="text" @click="viewSalesRecordDetails(item)">
            {{ $t('sales.records.viewDetails') }}
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- No sales records message -->
    <v-alert
      v-if="salesRecords.length === 0 && !salesRecordsLoading && !salesRecordsError"
      type="info"
      variant="tonal"
      class="mt-6"
    >
      {{ $t('sales.records.noRecords') }}
    </v-alert>

    <!-- Sales Record Items Dialog -->
    <v-dialog v-model="showItemsDialog" max-width="900">
      <v-card>
        <v-card-title class="text-h5 py-4 px-6">
          {{ selectedRecord ? $t('sales.records.itemsDialog.title') + ` #${selectedRecord.record_number}` : $t('sales.records.itemsDialog.title') }}
          <v-spacer></v-spacer>
          <v-btn icon @click="showItemsDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-divider></v-divider>
        
        <v-card-text class="py-4">
          <v-data-table
            v-if="selectedRecordItems.length > 0"
            :headers="itemsHeaders"
            :items="selectedRecordItems"
            class="elevation-1"
          >
            <template v-slot:item.line_subtotal="{ item }">
              {{ formatCurrency(item.line_subtotal) }}
            </template>
            <template v-slot:item.line_total="{ item }">
              {{ formatCurrency(item.line_total) }}
            </template>
            <template v-slot:item.unit_price="{ item }">
              {{ formatCurrency(item.unit_price) }}
            </template>
            <template v-slot:item.tax_amount="{ item }">
              {{ formatCurrency(item.tax_amount) }}
            </template>
            <template v-slot:item.fulfillment_status="{ item }">
              <v-chip :color="getFulfillmentStatusColor(item.fulfillment_status)" size="small" text-color="white">
                {{ $t(`sales.records.itemsDialog.fulfillmentStatus.${item.fulfillment_status}`) }}
              </v-chip>
            </template>
          </v-data-table>
          
          <v-alert v-else type="info" variant="tonal" class="mt-4">
            {{ $t('sales.records.itemsDialog.noItems') }}
          </v-alert>
        </v-card-text>
        
        <v-divider></v-divider>
        
        <v-card-actions class="py-3 px-6">
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="outlined" @click="showItemsDialog = false">
            {{ $t('sales.records.itemsDialog.close') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { salesApi } from '@/services/api';

// Router and i18n
const router = useRouter();
const { t } = useI18n();

// Sales Records headers
const salesRecordsHeaders = computed(() => [
  { title: t('sales.records.headers.recordNumber'), key: 'record_number' },
  { title: t('sales.records.headers.date'), key: 'record_date' },
  { title: t('sales.records.headers.type'), key: 'record_type' },
  { title: t('sales.records.headers.customer'), key: 'customer_name' },
  { title: t('sales.records.headers.total'), key: 'total_amount' },
  { title: t('sales.records.headers.paymentStatus'), key: 'payment_status' },
  { title: t('sales.records.headers.actions'), key: 'actions', sortable: false }
]);

// Items headers
const itemsHeaders = computed(() => [
  { title: t('sales.records.itemsDialog.headers.position'), key: 'position' },
  { title: t('sales.records.itemsDialog.headers.description'), key: 'description' },
  { title: t('sales.records.itemsDialog.headers.quantity'), key: 'quantity' },
  { title: t('sales.records.itemsDialog.headers.unitPrice'), key: 'unit_price' },
  { title: t('sales.records.itemsDialog.headers.taxAmount'), key: 'tax_amount' },
  { title: t('sales.records.itemsDialog.headers.subtotal'), key: 'line_subtotal' },
  { title: t('sales.records.itemsDialog.headers.total'), key: 'line_total' },
  { title: t('sales.records.itemsDialog.headers.status'), key: 'fulfillment_status' }
]);

// Sales Records state
const salesRecords = ref<any[]>([]);
const salesRecordsLoading = ref(true);
const salesRecordsError = ref('');
const salesRecordsCurrentPage = ref(1);
const salesRecordsTotalCount = ref(0);
const recordsPageSize = ref(10);
const showItemsDialog = ref(false);
const selectedRecord = ref<any>(null);
const selectedRecordItems = ref<any[]>([]);

// Computed
const salesRecordsTotalPages = computed(() => Math.ceil(salesRecordsTotalCount.value / recordsPageSize.value));

// Load sales records
const loadSalesRecords = async () => {
  salesRecordsLoading.value = true;
  salesRecordsError.value = '';

  try {
    const response = await salesApi.getSalesRecords({
      page: salesRecordsCurrentPage.value,
      page_size: recordsPageSize.value
    });
    
    salesRecords.value = response.data.results;
    salesRecordsTotalCount.value = response.data.count;
  } catch (err) {
    salesRecordsError.value = t('sales.records.error');
  } finally {
    salesRecordsLoading.value = false;
  }
};

// Mock data function for development
const getMockSalesRecords = () => {
  return [
    {
      id: 1,
      record_number: 'INV-2023-001',
      record_date: '2023-07-15',
      record_type: 'INVOICE',
      customer_name: 'Acme Corp',
      total_amount: 1250.99,
      payment_status: 'PAID'
    },
    {
      id: 2,
      record_number: 'PRO-2023-002',
      record_date: '2023-07-16',
      record_type: 'PROPOSAL',
      customer_name: 'Globex Inc',
      total_amount: 3450.50,
      payment_status: 'PENDING'
    },
    {
      id: 3,
      record_number: 'DNO-2023-003',
      record_date: '2023-07-17',
      record_type: 'DELIVERY_NOTE',
      customer_name: 'Wayne Enterprises',
      total_amount: 2120.75,
      payment_status: 'PENDING'
    }
  ];
};

// Mock items data function
const getMockRecordItems = (recordId: number) => {
  return [
    {
      id: 1,
      position: 1,
      description: 'Super Widget Pro',
      quantity: 2,
      unit_price: 299.99,
      tax_amount: 48.00,
      line_subtotal: 599.98,
      line_total: 647.98,
      fulfillment_status: 'FULFILLED'
    },
    {
      id: 2,
      position: 2,
      description: 'Mega Gadget 5000',
      quantity: 1,
      unit_price: 499.99,
      tax_amount: 80.00,
      line_subtotal: 499.99,
      line_total: 579.99,
      fulfillment_status: 'PENDING'
    },
    {
      id: 3,
      position: 3,
      description: 'Installation Service',
      quantity: 1,
      unit_price: 100.00,
      tax_amount: 16.00,
      line_subtotal: 100.00,
      line_total: 116.00,
      fulfillment_status: 'FULFILLED'
    }
  ];
};

// View sales record details
const viewSalesRecordDetails = (record: any) => {
  selectedRecord.value = record;
  
  // In a real implementation, we would fetch the items from the API
  // For now, we'll use mock data
  loadSalesRecordItems(record.id);
  
  showItemsDialog.value = true;
};

// Load sales record items
const loadSalesRecordItems = async (recordId: number) => {
  try {
    const response = await salesApi.getSalesRecordItems(recordId);
    selectedRecordItems.value = response.data;
  } catch (err) {
    console.error('Error loading sales record items:', err);
    // Fallback with mock data for development
    if (process.env.NODE_ENV === 'development') {
      selectedRecordItems.value = getMockRecordItems(recordId);
    } else {
      selectedRecordItems.value = [];
    }
  }
};

// Page change handlers
const changeSalesRecordsPage = () => {
  loadSalesRecords();
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

const getPaymentStatusColor = (status: string): string => {
  switch (status) {
    case 'PAID':
      return 'green';
    case 'PENDING':
      return 'orange';
    case 'OVERDUE':
      return 'red';
    case 'CANCELLED':
      return 'grey';
    default:
      return 'grey';
  }
};

const getFulfillmentStatusColor = (status: string): string => {
  switch (status) {
    case 'FULFILLED':
      return 'green';
    case 'PARTIAL':
      return 'orange';
    case 'PENDING':
      return 'blue';
    case 'CANCELLED':
      return 'grey';
    default:
      return 'grey';
  }
};

const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

// Initialize component
onMounted(() => {
  loadSalesRecords();
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
