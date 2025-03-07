<template>
  <div class="sales-order-detail">
    <v-row class="mb-4">
      <v-col cols="12" sm="6">
        <h1 class="text-h4">Sales Order Details</h1>
      </v-col>
      <v-col cols="12" sm="6" class="d-flex justify-end align-center flex-wrap gap-2">
        <v-btn
          v-if="order && order.status === 'draft'"
          color="secondary"
          prepend-icon="mdi-pencil"
          @click="editOrder"
          class="ma-1"
        >
          Edit Order
        </v-btn>
        <v-btn
          v-if="order && order.status === 'draft'"
          color="success"
          prepend-icon="mdi-check"
          @click="confirmOrder"
          class="ma-1"
        >
          Confirm Order
        </v-btn>
        <v-btn
          v-if="order && ['confirmed', 'invoiced'].includes(order.status)"
          color="info"
          prepend-icon="mdi-file-document"
          @click="createInvoice"
          class="ma-1"
        >
          Create Invoice
        </v-btn>
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-arrow-left"
          @click="goBack"
          class="ma-1"
        >
          Back to List
        </v-btn>
      </v-col>
    </v-row>

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

    <!-- Order details -->
    <template v-else-if="order">
      <v-card class="mb-6">
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <h2 class="text-h5">Order #{{ order.order_number }}</h2>
              <v-chip
                :color="getStatusColor(order.status)"
                text-color="white"
                class="mt-2"
              >
                {{ capitalizeFirst(order.status) }}
              </v-chip>
            </v-col>
            <v-col cols="12" md="6">
              <v-list density="compact" class="bg-transparent">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="mdi-calendar"></v-icon>
                  </template>
                  <v-list-item-title>Date: {{ formatDate(order.order_date) }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="mdi-account"></v-icon>
                  </template>
                  <v-list-item-title>Customer: {{ order.customer_name }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="mdi-tag"></v-icon>
                  </template>
                  <v-list-item-title>Reference: {{ order.reference || 'N/A' }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Customer Information -->
      <v-card class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-account-details"></v-icon>
          Customer Information
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4">
              <h4 class="text-subtitle-1 font-weight-bold mb-2">Billing Address</h4>
              <p>{{ order.billing_address.name }}</p>
              <p>{{ order.billing_address.street }}</p>
              <p>{{ order.billing_address.postal_code }} {{ order.billing_address.city }}</p>
              <p>{{ order.billing_address.country }}</p>
            </v-col>
            <v-col cols="12" md="4" v-if="order.shipping_address">
              <h4 class="text-subtitle-1 font-weight-bold mb-2">Shipping Address</h4>
              <p>{{ order.shipping_address.name }}</p>
              <p>{{ order.shipping_address.street }}</p>
              <p>{{ order.shipping_address.postal_code }} {{ order.shipping_address.city }}</p>
              <p>{{ order.shipping_address.country }}</p>
            </v-col>
            <v-col cols="12" md="4">
              <h4 class="text-subtitle-1 font-weight-bold mb-2">Contact</h4>
              <p v-if="order.contact_email">
                <v-icon size="small" class="mr-1">mdi-email</v-icon>
                {{ order.contact_email }}
              </p>
              <p v-if="order.contact_phone">
                <v-icon size="small" class="mr-1">mdi-phone</v-icon>
                {{ order.contact_phone }}
              </p>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Order Items -->
      <v-card class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-cart"></v-icon>
          Order Items
        </v-card-title>
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>Product</th>
                <th>SKU</th>
                <th>Quantity</th>
                <th>Unit Price</th>
                <th>Discount</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in order.items" :key="index">
                <td>{{ item.product_name }}</td>
                <td>{{ item.product_sku }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ formatCurrency(item.unit_price) }}</td>
                <td>{{ item.discount_percent ? item.discount_percent + '%' : '-' }}</td>
                <td>{{ formatCurrency(item.total_price) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="4"></td>
                <td class="text-right font-weight-medium">Subtotal:</td>
                <td>{{ formatCurrency(order.subtotal) }}</td>
              </tr>
              <tr v-if="order.tax_amount > 0">
                <td colspan="4"></td>
                <td class="text-right font-weight-medium">Tax ({{ order.tax_rate }}%):</td>
                <td>{{ formatCurrency(order.tax_amount) }}</td>
              </tr>
              <tr v-if="order.shipping_amount > 0">
                <td colspan="4"></td>
                <td class="text-right font-weight-medium">Shipping:</td>
                <td>{{ formatCurrency(order.shipping_amount) }}</td>
              </tr>
              <tr class="bg-grey-lighten-4">
                <td colspan="4"></td>
                <td class="text-right font-weight-bold">Total:</td>
                <td class="font-weight-bold">{{ formatCurrency(order.total_amount) }}</td>
              </tr>
            </tfoot>
          </v-table>
        </v-card-text>
      </v-card>

      <!-- Notes -->
      <v-card v-if="order.notes" class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-note-text"></v-icon>
          Notes
        </v-card-title>
        <v-card-text>
          <p>{{ order.notes }}</p>
        </v-card-text>
      </v-card>

      <!-- Related Documents -->
      <v-card v-if="order.documents && order.documents.length > 0" class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-file-document-multiple"></v-icon>
          Related Documents
        </v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="doc in order.documents"
              :key="doc.id"
              :href="doc.url"
              target="_blank"
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-file-document"></v-icon>
              </template>
              <v-list-item-title>{{ doc.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ formatDate(doc.created_at) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </template>

    <!-- No order found message -->
    <v-alert
      v-else
      type="warning"
      variant="tonal"
      class="mt-6"
    >
      Sales order not found.
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { salesApi } from '@/services/api';

// Define types
interface Address {
  name: string;
  street: string;
  postal_code: string;
  city: string;
  country: string;
}

interface OrderItem {
  product_name: string;
  product_sku: string;
  quantity: number;
  unit_price: number;
  discount_percent?: number;
  total_price: number;
}

interface Document {
  id: number;
  name: string;
  url: string;
  created_at: string;
}

interface SalesOrder {
  id: number;
  order_number: string;
  order_date: string;
  customer_name: string;
  reference?: string;
  status: 'draft' | 'confirmed' | 'invoiced' | 'completed' | 'canceled';
  billing_address: Address;
  shipping_address?: Address;
  contact_email?: string;
  contact_phone?: string;
  items: OrderItem[];
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  shipping_amount: number;
  total_amount: number;
  notes?: string;
  documents?: Document[];
}

// Router and route
const router = useRouter();
const route = useRoute();

// State
const order = ref<SalesOrder | null>(null);
const loading = ref(true);
const error = ref('');

// Get order ID from route params
const orderId = Number(route.params.id);

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

// Load order details
const loadOrderDetails = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await salesApi.getSalesOrder(orderId);
    order.value = response.data;
  } catch (err) {
    console.error('Error loading order details:', err);
    error.value = 'Failed to load order details. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Navigation
const goBack = () => {
  router.push({ name: 'SalesList' });
};

// Actions
const editOrder = () => {
  router.push({ name: 'SalesOrderEdit', params: { id: orderId } });
};

const confirmOrder = async () => {
  if (!order.value) return;
  
  try {
    await salesApi.updateSalesOrder(orderId, { status: 'confirmed' });
    await loadOrderDetails();
  } catch (err) {
    console.error('Error confirming order:', err);
    error.value = 'Failed to confirm order. Please try again.';
  }
};

const createInvoice = async () => {
  if (!order.value) return;
  
  try {
    await salesApi.updateSalesOrder(orderId, { status: 'invoiced' });
    await loadOrderDetails();
  } catch (err) {
    console.error('Error creating invoice:', err);
    error.value = 'Failed to create invoice. Please try again.';
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
  loadOrderDetails();
});
</script>

<style scoped>
.sales-order-detail {
  padding: 20px 0;
}
</style>
