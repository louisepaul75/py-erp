<template>
  <div class="customer-form">
    <div class="header">
      <h1>{{ isEditing ? 'Edit Customer' : 'New Customer' }}</h1>
      <div class="actions">
        <button @click="goBack" class="btn secondary">Cancel</button>
        <button @click="saveCustomer" class="btn primary" :disabled="isSaving">
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <form @submit.prevent="saveCustomer">
      <div class="card">
        <h2>General Information</h2>

        <div class="form-group">
          <label>Customer Type</label>
          <div class="flex items-center gap-6">
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="form.is_company"
                :value="false"
                @change="handleCustomerTypeChange"
                class="form-radio h-4 w-4 text-blue-600 border-gray-300"
              />
              <span class="ml-2">Individual (B2C)</span>
            </label>
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="form.is_company"
                :value="true"
                @change="handleCustomerTypeChange"
                class="form-radio h-4 w-4 text-blue-600 border-gray-300"
              />
              <span class="ml-2">Business (B2B)</span>
            </label>
          </div>
        </div>

        <div v-if="form.is_company" class="form-group">
          <label for="company_name">Company Name <span class="required">*</span></label>
          <input
            id="company_name"
            v-model="form.company_name"
            type="text"
            required
            class="form-input"
            :class="{ 'border-red-500': errors.company_name }"
          />
          <div v-if="errors.company_name" class="error-message">{{ errors.company_name }}</div>
        </div>

        <div v-if="form.is_company" class="form-group">
          <label for="vat_id">VAT ID</label>
          <input id="vat_id" v-model="form.vat_id" type="text" class="form-input" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="first_name"
              >First Name <span v-if="!form.is_company" class="required">*</span></label
            >
            <input
              id="first_name"
              v-model="form.first_name"
              type="text"
              :required="!form.is_company"
              class="form-input"
              :class="{ 'border-red-500': errors.first_name }"
            />
            <div v-if="errors.first_name" class="error-message">{{ errors.first_name }}</div>
          </div>

          <div class="form-group">
            <label for="last_name"
              >Last Name <span v-if="!form.is_company" class="required">*</span></label
            >
            <input
              id="last_name"
              v-model="form.last_name"
              type="text"
              :required="!form.is_company"
              class="form-input"
              :class="{ 'border-red-500': errors.last_name }"
            />
            <div v-if="errors.last_name" class="error-message">{{ errors.last_name }}</div>
          </div>
        </div>

        <div class="form-group">
          <label for="website">Website</label>
          <input id="website" v-model="form.website" type="url" class="form-input" />
        </div>

        <div class="form-group">
          <label for="verified_status">Verified Status</label>
          <select id="verified_status" v-model="form.verified_status" class="form-select">
            <option value="Yes">Yes</option>
            <option value="No">No</option>
            <option value="Not Determined">Not Determined</option>
          </select>
        </div>
      </div>

      <div class="card">
        <h2>Billing Address</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="billing_street">Street <span class="required">*</span></label>
            <input
              id="billing_street"
              v-model="form.billing_street"
              type="text"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.billing_street }"
            />
            <div v-if="errors.billing_street" class="error-message">
              {{ errors.billing_street }}
            </div>
          </div>

          <div class="form-group narrow">
            <label for="billing_street_number">Number <span class="required">*</span></label>
            <input
              id="billing_street_number"
              v-model="form.billing_street_number"
              type="text"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.billing_street_number }"
            />
            <div v-if="errors.billing_street_number" class="error-message">
              {{ errors.billing_street_number }}
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group narrow">
            <label for="billing_postal_code">Postal Code <span class="required">*</span></label>
            <input
              id="billing_postal_code"
              v-model="form.billing_postal_code"
              type="text"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.billing_postal_code }"
            />
            <div v-if="errors.billing_postal_code" class="error-message">
              {{ errors.billing_postal_code }}
            </div>
          </div>

          <div class="form-group">
            <label for="billing_city">City <span class="required">*</span></label>
            <input
              id="billing_city"
              v-model="form.billing_city"
              type="text"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.billing_city }"
            />
            <div v-if="errors.billing_city" class="error-message">{{ errors.billing_city }}</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="billing_country">Country <span class="required">*</span></label>
            <select
              id="billing_country"
              v-model="form.billing_country"
              required
              class="form-select"
              :class="{ 'border-red-500': errors.billing_country }"
            >
              <option value="">Select Country</option>
              <option value="DE">Germany</option>
              <option value="AT">Austria</option>
              <option value="CH">Switzerland</option>
            </select>
            <div v-if="errors.billing_country" class="error-message">
              {{ errors.billing_country }}
            </div>
          </div>

          <div class="form-group">
            <label for="billing_state">State/Region</label>
            <input id="billing_state" v-model="form.billing_state" type="text" class="form-input" />
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Contact Information</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="phone_main">Phone <span class="required">*</span></label>
            <input
              id="phone_main"
              v-model="form.phone_main"
              type="tel"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.phone_main }"
            />
            <div v-if="errors.phone_main" class="error-message">{{ errors.phone_main }}</div>
          </div>

          <div class="form-group">
            <label for="email_main">Email <span class="required">*</span></label>
            <input
              id="email_main"
              v-model="form.email_main"
              type="email"
              required
              class="form-input"
              :class="{ 'border-red-500': errors.email_main }"
            />
            <div v-if="errors.email_main" class="error-message">{{ errors.email_main }}</div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Financial Information</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="payment_terms_overall">Payment Terms</label>
            <input
              id="payment_terms_overall"
              v-model="form.payment_terms_overall"
              type="text"
              class="form-input"
              placeholder="e.g., Payment in 30 days"
            />
          </div>

          <div class="form-group">
            <label for="skonto_period">Skonto Period</label>
            <input
              id="skonto_period"
              v-model="form.skonto_period"
              type="text"
              class="form-input"
              placeholder="e.g., Payment within 10 days"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="skonto_rate_or_amount">Skonto Rate/Amount</label>
            <input
              id="skonto_rate_or_amount"
              v-model="form.skonto_rate_or_amount"
              type="text"
              class="form-input"
              placeholder="e.g., 2%"
            />
          </div>

          <div class="form-group">
            <label for="credit_limit">Credit Limit</label>
            <input
              id="credit_limit"
              v-model="form.credit_limit"
              type="number"
              min="0"
              step="0.01"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="discount">Discount (%)</label>
            <input
              id="discount"
              v-model="form.discount"
              type="number"
              min="0"
              max="100"
              step="0.01"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="default_shipping_method">Default Shipping Method</label>
            <select
              id="default_shipping_method"
              v-model="form.default_shipping_method"
              class="form-select"
            >
              <option value="">Select Shipping Method</option>
              <option value="Standard">Standard</option>
              <option value="Express">Express</option>
              <option value="Overnight">Overnight</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Allowed Payment Methods</label>
          <div class="flex flex-wrap gap-4">
            <label
              class="inline-flex items-center"
              v-for="method in paymentMethods"
              :key="method.value"
            >
              <input
                type="checkbox"
                :value="method.value"
                v-model="form.allowed_payment_methods"
                class="form-checkbox h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <span class="ml-2">{{ method.label }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Bank Details</h2>

        <div class="form-group">
          <label for="bank_account_holder">Account Holder</label>
          <input
            id="bank_account_holder"
            v-model="form.bank_account_holder"
            type="text"
            class="form-input"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="bank_iban">IBAN</label>
            <input id="bank_iban" v-model="form.bank_iban" type="text" class="form-input" />
          </div>

          <div class="form-group">
            <label for="bank_bic">BIC</label>
            <input id="bank_bic" v-model="form.bank_bic" type="text" class="form-input" />
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Marketing Preferences</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="postal_advertising">Postal Advertising</label>
            <select id="postal_advertising" v-model="form.postal_advertising" class="form-select">
              <option value="Yes">Yes</option>
              <option value="No">No</option>
              <option value="Not Determined">Not Determined</option>
            </select>
          </div>

          <div class="form-group">
            <label for="email_advertising">Email Advertising</label>
            <select id="email_advertising" v-model="form.email_advertising" class="form-select">
              <option value="Yes">Yes</option>
              <option value="No">No</option>
              <option value="Not Determined">Not Determined</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="sales_representative">Sales Representative</label>
          <input
            id="sales_representative"
            v-model="form.sales_representative"
            type="text"
            class="form-input"
          />
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const customerId = computed(() => route.params.id);
const isEditing = computed(() => !!customerId.value);

const isSaving = ref(false);
const errors = ref({});

const paymentMethods = [
  { value: 'INVOICE', label: 'Invoice' },
  { value: 'CREDIT_CARD', label: 'Credit Card' },
  { value: 'PAYPAL', label: 'PayPal' },
  { value: 'SEPA', label: 'SEPA Direct Debit' },
  { value: 'CASH', label: 'Cash on Delivery' }
];

const form = ref({
  is_company: false,
  first_name: '',
  last_name: '',
  company_name: '',
  vat_id: '',
  billing_street: '',
  billing_street_number: '',
  billing_postal_code: '',
  billing_city: '',
  billing_country: '',
  billing_state: '',
  phone_main: '',
  email_main: '',
  bank_iban: '',
  bank_bic: '',
  bank_account_holder: '',
  allowed_payment_methods: [],
  postal_advertising: 'Not Determined',
  email_advertising: 'Not Determined',
  sales_representative: '',
  discount: null,
  default_shipping_method: '',
  payment_terms_overall: '',
  skonto_period: '',
  skonto_rate_or_amount: '',
  credit_limit: null,
  website: '',
  verified_status: 'Not Determined',
  is_active: true
});

function handleCustomerTypeChange() {
  if (form.value.is_company) {
    if (!isEditing.value) {
      form.value.first_name = '';
      form.value.last_name = '';
    }
  } else {
    if (!isEditing.value) {
      form.value.company_name = '';
      form.value.vat_id = '';
    }
  }
}

function validateForm() {
  errors.value = {};
  let isValid = true;

  if (form.value.is_company && !form.value.company_name) {
    errors.value.company_name = 'Company name is required';
    isValid = false;
  }

  if (!form.value.is_company) {
    if (!form.value.first_name) {
      errors.value.first_name = 'First name is required';
      isValid = false;
    }
    if (!form.value.last_name) {
      errors.value.last_name = 'Last name is required';
      isValid = false;
    }
  }

  if (!form.value.billing_street) {
    errors.value.billing_street = 'Street is required';
    isValid = false;
  }

  if (!form.value.billing_street_number) {
    errors.value.billing_street_number = 'Street number is required';
    isValid = false;
  }

  if (!form.value.billing_postal_code) {
    errors.value.billing_postal_code = 'Postal code is required';
    isValid = false;
  }

  if (!form.value.billing_city) {
    errors.value.billing_city = 'City is required';
    isValid = false;
  }

  if (!form.value.billing_country) {
    errors.value.billing_country = 'Country is required';
    isValid = false;
  }

  if (!form.value.phone_main) {
    errors.value.phone_main = 'Phone number is required';
    isValid = false;
  }

  if (!form.value.email_main) {
    errors.value.email_main = 'Email is required';
    isValid = false;
  } else if (!isValidEmail(form.value.email_main)) {
    errors.value.email_main = 'Please enter a valid email address';
    isValid = false;
  }

  return isValid;
}

function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

async function saveCustomer() {
  if (!validateForm()) {
    const firstErrorEl = document.querySelector('.error');
    if (firstErrorEl) {
      firstErrorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    return;
  }

  isSaving.value = true;

  try {
    // Mock API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    router.push('/customers');
  } catch (error) {
    console.error('Error saving customer:', error);
  } finally {
    isSaving.value = false;
  }
}

function goBack() {
  router.back();
}
</script>

<style scoped>
.customer-form {
  @apply max-w-5xl mx-auto py-6;
}

.header {
  @apply flex justify-between items-center mb-6;
}

.header h1 {
  @apply text-2xl font-semibold text-gray-900;
}

.actions {
  @apply flex gap-3;
}

.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6;
}

.card h2 {
  @apply text-lg font-medium text-gray-900 mb-4;
}

.form-group {
  @apply mb-4;
}

.form-group label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.form-row {
  @apply flex flex-col sm:flex-row gap-4 mb-4;
}

.form-group.narrow {
  @apply sm:w-1/3;
}

.error-message {
  @apply text-red-600 text-sm mt-1;
}

.required {
  @apply text-red-600 ml-0.5;
}

/* Override any dark mode styles */
:deep(.form-input),
:deep(.form-select) {
  @apply bg-white text-gray-900;
}

:deep(.form-radio),
:deep(.form-checkbox) {
  @apply text-blue-600 border-gray-300;
}
</style>
