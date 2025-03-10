<template>
  <div class="sales-order-edit">
    <v-row class="mb-4">
      <v-col cols="12" sm="6">
        <h1 class="text-h4">Edit Sales Order</h1>
      </v-col>
      <v-col cols="12" sm="6" class="d-flex justify-end align-center flex-wrap gap-2">
        <v-btn
          color="success"
          prepend-icon="mdi-check"
          @click="saveChanges"
          :loading="saving"
          class="ma-1"
        >
          Save Changes
        </v-btn>
        <v-btn
          color="error"
          variant="text"
          @click="cancelEdit"
          :disabled="saving"
          class="ma-1"
        >
          Cancel
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
      v-if="error"
      type="error"
      variant="tonal"
      class="mb-6"
    >
      {{ error }}
    </v-alert>

    <!-- Order form -->
    <template v-if="editedOrder">
      <!-- Basic Information -->
      <v-card class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-information"></v-icon>
          Basic Information
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="editedOrder.order_number"
                label="Order Number"
                readonly
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="editedOrder.reference"
                label="Reference"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="editedOrder.order_date"
                label="Order Date"
                type="date"
                variant="outlined"
                density="comfortable"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Customer Information -->
      <v-card class="mb-6">
        <v-card-title>
          <v-icon start icon="mdi-account"></v-icon>
          Customer Information
        </v-card-title>
        <v-card-text>
          <v-row>
            <!-- Billing Address -->
            <v-col cols="12" md="6">
              <h4 class="text-subtitle-1 mb-3">Billing Address</h4>
              <v-text-field
                v-model="editedOrder.billing_address.name"
                label="Name"
                variant="outlined"
                density="comfortable"
                class="mb-3"
              ></v-text-field>
              <v-text-field
                v-model="editedOrder.billing_address.street"
                label="Street"
                variant="outlined"
                density="comfortable"
                class="mb-3"
              ></v-text-field>
              <v-row>
                <v-col>
                  <v-text-field
                    v-model="editedOrder.billing_address.postal_code"
                    label="Postal Code"
                    variant="outlined"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="editedOrder.billing_address.city"
                    label="City"
                    variant="outlined"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-select
                v-model="editedOrder.billing_address.country"
                :items="countries"
                label="Country"
                variant="outlined"
                density="comfortable"
              ></v-select>
            </v-col>

            <!-- Shipping Address -->
            <v-col cols="12" md="6">
              <div class="d-flex justify-space-between align-center mb-3">
                <h4 class="text-subtitle-1">Shipping Address</h4>
                <v-checkbox
                  v-model="sameAsBilling"
                  label="Same as billing"
                  density="comfortable"
                  hide-details
                  @change="updateShippingAddress"
                ></v-checkbox>
              </div>
              <v-text-field
                v-model="editedOrder.shipping_address.name"
                label="Name"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :disabled="sameAsBilling"
              ></v-text-field>
              <v-text-field
                v-model="editedOrder.shipping_address.street"
                label="Street"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :disabled="sameAsBilling"
              ></v-text-field>
              <v-row>
                <v-col>
                  <v-text-field
                    v-model="editedOrder.shipping_address.postal_code"
                    label="Postal Code"
                    variant="outlined"
                    density="comfortable"
                    :disabled="sameAsBilling"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="editedOrder.shipping_address.city"
                    label="City"
                    variant="outlined"
                    density="comfortable"
                    :disabled="sameAsBilling"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-select
                v-model="editedOrder.shipping_address.country"
                :items="countries"
                label="Country"
                variant="outlined"
                density="comfortable"
                :disabled="sameAsBilling"
              ></v-select>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Order Items -->
      <v-card class="mb-6">
        <v-card-title class="d-flex justify-space-between align-center">
          <div>
            <v-icon start icon="mdi-cart"></v-icon>
            Order Items
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="addOrderItem"
          >
            Add Item
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th>Product</th>
                <th>SKU</th>
                <th>Quantity</th>
                <th>Unit Price</th>
                <th>Discount %</th>
                <th>Total</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in editedOrder.items" :key="index">
                <td>
                  <v-text-field
                    v-model="item.product_name"
                    variant="outlined"
                    density="compact"
                    hide-details
                  ></v-text-field>
                </td>
                <td>
                  <v-text-field
                    v-model="item.product_sku"
                    variant="outlined"
                    density="compact"
                    hide-details
                  ></v-text-field>
                </td>
                <td>
                  <v-text-field
                    v-model.number="item.quantity"
                    type="number"
                    variant="outlined"
                    density="compact"
                    hide-details
                    @input="updateItemTotal(item)"
                  ></v-text-field>
                </td>
                <td>
                  <v-text-field
                    v-model.number="item.unit_price"
                    type="number"
                    variant="outlined"
                    density="compact"
                    hide-details
                    @input="updateItemTotal(item)"
                  ></v-text-field>
                </td>
                <td>
                  <v-text-field
                    v-model.number="item.discount_percent"
                    type="number"
                    variant="outlined"
                    density="compact"
                    hide-details
                    @input="updateItemTotal(item)"
                  ></v-text-field>
                </td>
                <td>{{ formatCurrency(item.total_price) }}</td>
                <td>
                  <v-btn
                    icon="mdi-delete"
                    variant="text"
                    color="error"
                    size="small"
                    @click="removeOrderItem(index)"
                  ></v-btn>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="4"></td>
                <td class="text-right font-weight-medium">Subtotal:</td>
                <td>{{ formatCurrency(calculateSubtotal()) }}</td>
                <td></td>
              </tr>
              <tr>
                <td colspan="4"></td>
                <td class="text-right font-weight-medium">
                  Tax ({{ editedOrder.tax_rate }}%):
                </td>
                <td>{{ formatCurrency(calculateTax()) }}</td>
                <td></td>
              </tr>
              <tr>
                <td colspan="4"></td>
                <td class="text-right font-weight-medium">Shipping:</td>
                <td>
                  <v-text-field
                    v-model.number="editedOrder.shipping_amount"
                    type="number"
                    variant="outlined"
                    density="compact"
                    hide-details
                    @input="updateTotals"
                  ></v-text-field>
                </td>
                <td></td>
              </tr>
              <tr class="bg-grey-lighten-4">
                <td colspan="4"></td>
                <td class="text-right font-weight-bold">Total:</td>
                <td class="font-weight-bold">{{ formatCurrency(calculateTotal()) }}</td>
                <td></td>
              </tr>
            </tfoot>
          </v-table>
        </v-card-text>
      </v-card>

      <!-- Notes -->
      <v-card>
        <v-card-title>
          <v-icon start icon="mdi-note-text"></v-icon>
          Notes
        </v-card-title>
        <v-card-text>
          <v-textarea
            v-model="editedOrder.notes"
            variant="outlined"
            density="comfortable"
            rows="4"
          ></v-textarea>
        </v-card-text>
      </v-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { salesApi } from '@/services/api';

// Router and route
const router = useRouter();
const route = useRoute();

// State
const loading = ref(true);
const saving = ref(false);
const error = ref('');
const sameAsBilling = ref(false);
const editedOrder = ref<any>(null);

// Constants
const countries = [
  { title: 'Deutschland', value: 'Deutschland' },
  { title: 'Österreich', value: 'Österreich' },
  { title: 'Schweiz', value: 'Schweiz' }
];

// Get order ID from route params
const orderId = Number(route.params.id);

// Load order details
const loadOrderDetails = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await salesApi.getSalesOrder(orderId);
    editedOrder.value = { ...response.data };
    sameAsBilling.value = JSON.stringify(editedOrder.value.billing_address) === 
                         JSON.stringify(editedOrder.value.shipping_address);
  } catch (err) {
    console.error('Error loading order details:', err);
    error.value = 'Failed to load order details. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Update shipping address when "same as billing" changes
const updateShippingAddress = () => {
  if (sameAsBilling.value) {
    editedOrder.value.shipping_address = { ...editedOrder.value.billing_address };
  }
};

// Order items management
const addOrderItem = () => {
  editedOrder.value.items.push({
    product_name: '',
    product_sku: '',
    quantity: 1,
    unit_price: 0,
    discount_percent: 0,
    total_price: 0
  });
};

const removeOrderItem = (index: number) => {
  editedOrder.value.items.splice(index, 1);
  updateTotals();
};

const updateItemTotal = (item: any) => {
  const quantity = Number(item.quantity) || 0;
  const unitPrice = Number(item.unit_price) || 0;
  const discount = Number(item.discount_percent) || 0;
  
  item.total_price = quantity * unitPrice * (1 - discount / 100);
  updateTotals();
};

// Calculate totals
const calculateSubtotal = () => {
  return editedOrder.value.items.reduce((sum: number, item: any) => sum + item.total_price, 0);
};

const calculateTax = () => {
  const subtotal = calculateSubtotal();
  return subtotal * (editedOrder.value.tax_rate / 100);
};

const calculateTotal = () => {
  const subtotal = calculateSubtotal();
  const tax = calculateTax();
  const shipping = Number(editedOrder.value.shipping_amount) || 0;
  return subtotal + tax + shipping;
};

const updateTotals = () => {
  editedOrder.value.subtotal = calculateSubtotal();
  editedOrder.value.tax_amount = calculateTax();
  editedOrder.value.total_amount = calculateTotal();
};

// Save changes
const saveChanges = async () => {
  saving.value = true;
  error.value = '';

  try {
    await salesApi.updateSalesOrder(orderId, editedOrder.value);
    router.push({ name: 'SalesOrderDetail', params: { id: orderId } });
  } catch (err) {
    console.error('Error saving order:', err);
    error.value = 'Failed to save changes. Please try again.';
    saving.value = false;
  }
};

// Cancel edit
const cancelEdit = () => {
  router.push({ name: 'SalesOrderDetail', params: { id: orderId } });
};

// Format currency
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount);
};

// Initialize component
onMounted(() => {
  loadOrderDetails();
});
</script>

<style scoped>
.sales-order-edit {
  padding: 20px 0;
}

.v-table {
  background: white !important;
}
</style> 