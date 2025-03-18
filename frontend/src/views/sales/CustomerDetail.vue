<template>
  <div class="customer-detail">
    <v-row class="mb-4">
      <v-col cols="12" sm="6">
        <h1 class="text-h4">Customer Details</h1>
      </v-col>
      <v-col cols="12" sm="6" class="d-flex justify-end align-center flex-wrap gap-2">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-arrow-left"
          @click="goBack"
          class="ma-1"
        >
          Back to List
        </v-btn>
        <v-btn
          v-if="!isEditing"
          color="secondary"
          prepend-icon="mdi-pencil"
          @click="startEditing"
          class="ma-1"
        >
          Edit
        </v-btn>
        <v-btn
          v-if="isEditing"
          color="success"
          prepend-icon="mdi-check"
          @click="saveChanges"
          class="ma-1"
        >
          Save
        </v-btn>
        <v-btn v-if="isEditing" color="error" variant="text" @click="cancelEditing" class="ma-1">
          Cancel
        </v-btn>
      </v-col>
    </v-row>

    <!-- Loading indicator -->
    <div v-if="loading" class="d-flex justify-center my-6">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <!-- Error message -->
    <v-alert v-else-if="error" type="error" variant="tonal" class="mb-6">
      {{ error }}
    </v-alert>

    <!-- Customer details -->
    <template v-else-if="customer">
      <!-- Basic Information -->
      <v-card class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-account-details"></v-icon>
          Basic Information
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="customerFields.name"
                label="Name"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="customerFields.customerNumber"
                label="Customer Number"
                readonly
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="customerFields.email"
                label="Email"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="customerFields.phone"
                label="Phone"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="customerFields.type"
                :items="customerTypes"
                label="Customer Type"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-select>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Address Information -->
      <v-card class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-map-marker"></v-icon>
          Address Information
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="customerFields.street"
                label="Street"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="customerFields.postalCode"
                label="Postal Code"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                v-model="customerFields.city"
                label="City"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="customerFields.country"
                :items="countries"
                label="Country"
                :readonly="!isEditing"
                variant="outlined"
                density="comfortable"
              ></v-select>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Financial Information -->
      <v-card class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-currency-eur"></v-icon>
          Financial Information
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                :model-value="formatCurrency(customer.revenue365Days)"
                label="Revenue (365 Days)"
                readonly
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="customerFields.creditLimit"
                label="Credit Limit"
                :readonly="!isEditing"
                type="number"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="customerFields.paymentTerms"
                label="Payment Terms (Days)"
                :readonly="!isEditing"
                type="number"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Recent Orders -->
      <v-card v-if="recentOrders.length > 0">
        <v-card-title>
          <v-icon start icon="mdi-cart"></v-icon>
          Recent Orders
        </v-card-title>
        <v-card-text>
          <v-data-table :headers="orderHeaders" :items="recentOrders" :items-per-page="5">
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
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </template>

    <!-- No customer found message -->
    <v-alert v-else type="warning" variant="tonal" class="mt-6"> Customer not found. </v-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { salesApi } from '@/services/api';

// Define types
interface CustomerFields {
  name: string;
  customerNumber: string;
  email: string;
  phone: string;
  type: 'b2b' | 'b2c';
  street: string;
  postalCode: string;
  city: string;
  country: string;
  creditLimit: number;
  paymentTerms: number;
  revenue365Days: number;
}

interface Address {
  id: number;
  is_primary: boolean;
  salutation?: string;
  first_name?: string;
  last_name?: string;
  company_name?: string;
  street: string;
  country: string;
  postal_code: string;
  city: string;
  phone?: string;
  fax?: string;
  email?: string;
  contact_person?: string;
  formal_salutation?: string;
}

interface Customer {
  id: number;
  customer_number: string;
  legacy_address_number?: string;
  customer_group?: string;
  delivery_block: boolean;
  price_group?: string;
  vat_id?: string;
  payment_method?: string;
  shipping_method?: string;
  credit_limit?: number;
  discount_percentage?: number;
  payment_terms_discount_days?: number;
  payment_terms_net_days?: number;
  notes?: string;
  addresses: Address[];
  revenue365Days?: number;
}

interface Order {
  id: number;
  order_number: string;
  order_date: string;
  total_amount: number;
  status: 'draft' | 'confirmed' | 'invoiced' | 'completed' | 'canceled';
}

// Router and route
const router = useRouter();
const route = useRoute();

// State
const customer = ref<Customer | null>(null);
const editedCustomer = ref<Customer | null>(null);
const loading = ref(true);
const error = ref('');
const isEditing = ref(false);
const recentOrders = ref<Order[]>([]);

// Computed properties for form fields
const customerFields = computed((): CustomerFields => {
  if (!editedCustomer.value) {
    return {
      name: '',
      customerNumber: '',
      email: '',
      phone: '',
      type: 'b2b' as const,
      street: '',
      postalCode: '',
      city: '',
      country: '',
      creditLimit: 0,
      paymentTerms: 0,
      revenue365Days: 0
    };
  }

  const primaryAddress =
    editedCustomer.value.addresses.find((a) => a.is_primary) || editedCustomer.value.addresses[0];

  return {
    name:
      primaryAddress?.company_name ||
      `${primaryAddress?.first_name || ''} ${primaryAddress?.last_name || ''}`.trim() ||
      '',
    customerNumber: editedCustomer.value.customer_number,
    email: primaryAddress?.email || '',
    phone: primaryAddress?.phone || '',
    type: editedCustomer.value.customer_group?.toLowerCase().includes('b2b') ? 'b2b' : 'b2c',
    street: primaryAddress?.street || '',
    postalCode: primaryAddress?.postal_code || '',
    city: primaryAddress?.city || '',
    country: primaryAddress?.country || '',
    creditLimit: Number(editedCustomer.value.credit_limit || 0),
    paymentTerms: Number(editedCustomer.value.payment_terms_net_days || 0),
    revenue365Days: Number(editedCustomer.value.revenue365Days || 0)
  };
});

// Constants
const customerTypes = [
  { title: 'Business (B2B)', value: 'b2b' },
  { title: 'Consumer (B2C)', value: 'b2c' }
];

const countries = [
  { title: 'Deutschland', value: 'Deutschland' },
  { title: 'Österreich', value: 'Österreich' },
  { title: 'Schweiz', value: 'Schweiz' }
];

const orderHeaders = [
  { title: 'Order #', key: 'order_number' },
  { title: 'Date', key: 'order_date' },
  { title: 'Total', key: 'total_amount' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false }
];

// Get customer ID from route params
const customerId = Number(route.params.id);

// Load customer details
const loadCustomerDetails = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await salesApi.getCustomer(customerId);
    const customerData = response.data as Customer;

    // Ensure customer has at least one address
    if (!customerData.addresses || customerData.addresses.length === 0) {
      customerData.addresses = [
        {
          id: 0,
          is_primary: true,
          street: '',
          country: '',
          postal_code: '',
          city: ''
        }
      ];
    }

    customer.value = customerData;
    editedCustomer.value = { ...customerData };

    // Try to load recent orders, but don't fail if endpoint doesn't exist
    try {
      const ordersResponse = await salesApi.getCustomerOrders(customerId);
      recentOrders.value = ordersResponse.data.results as Order[];
    } catch (orderErr) {
      console.log('Orders endpoint not available yet:', orderErr);
      recentOrders.value = []; // Set empty orders array
    }
  } catch (err) {
    console.error('Error loading customer details:', err);
    error.value = 'Failed to load customer details. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Navigation
const goBack = () => {
  router.push({ name: 'Sales', query: { tab: 'customers' } });
};

const viewOrderDetails = (orderId: number) => {
  router.push({ name: 'SalesOrderDetail', params: { id: orderId } });
};

// Editing
const startEditing = () => {
  isEditing.value = true;
  if (customer.value) {
    editedCustomer.value = { ...customer.value };
  }
};

const cancelEditing = () => {
  isEditing.value = false;
  if (customer.value) {
    editedCustomer.value = { ...customer.value };
  }
};

const saveChanges = async () => {
  if (!editedCustomer.value) return;

  loading.value = true;
  error.value = '';

  try {
    await salesApi.updateCustomer(customerId, editedCustomer.value);
    customer.value = { ...editedCustomer.value };
    isEditing.value = false;
  } catch (err) {
    console.error('Error updating customer:', err);
    error.value = 'Failed to update customer. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Format date
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(date);
};

// Format currency
const formatCurrency = (amount: number | undefined): string => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount || 0);
};

// Get status color
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

// Capitalize first letter
const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

// Initialize component
onMounted(() => {
  loadCustomerDetails();
});
</script>

<style scoped>
.customer-detail {
  padding: 20px 0;
}
</style>
