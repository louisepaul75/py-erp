<template>
  <div class="sales-order-detail">
    <div class="header">
      <h1>Sales Order Details</h1>
      <div class="actions">
        <button 
          v-if="order && order.status === 'draft'" 
          class="btn-edit"
          @click="editOrder"
        >
          Edit Order
        </button>
        <button 
          v-if="order && order.status === 'draft'" 
          class="btn-confirm"
          @click="confirmOrder"
        >
          Confirm Order
        </button>
        <button 
          v-if="order && ['confirmed', 'invoiced'].includes(order.status)" 
          class="btn-invoice"
          @click="createInvoice"
        >
          Create Invoice
        </button>
        <button class="btn-back" @click="goBack">
          Back to List
        </button>
      </div>
    </div>
    
    <!-- Loading indicator -->
    <div v-if="loading" class="loading">
      <p>Loading order details...</p>
    </div>
    
    <!-- Error message -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <!-- Order details -->
    <div v-else-if="order" class="order-container">
      <div class="order-header">
        <div class="order-info">
          <h2>Order #{{ order.order_number }}</h2>
          <div class="status">
            <span :class="'status-badge ' + order.status">
              {{ capitalizeFirst(order.status) }}
            </span>
          </div>
        </div>
        <div class="order-meta">
          <div class="meta-item">
            <span class="label">Date:</span>
            <span class="value">{{ formatDate(order.order_date) }}</span>
          </div>
          <div class="meta-item">
            <span class="label">Customer:</span>
            <span class="value">{{ order.customer_name }}</span>
          </div>
          <div class="meta-item">
            <span class="label">Reference:</span>
            <span class="value">{{ order.reference || 'N/A' }}</span>
          </div>
        </div>
      </div>
      
      <div class="order-sections">
        <!-- Customer Information -->
        <div class="section">
          <h3>Customer Information</h3>
          <div class="section-content">
            <div class="customer-details">
              <div class="address">
                <h4>Billing Address</h4>
                <p>{{ order.billing_address.name }}</p>
                <p>{{ order.billing_address.street }}</p>
                <p>{{ order.billing_address.postal_code }} {{ order.billing_address.city }}</p>
                <p>{{ order.billing_address.country }}</p>
              </div>
              <div class="address" v-if="order.shipping_address">
                <h4>Shipping Address</h4>
                <p>{{ order.shipping_address.name }}</p>
                <p>{{ order.shipping_address.street }}</p>
                <p>{{ order.shipping_address.postal_code }} {{ order.shipping_address.city }}</p>
                <p>{{ order.shipping_address.country }}</p>
              </div>
              <div class="contact">
                <h4>Contact</h4>
                <p v-if="order.contact_email">Email: {{ order.contact_email }}</p>
                <p v-if="order.contact_phone">Phone: {{ order.contact_phone }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Order Items -->
        <div class="section">
          <h3>Order Items</h3>
          <div class="section-content">
            <table class="items-table">
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
                  <td>Subtotal:</td>
                  <td>{{ formatCurrency(order.subtotal) }}</td>
                </tr>
                <tr v-if="order.tax_amount > 0">
                  <td colspan="4"></td>
                  <td>Tax ({{ order.tax_rate }}%):</td>
                  <td>{{ formatCurrency(order.tax_amount) }}</td>
                </tr>
                <tr v-if="order.shipping_amount > 0">
                  <td colspan="4"></td>
                  <td>Shipping:</td>
                  <td>{{ formatCurrency(order.shipping_amount) }}</td>
                </tr>
                <tr class="total-row">
                  <td colspan="4"></td>
                  <td>Total:</td>
                  <td>{{ formatCurrency(order.total_amount) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
        
        <!-- Notes -->
        <div class="section" v-if="order.notes">
          <h3>Notes</h3>
          <div class="section-content">
            <p class="notes">{{ order.notes }}</p>
          </div>
        </div>
        
        <!-- Related Documents -->
        <div class="section" v-if="order.documents && order.documents.length > 0">
          <h3>Related Documents</h3>
          <div class="section-content">
            <ul class="documents-list">
              <li v-for="doc in order.documents" :key="doc.id">
                <a :href="doc.url" target="_blank">{{ doc.name }}</a>
                <span class="document-date">{{ formatDate(doc.created_at) }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <!-- No order found message -->
    <div v-else class="not-found">
      <p>Sales order not found.</p>
    </div>
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

// Navigation
const goBack = () => {
  router.push({ name: 'SalesList' });
};

// Edit order
const editOrder = () => {
  router.push({ name: 'SalesOrderEdit', params: { id: orderId } });
};

// Confirm order
const confirmOrder = async () => {
  try {
    await salesApi.updateSalesOrder(orderId, { status: 'confirmed' });
    await loadOrderDetails(); // Reload order details
  } catch (err) {
    console.error('Error confirming order:', err);
    error.value = 'Failed to confirm order. Please try again.';
  }
};

// Create invoice
const createInvoice = async () => {
  try {
    // This would typically call a specific endpoint to create an invoice
    await salesApi.updateSalesOrder(orderId, { status: 'invoiced' });
    await loadOrderDetails(); // Reload order details
  } catch (err) {
    console.error('Error creating invoice:', err);
    error.value = 'Failed to create invoice. Please try again.';
  }
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.actions {
  display: flex;
  gap: 10px;
}

.actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-edit {
  background-color: #fff8e1;
  color: #f57f17;
}

.btn-edit:hover {
  background-color: #ffecb3;
}

.btn-confirm {
  background-color: #e8f5e9;
  color: #1b5e20;
}

.btn-confirm:hover {
  background-color: #c8e6c9;
}

.btn-invoice {
  background-color: #ede7f6;
  color: #4527a0;
}

.btn-invoice:hover {
  background-color: #d1c4e9;
}

.btn-back {
  background-color: #f5f5f5;
  color: #424242;
}

.btn-back:hover {
  background-color: #e0e0e0;
}

.loading, .error, .not-found {
  text-align: center;
  padding: 30px;
}

.error {
  color: #dc3545;
}

.order-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.order-header {
  padding: 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
}

.order-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.order-info h2 {
  margin: 0;
  font-size: 1.5rem;
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

.order-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  gap: 5px;
}

.meta-item .label {
  font-weight: 500;
}

.order-sections {
  padding: 20px;
}

.section {
  margin-bottom: 30px;
}

.section h3 {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
}

.section-content {
  padding: 0 10px;
}

.customer-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.address h4, .contact h4 {
  margin-bottom: 10px;
  font-size: 1rem;
}

.address p, .contact p {
  margin: 5px 0;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
}

.items-table th, .items-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eaeaea;
}

.items-table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.items-table tfoot td {
  text-align: right;
  font-weight: 500;
}

.items-table .total-row {
  font-weight: 700;
  font-size: 1.1rem;
}

.notes {
  white-space: pre-line;
  line-height: 1.5;
}

.documents-list {
  list-style: none;
  padding: 0;
}

.documents-list li {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eaeaea;
}

.documents-list a {
  color: #1976d2;
  text-decoration: none;
}

.documents-list a:hover {
  text-decoration: underline;
}

.document-date {
  color: #757575;
  font-size: 0.9rem;
}
</style> 