<template>
  <div class="customer-overview p-4 md:p-6">
    <h1 class="text-2xl font-bold mb-6">Kundenübersicht</h1>

    <!-- Quick and Advanced Search -->
    <div class="mb-6 bg-white rounded-lg shadow p-4">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- Quick Search -->
        <div class="flex-1">
          <div class="relative">
            <input
              v-model="quickSearch"
              type="text"
              placeholder="Schnellsuche..."
              class="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              @input="applyFilters"
            />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 absolute left-3 top-2.5 text-gray-400"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </div>
        </div>

        <!-- Toggle Advanced Search -->
        <button
          @click="showAdvancedSearch = !showAdvancedSearch"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center"
        >
          <span>Erweiterte Suche</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 ml-2"
            :class="{ 'rotate-180': showAdvancedSearch }"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
      </div>

      <!-- Advanced Search Panel -->
      <div
        v-if="showAdvancedSearch"
        class="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Kundenname</label>
          <input
            v-model="advancedSearch.name"
            type="text"
            class="w-full p-2 border rounded-lg"
            @input="applyFilters"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">E-Mail</label>
          <input
            v-model="advancedSearch.email"
            type="text"
            class="w-full p-2 border rounded-lg"
            @input="applyFilters"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Stadt</label>
          <input
            v-model="advancedSearch.city"
            type="text"
            class="w-full p-2 border rounded-lg"
            @input="applyFilters"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">PLZ</label>
          <input
            v-model="advancedSearch.postalCode"
            type="text"
            class="w-full p-2 border rounded-lg"
            @input="applyFilters"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Kundennummer</label>
          <input
            v-model="advancedSearch.documentNumber"
            type="text"
            class="w-full p-2 border rounded-lg"
            @input="applyFilters"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Shop-Nr.</label>
          <input
            v-model="advancedSearch.shopNumber"
            type="text"
            class="w-full p-2 border rounded-lg"
            @input="applyFilters"
          />
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="mb-6 bg-white rounded-lg shadow p-4">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- Replace the B2B/B2C Filter dropdown with radio buttons -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Kundentyp</label>
          <div class="flex space-x-4">
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="filters.customerType"
                value="all"
                class="form-radio"
                @change="applyFilters"
              />
              <span class="ml-2">Alle</span>
            </label>
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="filters.customerType"
                value="b2b"
                class="form-radio"
                @change="applyFilters"
              />
              <span class="ml-2">Partner (B2B)</span>
            </label>
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="filters.customerType"
                value="b2c"
                class="form-radio"
                @change="applyFilters"
              />
              <span class="ml-2">Privatkunden (B2C)</span>
            </label>
          </div>
        </div>

        <!-- Add after the customer type filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Land</label>
          <select
            v-model="filters.country"
            class="w-full p-2 border rounded-lg"
            @change="applyFilters"
          >
            <option value="all">Alle Länder</option>
            <option v-for="country in availableCountries" :key="country" :value="country">
              {{ country }}
            </option>
          </select>
        </div>

        <!-- Last Order Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Letzte Bestellung</label>
          <select
            v-model="filters.lastOrderYears"
            class="w-full p-2 border rounded-lg"
            @change="applyFilters"
          >
            <option value="all">Alle</option>
            <option value="1">Innerhalb des letzten Jahres</option>
            <option value="2">Innerhalb der letzten 2 Jahre</option>
            <option value="3">Innerhalb der letzten 3 Jahre</option>
            <option value="4">Innerhalb der letzten 4 Jahre</option>
            <option value="5">Innerhalb der letzten 5 Jahre</option>
            <option value="older">Älter als 5 Jahre</option>
          </select>
        </div>

        <!-- Revenue Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Umsatz (365 Tage)</label>
          <div class="flex items-center space-x-2">
            <div class="flex-1">
              <div class="text-xs text-gray-500 mb-1">Von</div>
              <input
                v-model.number="filters.minRevenue"
                type="number"
                class="w-full p-2 border rounded-lg"
                @input="applyFilters"
              />
            </div>
            <div class="flex-1">
              <div class="text-xs text-gray-500 mb-1">Bis</div>
              <input
                v-model.number="filters.maxRevenue"
                type="number"
                class="w-full p-2 border rounded-lg"
                @input="applyFilters"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Count and Reset -->
    <div class="flex justify-between items-center mb-4">
      <p class="text-gray-600">{{ filteredCustomers.length }} Kunden gefunden</p>
      <button @click="resetFilters" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg">
        Filter zurücksetzen
      </button>
    </div>

    <!-- Customer Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                v-for="(column, index) in displayColumns"
                :key="column.key"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                @click="sortBy(column.key)"
                draggable="true"
                @dragstart="dragStart($event, index)"
                @dragover.prevent
                @dragenter.prevent
                @drop="drop($event, index)"
                :class="{ 'bg-gray-100': draggedColumnIndex === index }"
              >
                <div class="flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 mr-1 text-gray-400 cursor-move"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <line x1="8" y1="6" x2="21" y2="6"></line>
                    <line x1="8" y1="12" x2="21" y2="12"></line>
                    <line x1="8" y1="18" x2="21" y2="18"></line>
                    <line x1="3" y1="6" x2="3.01" y2="6"></line>
                    <line x1="3" y1="12" x2="3.01" y2="12"></line>
                    <line x1="3" y1="18" x2="3.01" y2="18"></line>
                  </svg>
                  {{ column.label }}
                  <svg
                    v-if="sortColumn === column.key"
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 ml-1"
                    :class="{ 'rotate-180': !sortAscending }"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="18 15 12 9 6 15"></polyline>
                  </svg>
                </div>
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Aktionen
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="customer in paginatedCustomers" :key="customer.id" class="hover:bg-gray-50">
              <td
                v-for="column in displayColumns"
                :key="column.key"
                class="px-6 py-4 whitespace-nowrap"
              >
                <template v-if="column.key === 'name'">
                  <div class="font-medium text-gray-900">{{ customer.name }}</div>
                  <div class="text-sm text-gray-500">{{ customer.email }}</div>
                </template>
                <template v-else-if="column.key === 'type'">
                  <span
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="
                      customer.type === 'b2b'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800'
                    "
                  >
                    {{ customer.type.toUpperCase() }}
                  </span>
                </template>
                <template v-else-if="column.key === 'lastOrderDate'">
                  {{ formatDate(customer.lastOrderDate) }}
                </template>
                <template v-else-if="column.key === 'revenue365Days'">
                  {{ formatCurrency(customer.revenue365Days) }}
                </template>
                <template v-else>
                  {{ customer[column.key] }}
                </template>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  class="text-indigo-600 hover:text-indigo-900 mr-3"
                  @click="viewCustomerDetails(customer)"
                >
                  Details
                </button>
                <div class="relative inline-block">
                  <button
                    class="text-gray-600 hover:text-gray-900"
                    @click="toggleActionMenu(customer.id)"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      class="h-5 w-5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <circle cx="12" cy="12" r="1"></circle>
                      <circle cx="19" cy="12" r="1"></circle>
                      <circle cx="5" cy="12" r="1"></circle>
                    </svg>
                  </button>
                  <div
                    v-if="activeActionMenu === customer.id"
                    class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10"
                  >
                    <div class="py-1">
                      <a
                        href="#"
                        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        @click.prevent="editCustomer(customer)"
                        >Bearbeiten</a
                      >
                      <a
                        href="#"
                        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        @click.prevent="viewOrders(customer)"
                        >Bestellungen anzeigen</a
                      >
                      <a
                        href="#"
                        class="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                        @click.prevent="deleteCustomer(customer)"
                        >Löschen</a
                      >
                    </div>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="filteredCustomers.length === 0">
              <td :colspan="displayColumns.length + 1" class="px-6 py-4 text-center text-gray-500">
                Keine Kunden gefunden
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-6 py-3 flex items-center justify-between border-t border-gray-200">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="currentPage > 1 ? currentPage-- : null"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
          >
            Zurück
          </button>
          <button
            @click="currentPage < totalPages ? currentPage++ : null"
            :disabled="currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
          >
            Weiter
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Zeige <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span> bis
              <span class="font-medium">{{
                Math.min(currentPage * pageSize, filteredCustomers.length)
              }}</span>
              von <span class="font-medium">{{ filteredCustomers.length }}</span> Einträgen
            </p>
          </div>
          <div>
            <nav
              class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
              aria-label="Pagination"
            >
              <button
                @click="currentPage = 1"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
              >
                <span class="sr-only">Erste Seite</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="11 17 6 12 11 7"></polyline>
                  <polyline points="18 17 13 12 18 7"></polyline>
                </svg>
              </button>
              <button
                @click="currentPage > 1 ? currentPage-- : null"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
              >
                <span class="sr-only">Zurück</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="15 18 9 12 15 6"></polyline>
                </svg>
              </button>

              <button
                v-for="page in displayedPages"
                :key="page"
                @click="currentPage = page"
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium hover:bg-gray-50"
                :class="
                  currentPage === page
                    ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                    : 'text-gray-500'
                "
              >
                {{ page }}
              </button>

              <button
                @click="currentPage < totalPages ? currentPage++ : null"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
              >
                <span class="sr-only">Weiter</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </button>
              <button
                @click="currentPage = totalPages"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
              >
                <span class="sr-only">Letzte Seite</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="13 17 18 12 13 7"></polyline>
                  <polyline points="6 17 11 12 6 7"></polyline>
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

// Sample customer data
const customers = ref([]);

// Generate sample data
onMounted(() => {
  const sampleData = [];
  const customerTypes = ['b2b', 'b2c'];
  const cities = [
    'Berlin',
    'Hamburg',
    'München',
    'Köln',
    'Frankfurt',
    'Stuttgart',
    'Düsseldorf',
    'Leipzig'
  ];
  const countries = [
    'Deutschland',
    'Österreich',
    'Schweiz',
    'Frankreich',
    'Italien',
    'Niederlande',
    'Belgien'
  ];
  const now = new Date();

  for (let i = 1; i <= 100; i++) {
    const type = customerTypes[Math.floor(Math.random() * customerTypes.length)];
    const isB2B = type === 'b2b';

    // Generate a date between now and 6 years ago
    const lastOrderDate = new Date();
    lastOrderDate.setFullYear(now.getFullYear() - Math.floor(Math.random() * 6));
    lastOrderDate.setMonth(Math.floor(Math.random() * 12));
    lastOrderDate.setDate(Math.floor(Math.random() * 28) + 1);

    sampleData.push({
      id: i,
      name: isB2B ? `Firma ${i} GmbH` : `Kunde ${i}`,
      email: isB2B ? `kontakt@firma${i}.de` : `kunde${i}@example.com`,
      type: type,
      phone: `+49 ${Math.floor(Math.random() * 900) + 100} ${Math.floor(Math.random() * 9000000) + 1000000}`,
      city: cities[Math.floor(Math.random() * cities.length)],
      postalCode: `${Math.floor(Math.random() * 90000) + 10000}`,
      country: countries[Math.floor(Math.random() * countries.length)],
      lastOrderDate: lastOrderDate,
      customerNumber: `CUST-${Math.floor(Math.random() * 900000) + 100000}`,
      shopNumber: `SHOP-${Math.floor(Math.random() * 900) + 100}`,
      revenue365Days: isB2B
        ? Math.floor(Math.random() * 100000) + 10000
        : Math.floor(Math.random() * 2000) + 100
    });
  }

  customers.value = sampleData;

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative.inline-block')) {
      closeActionMenus();
    }
  });
});

// Table columns
const allColumns = [
  { key: 'name', label: 'Kunde' },
  { key: 'type', label: 'Typ' },
  { key: 'phone', label: 'Telefon' },
  { key: 'city', label: 'Stadt' },
  { key: 'country', label: 'Land' },
  { key: 'lastOrderDate', label: 'Letzte Bestellung' },
  { key: 'customerNumber', label: 'Kundennummer' },
  { key: 'revenue365Days', label: 'Umsatz (365 Tage)' }
];

// Column order management
const columnOrder = ref([...Array(allColumns.length).keys()]); // Default order: 0, 1, 2, ...
const draggedColumnIndex = ref(null);

// Computed property for columns in the current display order
const displayColumns = computed(() => {
  return columnOrder.value.map((index) => allColumns[index]);
});

// Drag and drop handlers
const dragStart = (event, index) => {
  draggedColumnIndex.value = index;
  event.dataTransfer.effectAllowed = 'move';
  // Required for Firefox
  event.dataTransfer.setData('text/plain', index);
};

const drop = (event, targetIndex) => {
  event.preventDefault();
  if (draggedColumnIndex.value !== null) {
    const newOrder = [...columnOrder.value];
    const draggedValue = newOrder[draggedColumnIndex.value];

    // Remove the dragged item
    newOrder.splice(draggedColumnIndex.value, 1);

    // Insert at the new position
    newOrder.splice(targetIndex, 0, draggedValue);

    columnOrder.value = newOrder;
    draggedColumnIndex.value = null;
  }
};

// Search and filters
const quickSearch = ref('');
const showAdvancedSearch = ref(false);
const advancedSearch = ref({
  name: '',
  email: '',
  city: '',
  postalCode: '',
  documentNumber: '',
  shopNumber: ''
});

const filters = ref({
  customerType: 'all',
  country: 'all',
  lastOrderYears: 'all', // Default: all
  minRevenue: 0,
  maxRevenue: null
});

// Sorting
const sortColumn = ref('name');
const sortAscending = ref(true);

// Pagination
const currentPage = ref(1);
const pageSize = ref(10);

// Reset filters
const resetFilters = () => {
  quickSearch.value = '';
  advancedSearch.value = {
    name: '',
    email: '',
    city: '',
    postalCode: '',
    documentNumber: '',
    shopNumber: ''
  };
  filters.value = {
    customerType: 'all',
    country: 'all',
    lastOrderYears: 'all',
    minRevenue: 0,
    maxRevenue: null
  };
  sortColumn.value = 'name';
  sortAscending.value = true;
  currentPage.value = 1;
  applyFilters();
};

// Apply filters
const applyFilters = () => {
  currentPage.value = 1; // Reset to first page when filters change
};

// Filter customers based on search and filters
const filteredCustomers = computed(() => {
  const now = new Date();
  const fourYearsAgo = new Date();
  fourYearsAgo.setFullYear(now.getFullYear() - parseInt(filters.value.lastOrderYears));

  return customers.value
    .filter((customer) => {
      // Quick search
      if (quickSearch.value) {
        const searchTerm = quickSearch.value.toLowerCase();
        const searchableFields = [
          customer.name.toLowerCase(),
          customer.email.toLowerCase(),
          customer.city.toLowerCase(),
          customer.type.toLowerCase()
        ];

        if (!searchableFields.some((field) => field.includes(searchTerm))) {
          return false;
        }
      }

      // Advanced search
      if (
        advancedSearch.value.name &&
        !customer.name.toLowerCase().includes(advancedSearch.value.name.toLowerCase())
      ) {
        return false;
      }

      if (
        advancedSearch.value.email &&
        !customer.email.toLowerCase().includes(advancedSearch.value.email.toLowerCase())
      ) {
        return false;
      }

      if (
        advancedSearch.value.city &&
        !customer.city.toLowerCase().includes(advancedSearch.value.city.toLowerCase())
      ) {
        return false;
      }

      if (
        advancedSearch.value.postalCode &&
        !customer.postalCode.includes(advancedSearch.value.postalCode)
      ) {
        return false;
      }

      if (
        advancedSearch.value.documentNumber &&
        !customer.customerNumber.includes(advancedSearch.value.documentNumber)
      ) {
        return false;
      }

      if (
        advancedSearch.value.shopNumber &&
        !customer.shopNumber.includes(advancedSearch.value.shopNumber)
      ) {
        return false;
      }

      // Customer type filter
      if (filters.value.customerType !== 'all' && customer.type !== filters.value.customerType) {
        return false;
      }

      // Country filter
      if (filters.value.country !== 'all' && customer.country !== filters.value.country) {
        return false;
      }

      // Last order filter
      if (filters.value.lastOrderYears !== 'all') {
        if (filters.value.lastOrderYears !== 'older') {
          const yearsAgo = new Date();
          yearsAgo.setFullYear(now.getFullYear() - parseInt(filters.value.lastOrderYears));
          if (customer.lastOrderDate < yearsAgo) {
            return false;
          }
        } else {
          // "Older than 5 years"
          const fiveYearsAgo = new Date();
          fiveYearsAgo.setFullYear(now.getFullYear() - 5);
          if (customer.lastOrderDate >= fiveYearsAgo) {
            return false;
          }
        }
      }

      // Revenue filter
      if (customer.revenue365Days < filters.value.minRevenue) {
        return false;
      }
      if (filters.value.maxRevenue && customer.revenue365Days > filters.value.maxRevenue) {
        return false;
      }

      return true;
    })
    .sort((a, b) => {
      let valueA = a[sortColumn.value];
      let valueB = b[sortColumn.value];

      // Handle date comparison
      if (sortColumn.value === 'lastOrderDate') {
        return sortAscending.value
          ? valueA.getTime() - valueB.getTime()
          : valueB.getTime() - valueA.getTime();
      }

      // Handle string comparison
      if (typeof valueA === 'string') {
        valueA = valueA.toLowerCase();
        valueB = valueB.toLowerCase();
      }

      if (valueA < valueB) return sortAscending.value ? -1 : 1;
      if (valueA > valueB) return sortAscending.value ? 1 : -1;
      return 0;
    });
});

// Sort by column
const sortBy = (column) => {
  if (sortColumn.value === column) {
    sortAscending.value = !sortAscending.value;
  } else {
    sortColumn.value = column;
    sortAscending.value = true;
  }
};

// Pagination
const totalPages = computed(() => {
  return Math.ceil(filteredCustomers.value.length / pageSize.value);
});

const paginatedCustomers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredCustomers.value.slice(start, end);
});

// Calculate displayed page numbers
const displayedPages = computed(() => {
  const pages = [];
  const maxVisiblePages = 5;

  if (totalPages.value <= maxVisiblePages) {
    // Show all pages if there are few
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i);
    }
  } else {
    // Show a window of pages around current page
    let startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1);

    // Adjust if we're near the end
    if (endPage === totalPages.value) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
  }

  return pages;
});

// Add this computed property
const availableCountries = computed(() => {
  const countries = new Set();
  customers.value.forEach((customer) => {
    countries.add(customer.country);
  });
  return Array.from(countries).sort();
});

// Add these for the action menu
const activeActionMenu = ref(null);

const toggleActionMenu = (customerId) => {
  if (activeActionMenu.value === customerId) {
    activeActionMenu.value = null;
  } else {
    activeActionMenu.value = customerId;
  }
};

// Close menu when clicking outside
const closeActionMenus = () => {
  activeActionMenu.value = null;
};

// Action functions
const viewCustomerDetails = (customer) => {
  alert(`Viewing details for ${customer.name}`);
  // In a real app, you would navigate to a details page or open a modal
};

const editCustomer = (customer) => {
  alert(`Editing ${customer.name}`);
  // In a real app, you would navigate to an edit page or open a modal
};

const viewOrders = (customer) => {
  alert(`Viewing orders for ${customer.name}`);
  // In a real app, you would navigate to an orders page filtered for this customer
};

const deleteCustomer = (customer) => {
  if (confirm(`Sind Sie sicher, dass Sie ${customer.name} löschen möchten?`)) {
    alert(`${customer.name} wurde gelöscht`);
    // In a real app, you would call an API to delete the customer
  }
};

// Helper functions
const getInitials = (name) => {
  return name
    .split(' ')
    .map((word) => word.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2);
};

const formatDate = (date) => {
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(date);
};

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount);
};
</script>

<style scoped>
/* Additional styles if needed */
.customer-overview {
  background-color: #f9fafb;
  min-height: 100vh;
}
</style>
