<template>
  <div class="customer-detail">
    <div class="header">
      <h1>
        {{
          customer.is_company
            ? customer.company_name
            : `${customer.first_name} ${customer.last_name}`
        }}
        <span v-if="!customer.is_active" class="inactive-badge">Inactive</span>
      </h1>
      <div class="actions">
        <button @click="editCustomer" class="btn primary">Edit</button>
        <button
          @click="toggleActive"
          class="btn"
          :class="customer.is_active ? 'warning' : 'success'"
        >
          {{ customer.is_active ? 'Deactivate' : 'Activate' }}
        </button>
      </div>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="{ active: activeTab === tab.id }"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- General Information Tab -->
    <div v-if="activeTab === 'general'" class="tab-content">
      <div class="card">
        <h2>General Information</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Customer Type</label>
            <span>{{ customer.is_company ? 'Business (B2B)' : 'Individual (B2C)' }}</span>
          </div>
          <div v-if="customer.is_company" class="info-item">
            <label>Company Name</label>
            <span>{{ customer.company_name }}</span>
          </div>
          <div v-if="customer.is_company" class="info-item">
            <label>VAT ID</label>
            <span>{{ customer.vat_id || 'Not provided' }}</span>
          </div>
          <div v-if="!customer.is_company || customer.first_name" class="info-item">
            <label>First Name</label>
            <span>{{ customer.first_name }}</span>
          </div>
          <div v-if="!customer.is_company || customer.last_name" class="info-item">
            <label>Last Name</label>
            <span>{{ customer.last_name }}</span>
          </div>
          <div class="info-item">
            <label>Website</label>
            <span>
              <a v-if="customer.website" :href="customer.website" target="_blank">{{
                customer.website
              }}</a>
              <span v-else>Not provided</span>
            </span>
          </div>
          <div class="info-item">
            <label>Created</label>
            <span>{{ formatDate(customer.created_at) }}</span>
          </div>
          <div class="info-item">
            <label>Last Updated</label>
            <span>{{ formatDate(customer.updated_at) }}</span>
          </div>
          <div class="info-item">
            <label>Verified Status</label>
            <span>{{ customer.verified_status || 'Not Determined' }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Billing Address</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Street</label>
            <span>{{ customer.billing_street }} {{ customer.billing_street_number }}</span>
          </div>
          <div class="info-item">
            <label>City</label>
            <span>{{ customer.billing_city }}</span>
          </div>
          <div class="info-item">
            <label>Postal Code</label>
            <span>{{ customer.billing_postal_code }}</span>
          </div>
          <div class="info-item">
            <label>Country</label>
            <span>{{ customer.billing_country }}</span>
          </div>
          <div class="info-item" v-if="customer.billing_state">
            <label>State/Region</label>
            <span>{{ customer.billing_state }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2>Primary Contact</h2>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <label>Phone</label>
            <span>{{ customer.phone_main }}</span>
          </div>
          <div class="info-item">
            <label>Email</label>
            <span>{{ customer.email_main }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Documents Tab -->
    <div v-if="activeTab === 'documents'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>Documents</h2>
          <div class="document-actions">
            <div class="dropdown">
              <button class="btn small dropdown-toggle">New</button>
              <div class="dropdown-menu">
                <button @click="createNewDocument('order')" class="dropdown-item">Order</button>
                <button @click="createNewDocument('invoice')" class="dropdown-item">Invoice</button>
                <button @click="createNewDocument('delivery')" class="dropdown-item">
                  Delivery Note
                </button>
                <button @click="createNewDocument('quote')" class="dropdown-item">Quote</button>
                <button @click="createNewDocument('credit')" class="dropdown-item">
                  Credit Note
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="document-stats">
          <div class="stat-card">
            <div class="stat-value">{{ documentCounts.orders || 0 }}</div>
            <div class="stat-label">Orders</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ documentCounts.invoices || 0 }}</div>
            <div class="stat-label">Invoices</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ documentCounts.deliveries || 0 }}</div>
            <div class="stat-label">Delivery Notes</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ documentCounts.quotes || 0 }}</div>
            <div class="stat-label">Quotes</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ formatCurrency(documentTotals.revenue) }}</div>
            <div class="stat-label">Total Revenue</div>
          </div>
        </div>

        <div class="document-filter">
          <div class="search-box">
            <input
              type="text"
              v-model="documentSearch"
              placeholder="Search documents..."
              @input="filterDocuments"
            />
          </div>
          <div class="filter-options">
            <select v-model="documentTypeFilter" @change="filterDocuments">
              <option value="all">All Documents</option>
              <option value="order">Orders</option>
              <option value="invoice">Invoices</option>
              <option value="delivery">Delivery Notes</option>
              <option value="quote">Quotes</option>
              <option value="credit">Credit Notes</option>
            </select>
            <select v-model="documentStatusFilter" @change="filterDocuments">
              <option value="all">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select v-model="documentSortOrder" @change="filterDocuments">
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="highest">Highest Amount</option>
              <option value="lowest">Lowest Amount</option>
            </select>
          </div>
        </div>

        <div v-if="filteredDocuments.length === 0" class="empty-state">
          <p>No documents found</p>
        </div>

        <div v-else class="document-table">
          <table>
            <thead>
              <tr class="draggable-header">
                <th
                  v-for="column in visibleColumns"
                  :key="column.id"
                  @click="sortTable(column.id)"
                  :class="{
                    sortable: column.sortable,
                    'sorted-asc': sortColumn === column.id && sortDirection === 'asc',
                    'sorted-desc': sortColumn === column.id && sortDirection === 'desc'
                  }"
                  draggable="true"
                  @dragstart="dragStart($event, column.id)"
                  @dragover.prevent
                  @dragenter.prevent
                  @drop="drop($event, column.id)"
                >
                  {{ column.label }}
                  <span v-if="column.sortable" class="sort-icon">
                    {{ sortColumn === column.id ? (sortDirection === 'asc' ? '↑' : '↓') : '↕' }}
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in sortedDocuments" :key="doc.id" :class="getDocumentRowClass(doc)">
                <td v-if="isColumnVisible('number')">
                  <a :href="`/documents/${doc.id}`" class="document-link">{{ doc.number }}</a>
                </td>
                <td v-if="isColumnVisible('type')">
                  <span class="document-type" :class="doc.type">
                    {{ getDocumentTypeName(doc.type) }}
                  </span>
                </td>
                <td v-if="isColumnVisible('date')">{{ formatDate(doc.date) }}</td>
                <td v-if="isColumnVisible('dueDate')">
                  {{ doc.due_date ? formatDate(doc.due_date) : '-' }}
                </td>
                <td v-if="isColumnVisible('amount')">{{ formatCurrency(doc.amount) }}</td>
                <td v-if="isColumnVisible('status')">
                  <span class="status-badge" :class="doc.status">
                    {{ getStatusName(doc.status) }}
                  </span>
                </td>
                <td v-if="isColumnVisible('actions')">
                  <div class="document-actions">
                    <button @click="viewDocument(doc.id)" class="btn icon" title="View">
                      <span class="icon">👁️</span>
                    </button>
                    <button @click="printDocument(doc.id)" class="btn icon" title="Print">
                      <span class="icon">🖨️</span>
                    </button>
                    <button @click="downloadDocument(doc.id)" class="btn icon" title="Download">
                      <span class="icon">📥</span>
                    </button>
                    <button
                      v-if="canEditDocument(doc)"
                      @click="editDocument(doc.id)"
                      class="btn icon"
                      title="Edit"
                    >
                      <span class="icon">✏️</span>
                    </button>
                    <button
                      v-if="canSendDocument(doc)"
                      @click="sendDocument(doc.id)"
                      class="btn icon success"
                      title="Send"
                    >
                      <span class="icon">📤</span>
                    </button>
                    <button
                      v-if="canCancelDocument(doc)"
                      @click="cancelDocument(doc.id)"
                      class="btn icon danger"
                      title="Cancel"
                    >
                      <span class="icon">❌</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination" v-if="totalDocumentPages > 1">
          <button
            @click="changePage(currentDocumentPage - 1)"
            :disabled="currentDocumentPage === 1"
            class="btn small"
          >
            Previous
          </button>
          <span>Page {{ currentDocumentPage }} of {{ totalDocumentPages }}</span>
          <button
            @click="changePage(currentDocumentPage + 1)"
            :disabled="currentDocumentPage === totalDocumentPages"
            class="btn small"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Financial Tab -->
    <div v-if="activeTab === 'financial'" class="tab-content">
      <div class="card">
        <h2>Payment Information</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Payment Terms</label>
            <span>{{ customer.payment_terms_overall || 'Not set' }}</span>
          </div>
          <div class="info-item">
            <label>Skonto Period</label>
            <span>{{ customer.skonto_period || 'Not set' }}</span>
          </div>
          <div class="info-item">
            <label>Skonto Rate/Amount</label>
            <span>{{ customer.skonto_rate_or_amount || 'Not set' }}</span>
          </div>
          <div class="info-item">
            <label>Credit Limit</label>
            <span>{{ formatCurrency(customer.credit_limit) }}</span>
          </div>
          <div class="info-item">
            <label>Discount</label>
            <span>{{ customer.discount ? `${customer.discount}%` : 'None' }}</span>
          </div>
          <div class="info-item">
            <label>Default Shipping Method</label>
            <span>{{ customer.default_shipping_method || 'Not set' }}</span>
          </div>
          <div class="info-item">
            <label>Allowed Payment Methods</label>
            <span>{{ formatPaymentMethods(customer.allowed_payment_methods) }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Bank Details</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Account Holder</label>
            <span>{{ customer.bank_account_holder || 'Not provided' }}</span>
          </div>
          <div class="info-item">
            <label>IBAN</label>
            <span>{{ customer.bank_iban || 'Not provided' }}</span>
          </div>
          <div class="info-item">
            <label>BIC</label>
            <span>{{ customer.bank_bic || 'Not provided' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Shipping Addresses Tab -->
    <div v-if="activeTab === 'shipping'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>Shipping Addresses</h2>
          <button @click="addShippingAddress" class="btn small">Add Address</button>
        </div>

        <div v-if="shippingAddresses.length === 0" class="empty-state">
          No shipping addresses found
        </div>

        <div v-else class="shipping-addresses">
          <div v-for="address in shippingAddresses" :key="address.id" class="shipping-address-card">
            <div class="address-header">
              <h3>{{ address.address_label || 'Address' }}</h3>
              <span v-if="address.is_default" class="default-badge">Default</span>
            </div>
            <div class="address-content">
              <p>{{ address.street }} {{ address.street_number }}</p>
              <p>{{ address.postal_code }} {{ address.city }}</p>
              <p>{{ address.country }}{{ address.state ? `, ${address.state}` : '' }}</p>
            </div>
            <div class="address-actions">
              <button @click="editShippingAddress(address.id)" class="btn small">Edit</button>
              <button
                v-if="!address.is_default"
                @click="setDefaultAddress(address.id)"
                class="btn small"
              >
                Set as Default
              </button>
              <button @click="deleteShippingAddress(address.id)" class="btn small danger">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Information Tab -->
    <div v-if="activeTab === 'contacts'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h2>Additional Contact Information</h2>
          <button @click="addContactInfo" class="btn small">Add Contact</button>
        </div>

        <div v-if="contactInfos.length === 0" class="empty-state">
          No additional contact information found
        </div>

        <div v-else class="contact-infos">
          <div v-for="contact in contactInfos" :key="contact.id" class="contact-info-card">
            <div class="contact-info-header">
              <h3>{{ formatContactType(contact.contact_type) }}</h3>
              <span v-if="contact.is_primary" class="primary-badge">Primary</span>
            </div>
            <div class="contact-info-content">
              <p>{{ contact.value }}</p>
              <p v-if="contact.description" class="description">{{ contact.description }}</p>
            </div>
            <div class="contact-info-actions">
              <button @click="editContactInfo(contact.id)" class="btn small">Edit</button>
              <button
                v-if="!contact.is_primary"
                @click="setPrimaryContact(contact.id)"
                class="btn small"
              >
                Set as Primary
              </button>
              <button @click="deleteContactInfo(contact.id)" class="btn small danger">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Persons (B2B only) -->
      <div v-if="customer.is_company" class="card">
        <div class="card-header">
          <h2>Contact Persons</h2>
          <button @click="addContactPerson" class="btn small">Add Person</button>
        </div>

        <div v-if="contactPersons.length === 0" class="empty-state">No contact persons found</div>

        <div v-else class="contact-persons">
          <div v-for="person in contactPersons" :key="person.id" class="contact-person-card">
            <div class="contact-person-header">
              <h3>{{ person.first_name }} {{ person.last_name }}</h3>
            </div>
            <div class="contact-person-content">
              <p v-if="person.position"><strong>Position:</strong> {{ person.position }}</p>
              <p v-if="person.phone"><strong>Phone:</strong> {{ person.phone }}</p>
              <p v-if="person.email"><strong>Email:</strong> {{ person.email }}</p>
            </div>
            <div class="contact-person-actions">
              <button @click="editContactPerson(person.id)" class="btn small">Edit</button>
              <button @click="deleteContactPerson(person.id)" class="btn small danger">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Marketing Tab -->
    <div v-if="activeTab === 'marketing'" class="tab-content">
      <div class="card">
        <h2>Marketing Preferences</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Postal Advertising</label>
            <span>{{ customer.postal_advertising || 'Not Determined' }}</span>
          </div>
          <div class="info-item">
            <label>Email Advertising</label>
            <span>{{ customer.email_advertising || 'Not Determined' }}</span>
          </div>
          <div class="info-item">
            <label>Sales Representative</label>
            <span>{{ customer.sales_representative || 'Not Assigned' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const customerId = computed(() => route.params.id);

// Mock data instead of API calls
const customer = ref({
  id: 1,
  is_company: true,
  company_name: 'Demo Company GmbH',
  vat_id: 'DE123456789',
  first_name: 'John',
  last_name: 'Doe',
  billing_street: 'Hauptstraße',
  billing_street_number: '1',
  billing_postal_code: '10115',
  billing_city: 'Berlin',
  billing_country: 'Germany',
  billing_state: '',
  phone_main: '+49 30 123456',
  email_main: 'contact@demo-company.com',
  bank_iban: 'DE89370400440532013000',
  bank_bic: 'COBADEFFXXX',
  bank_account_holder: 'Demo Company GmbH',
  allowed_payment_methods: ['INVOICE', 'SEPA', 'CREDIT_CARD'],
  postal_advertising: 'Not Determined',
  email_advertising: 'Yes',
  sales_representative: 'Max Mustermann',
  discount: 5,
  default_shipping_method: 'Standard',
  payment_terms_overall: 'Payment in 30 days',
  skonto_period: 'Payment within 10 days',
  skonto_rate_or_amount: '2%',
  credit_limit: 10000,
  website: 'https://demo-company.com',
  verified_status: 'Not Determined',
  is_active: true,
  created_at: '2024-02-20',
  updated_at: '2024-02-20'
});

const shippingAddresses = ref([
  {
    id: 1,
    customer_id: 1,
    street: 'Hauptstraße',
    street_number: '1',
    postal_code: '10115',
    city: 'Berlin',
    country: 'Germany',
    state: '',
    is_default: true,
    address_label: 'Headquarters'
  },
  {
    id: 2,
    customer_id: 1,
    street: 'Industriestraße',
    street_number: '42',
    postal_code: '70565',
    city: 'Stuttgart',
    country: 'Germany',
    state: '',
    is_default: false,
    address_label: 'Warehouse'
  }
]);

const contactInfos = ref([
  {
    id: 1,
    customer_id: 1,
    contact_type: 'PHONE',
    value: '+49 30 123456',
    is_primary: true,
    description: 'Main Office'
  },
  {
    id: 2,
    customer_id: 1,
    contact_type: 'EMAIL',
    value: 'contact@demo-company.com',
    is_primary: true,
    description: 'General Inquiries'
  },
  {
    id: 3,
    customer_id: 1,
    contact_type: 'PHONE',
    value: '+49 30 654321',
    is_primary: false,
    description: 'Support Hotline'
  }
]);

const contactPersons = ref([
  {
    id: 1,
    customer_id: 1,
    first_name: 'John',
    last_name: 'Doe',
    position: 'CEO',
    phone: '+49 30 123456-100',
    email: 'john.doe@demo-company.com'
  },
  {
    id: 2,
    customer_id: 1,
    first_name: 'Jane',
    last_name: 'Smith',
    position: 'Purchasing Manager',
    phone: '+49 30 123456-200',
    email: 'jane.smith@demo-company.com'
  }
]);

const activeTab = ref('general');
const documents = ref([
  {
    id: 101,
    number: 'ORD-2024-001',
    type: 'order',
    date: '2024-02-15',
    due_date: null,
    amount: 1250.0,
    status: 'processing',
    customer_reference: 'PO-12345'
  },
  {
    id: 102,
    number: 'INV-2024-001',
    type: 'invoice',
    date: '2024-02-20',
    due_date: '2024-03-20',
    amount: 1250.0,
    status: 'sent',
    customer_reference: 'PO-12345'
  },
  {
    id: 103,
    number: 'DEL-2024-001',
    type: 'delivery',
    date: '2024-02-18',
    due_date: null,
    amount: 0,
    status: 'completed',
    customer_reference: 'PO-12345'
  },
  {
    id: 104,
    number: 'ORD-2024-002',
    type: 'order',
    date: '2024-01-10',
    due_date: null,
    amount: 750.5,
    status: 'completed',
    customer_reference: 'PO-12346'
  },
  {
    id: 105,
    number: 'INV-2024-002',
    type: 'invoice',
    date: '2024-01-15',
    due_date: '2024-02-15',
    amount: 750.5,
    status: 'paid',
    customer_reference: 'PO-12346'
  },
  {
    id: 106,
    number: 'QUO-2024-001',
    type: 'quote',
    date: '2024-03-01',
    due_date: '2024-03-31',
    amount: 3200.0,
    status: 'sent',
    customer_reference: 'RFQ-789'
  }
]);

const documentCounts = ref({
  orders: 2,
  invoices: 2,
  deliveries: 1,
  quotes: 1,
  credits: 0
});

const documentTotals = ref({
  revenue: 2000.5,
  outstanding: 1250.0
});

// Document filtering and pagination
const documentSearch = ref('');
const documentTypeFilter = ref('all');
const documentStatusFilter = ref('all');
const documentSortOrder = ref('newest');
const currentDocumentPage = ref(1);
const documentsPerPage = 10;
const totalDocumentPages = computed(() => {
  return Math.ceil(filteredDocuments.value.length / documentsPerPage);
});

// Table columns configuration
const columns = ref([
  { id: 'number', label: 'Number', sortable: true, visible: true },
  { id: 'type', label: 'Type', sortable: true, visible: true },
  { id: 'date', label: 'Date', sortable: true, visible: true },
  { id: 'dueDate', label: 'Due Date', sortable: true, visible: true },
  { id: 'amount', label: 'Amount', sortable: true, visible: true },
  { id: 'status', label: 'Status', sortable: true, visible: true },
  { id: 'actions', label: 'Actions', sortable: false, visible: true }
]);

const visibleColumns = computed(() => {
  return columns.value.filter((col) => col.visible);
});

// Sorting
const sortColumn = ref('date');
const sortDirection = ref('desc');

const tabs = [
  { id: 'general', name: 'General' },
  { id: 'documents', name: 'Documents' },
  { id: 'financial', name: 'Financial' },
  { id: 'shipping', name: 'Shipping Addresses' },
  { id: 'contacts', name: 'Contacts' },
  { id: 'marketing', name: 'Marketing' }
];

const filteredDocuments = computed(() => {
  let result = [...documents.value];

  // Apply search filter
  if (documentSearch.value) {
    const searchTerm = documentSearch.value.toLowerCase();
    result = result.filter(
      (doc) =>
        doc.number.toLowerCase().includes(searchTerm) ||
        (doc.customer_reference && doc.customer_reference.toLowerCase().includes(searchTerm))
    );
  }

  // Apply type filter
  if (documentTypeFilter.value !== 'all') {
    result = result.filter((doc) => doc.type === documentTypeFilter.value);
  }

  // Apply status filter
  if (documentStatusFilter.value !== 'all') {
    result = result.filter((doc) => doc.status === documentStatusFilter.value);
  }

  return result;
});

const sortedDocuments = computed(() => {
  let result = [...filteredDocuments.value];

  if (sortColumn.value) {
    result.sort((a, b) => {
      let aValue, bValue;

      // Handle special cases for different column types
      switch (sortColumn.value) {
        case 'number':
          aValue = a.number;
          bValue = b.number;
          break;
        case 'type':
          aValue = a.type;
          bValue = b.type;
          break;
        case 'date':
          aValue = new Date(a.date);
          bValue = new Date(b.date);
          break;
        case 'dueDate':
          aValue = a.due_date ? new Date(a.due_date) : new Date(0);
          bValue = b.due_date ? new Date(b.due_date) : new Date(0);
          break;
        case 'amount':
          aValue = a.amount;
          bValue = b.amount;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          aValue = a[sortColumn.value];
          bValue = b[sortColumn.value];
      }

      // Compare the values based on sort direction
      if (sortDirection.value === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0;
      }
    });
  }

  // Apply pagination
  const startIndex = (currentDocumentPage.value - 1) * documentsPerPage;
  return result.slice(startIndex, startIndex + documentsPerPage);
});

function isColumnVisible(columnId) {
  const column = columns.value.find((col) => col.id === columnId);
  return column && column.visible;
}

function sortTable(columnId) {
  // If clicking the same column, toggle sort direction
  if (sortColumn.value === columnId) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    // If clicking a different column, set it as the sort column with default 'asc' direction
    sortColumn.value = columnId;
    sortDirection.value = 'asc';
  }
}

// Drag and drop functionality for columns
let draggedColumnId = null;

function dragStart(event, columnId) {
  draggedColumnId = columnId;
  event.dataTransfer.effectAllowed = 'move';
}

function drop(event, targetColumnId) {
  if (draggedColumnId === targetColumnId) return;

  // Find the indices of the dragged and target columns
  const draggedIndex = columns.value.findIndex((col) => col.id === draggedColumnId);
  const targetIndex = columns.value.findIndex((col) => col.id === targetColumnId);

  // Reorder the columns
  const draggedColumn = columns.value.splice(draggedIndex, 1)[0];
  columns.value.splice(targetIndex, 0, draggedColumn);

  draggedColumnId = null;
}

function editCustomer() {
  router.push(`/customers/${customerId.value}/edit`);
}

function toggleActive() {
  customer.value.is_active = !customer.value.is_active;
}

// Document functions
function filterDocuments() {
  currentDocumentPage.value = 1; // Reset to first page when filtering
}

function changePage(page) {
  currentDocumentPage.value = page;
}

function getDocumentTypeName(type) {
  const types = {
    order: 'Order',
    invoice: 'Invoice',
    delivery: 'Delivery Note',
    quote: 'Quote',
    credit: 'Credit Note'
  };
  return types[type] || type;
}

function getStatusName(status) {
  const statuses = {
    draft: 'Draft',
    sent: 'Sent',
    paid: 'Paid',
    overdue: 'Overdue',
    cancelled: 'Cancelled',
    completed: 'Completed',
    processing: 'Processing'
  };
  return statuses[status] || status;
}

function getDocumentRowClass(doc) {
  if (doc.status === 'overdue') return 'overdue';
  if (doc.status === 'cancelled') return 'cancelled';
  return '';
}

function canEditDocument(doc) {
  // Only allow editing of documents in draft status
  return doc.status === 'draft';
}

function canSendDocument(doc) {
  // Allow sending documents that are in draft status
  return doc.status === 'draft';
}

function canCancelDocument(doc) {
  // Allow cancelling documents that are not already cancelled or completed
  return !['cancelled', 'completed', 'paid'].includes(doc.status);
}

function sendDocument(id) {
  if (!confirm('Are you sure you want to send this document?')) return;

  // Find the document and update its status
  const doc = documents.value.find((d) => d.id === id);
  if (doc) {
    doc.status = 'sent';
  }
}

function cancelDocument(id) {
  if (!confirm('Are you sure you want to cancel this document?')) return;

  // Find the document and update its status
  const doc = documents.value.find((d) => d.id === id);
  if (doc) {
    doc.status = 'cancelled';
  }
}

function createNewDocument(type) {
  router.push({
    path: '/documents/new',
    query: {
      customer_id: customerId.value,
      type: type
    }
  });
}

function viewDocument(id) {
  router.push(`/documents/${id}`);
}

function editDocument(id) {
  router.push(`/documents/${id}/edit`);
}

function printDocument(id) {
  window.open(`/documents/${id}/print`, '_blank');
}

function downloadDocument(id) {
  window.open(`/api/documents/${id}/download`, '_blank');
}

// Shipping address functions
function addShippingAddress() {
  router.push(`/customers/${customerId.value}/shipping-addresses/new`);
}

function editShippingAddress(addressId) {
  router.push(`/customers/${customerId.value}/shipping-addresses/${addressId}/edit`);
}

function setDefaultAddress(addressId) {
  // Update local data to set the selected address as default
  shippingAddresses.value.forEach((addr) => {
    addr.is_default = addr.id === addressId;
  });
}

function deleteShippingAddress(addressId) {
  if (!confirm('Are you sure you want to delete this shipping address?')) return;
  shippingAddresses.value = shippingAddresses.value.filter((addr) => addr.id !== addressId);
}

// Contact info functions
function addContactInfo() {
  router.push(`/customers/${customerId.value}/contact-info/new`);
}

function editContactInfo(contactId) {
  router.push(`/customers/${customerId.value}/contact-info/${contactId}/edit`);
}

function setPrimaryContact(contactId) {
  const contact = contactInfos.value.find((c) => c.id === contactId);
  if (contact) {
    // Set all contacts of the same type to non-primary
    contactInfos.value.forEach((c) => {
      if (c.contact_type === contact.contact_type) {
        c.is_primary = c.id === contactId;
      }
    });

    // Update customer's main contact info if this is a primary contact
    if (contact.is_primary) {
      if (contact.contact_type === 'PHONE') {
        customer.value.phone_main = contact.value;
      } else if (contact.contact_type === 'EMAIL') {
        customer.value.email_main = contact.value;
      }
    }
  }
}

function deleteContactInfo(contactId) {
  if (!confirm('Are you sure you want to delete this contact information?')) return;
  contactInfos.value = contactInfos.value.filter((contact) => contact.id !== contactId);
}

// Contact person functions
function addContactPerson() {
  router.push(`/customers/${customerId.value}/contact-persons/new`);
}

function editContactPerson(personId) {
  router.push(`/customers/${customerId.value}/contact-persons/${personId}/edit`);
}

function deleteContactPerson(personId) {
  if (!confirm('Are you sure you want to delete this contact person?')) return;
  contactPersons.value = contactPersons.value.filter((person) => person.id !== personId);
}

// Helper functions
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
}

function formatCurrency(amount) {
  if (!amount) return '€0.00';
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount);
}

function formatPaymentMethods(methods) {
  if (!methods || methods.length === 0) return 'None specified';
  return Array.isArray(methods) ? methods.join(', ') : methods;
}

function formatContactType(type) {
  if (!type) return 'Unknown';
  const types = {
    PHONE: 'Phone',
    EMAIL: 'Email',
    FAX: 'Fax'
  };
  return types[type] || type;
}
</script>

<style scoped>
.customer-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.inactive-badge {
  background-color: #f87171;
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 10px;
  font-weight: normal;
}

.actions {
  display: flex;
  gap: 10px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 20px;
  overflow-x: auto;
}

.tabs button {
  padding: 10px 16px;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 2px solid transparent;
}

.tabs button.active {
  color: #1f2937;
  border-bottom: 2px solid #2563eb;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 15px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.info-item span {
  font-size: 14px;
}

/* Document styles */
.document-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 15px;
  flex: 1;
  min-width: 120px;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

.document-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.filter-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-options select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
}

.document-table {
  overflow-x: auto;
}

.document-table table {
  width: 100%;
  border-collapse: collapse;
}

.document-table th {
  text-align: left;
  padding: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
  user-select: none;
  position: relative;
}

.document-table th.sortable:hover {
  background-color: #f9fafb;
}

.document-table th.sorted-asc,
.document-table th.sorted-desc {
  color: #2563eb;
  background-color: #f0f9ff;
}

.sort-icon {
  margin-left: 5px;
  font-size: 12px;
}

.draggable-header th {
  cursor: grab;
}

.draggable-header th:active {
  cursor: grabbing;
}

.document-table td {
  padding: 12px 10px;
  font-size: 14px;
  border-bottom: 1px solid #e5e7eb;
}

.document-table tr:hover {
  background-color: #f9fafb;
}

.document-table tr.overdue {
  background-color: #fee2e2;
}

.document-table tr.cancelled {
  background-color: #f3f4f6;
  color: #9ca3af;
}

.document-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.document-link:hover {
  text-decoration: underline;
}

.document-type {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.document-type.order {
  background-color: #dbeafe;
  color: #1e40af;
}

.document-type.invoice {
  background-color: #dcfce7;
  color: #166534;
}

.document-type.delivery {
  background-color: #fef3c7;
  color: #92400e;
}

.document-type.quote {
  background-color: #e0e7ff;
  color: #3730a3;
}

.document-type.credit {
  background-color: #fce7f3;
  color: #9d174d;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.draft {
  background-color: #e5e7eb;
  color: #4b5563;
}

.status-badge.sent {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.paid {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.overdue {
  background-color: #fee2e2;
  color: #b91c1c;
}

.status-badge.cancelled {
  background-color: #f3f4f6;
  color: #6b7280;
}

.status-badge.completed {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.processing {
  background-color: #fef3c7;
  color: #92400e;
}

.document-actions {
  display: flex;
  gap: 5px;
}

.btn.icon {
  width: 28px;
  height: 28px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

/* Shipping address styles */
.shipping-addresses,
.contact-infos,
.contact-persons {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.shipping-address-card,
.contact-info-card,
.contact-person-card {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 15px;
}

.address-header,
.contact-info-header,
.contact-person-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.address-header h3,
.contact-info-header h3,
.contact-person-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.default-badge,
.primary-badge {
  background-color: #10b981;
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
}

.address-content,
.contact-info-content,
.contact-person-content {
  margin-bottom: 15px;
}

.address-content p,
.contact-info-content p,
.contact-person-content p {
  margin: 5px 0;
  font-size: 14px;
}

.address-actions,
.contact-info-actions,
.contact-person-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #6b7280;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  background-color: #f3f4f6;
  color: #1f2937;
}

.btn.primary {
  background-color: #2563eb;
  color: white;
}

.btn.danger {
  background-color: #ef4444;
  color: white;
}

.btn.warning {
  background-color: #f59e0b;
  color: white;
}

.btn.success {
  background-color: #10b981;
  color: white;
}

.btn.small {
  padding: 4px 10px;
  font-size: 12px;
}

.description {
  font-style: italic;
  color: #6b7280;
}

/* Dropdown styles */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
}

.dropdown-toggle::after {
  content: '▼';
  font-size: 10px;
  margin-left: 5px;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  z-index: 10;
  min-width: 160px;
  padding: 5px 0;
  margin: 2px 0 0;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  display: none;
}

.dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 8px 16px;
  clear: both;
  font-weight: 400;
  text-align: left;
  white-space: nowrap;
  background-color: transparent;
  border: 0;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}
</style>
