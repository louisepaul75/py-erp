<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-6">Kundenübersicht</h1>

        <!-- Quick and Advanced Search -->
        <v-card class="mb-6">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="quickSearch"
                  label="Schnellsuche..."
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  @input="applyFilters"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4" class="d-flex align-center">
                <v-btn
                  @click="showAdvancedSearch = !showAdvancedSearch"
                  variant="tonal"
                  color="primary"
                >
                  Erweiterte Suche
                  <v-icon right>
                    {{ showAdvancedSearch ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                  </v-icon>
                </v-btn>
              </v-col>
            </v-row>

            <!-- Advanced Search Panel -->
            <v-expand-transition>
              <div v-if="showAdvancedSearch">
                <v-row class="mt-4">
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="advancedSearch.name"
                      label="Kundenname"
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="advancedSearch.email"
                      label="E-Mail"
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="advancedSearch.city"
                      label="Stadt"
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="advancedSearch.postalCode"
                      label="PLZ"
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="advancedSearch.documentNumber"
                      label="Kundennummer"
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="advancedSearch.shopNumber"
                      label="Shop-Nr."
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </div>
            </v-expand-transition>
          </v-card-text>
        </v-card>

        <!-- Filters -->
        <v-card class="mb-6">
          <v-card-text>
            <v-row>
              <!-- Customer Type Filter -->
              <v-col cols="12" md="3">
                <v-radio-group
                  v-model="filters.customerType"
                  @update:model-value="applyFilters"
                  density="comfortable"
                >
                  <template v-slot:label>
                    <div class="text-subtitle-2 mb-2">Kundentyp</div>
                  </template>
                  <v-radio label="Alle" value="all"></v-radio>
                  <v-radio label="Partner (B2B)" value="b2b"></v-radio>
                  <v-radio label="Privatkunden (B2C)" value="b2c"></v-radio>
                </v-radio-group>
              </v-col>

              <!-- Country Filter -->
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.country"
                  :items="countryItems"
                  label="Land"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-earth"
                  @update:model-value="applyFilters"
                ></v-select>
              </v-col>

              <!-- Last Order Filter -->
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.lastOrderYears"
                  :items="lastOrderItems"
                  label="Letzte Bestellung"
                  variant="outlined"
                  density="comfortable"
                  @update:model-value="applyFilters"
                ></v-select>
              </v-col>

              <!-- Revenue Filter -->
              <v-col cols="12" md="3">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="filters.minRevenue"
                      label="Umsatz von"
                      type="number"
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="filters.maxRevenue"
                      label="Umsatz bis"
                      type="number"
                      variant="outlined"
                      density="comfortable"
                      @input="applyFilters"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Results Count and Reset -->
        <div class="d-flex justify-space-between align-center mb-4">
          <p class="text-grey-darken-1">{{ filteredCustomers.length }} Kunden gefunden</p>
          <v-btn
            @click="resetFilters"
            variant="tonal"
            prepend-icon="mdi-refresh"
            color="grey-darken-1"
          >
            Filter zurücksetzen
          </v-btn>
        </div>

        <!-- Customer Table -->
        <v-card>
          <v-data-table
            :headers="headers"
            :items="filteredCustomers"
            :items-per-page="pageSize"
            :page="currentPage"
            @update:page="currentPage = $event"
          >
            <template v-slot:item="{ item }">
              <tr>
                <td>{{ item.name }}</td>
                <td>
                  <v-chip
                    :class="item.type === 'b2b' ? 'b2b-chip' : 'b2c-chip'"
                    size="small"
                    class="font-weight-medium"
                  >
                    {{ item.type.toUpperCase() }}
                  </v-chip>
                </td>
                <td>{{ item.phone }}</td>
                <td>{{ item.city }}</td>
                <td>{{ item.country }}</td>
                <td>{{ formatDate(item.lastOrderDate) }}</td>
                <td>{{ item.customerNumber }}</td>
                <td class="text-right">{{ formatCurrency(item.revenue365Days) }}</td>
                <td class="text-right">
                  <v-btn
                    variant="text"
                    color="primary"
                    size="small"
                    class="mr-2"
                    @click="viewCustomerDetails(item)"
                  >
                    Details
                  </v-btn>

                  <v-menu location="bottom end">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        icon="mdi-dots-vertical"
                        variant="text"
                        size="small"
                        v-bind="props"
                      ></v-btn>
                    </template>

                    <v-list density="comfortable">
                      <v-list-item @click="editCustomer(item)">
                        <v-list-item-title>Bearbeiten</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="viewOrders(item)">
                        <v-list-item-title>Bestellungen anzeigen</v-list-item-title>
                      </v-list-item>
                      <v-divider></v-divider>
                      <v-list-item @click="deleteCustomer(item)" color="error">
                        <v-list-item-title>Löschen</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </td>
              </tr>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { salesApi } from '@/services/api';
import {
  VContainer,
  VRow,
  VCol,
  VCard,
  VCardText,
  VTextField,
  VBtn,
  VIcon,
  VExpandTransition,
  VRadioGroup,
  VRadio,
  VSelect,
  VDataTable,
  VChip,
  VMenu,
  VList,
  VListItem,
  VListItemTitle,
  VDivider
} from 'vuetify/components';

export default {
  name: 'CustomerOverview',
  components: {
    VContainer,
    VRow,
    VCol,
    VCard,
    VCardText,
    VTextField,
    VBtn,
    VIcon,
    VExpandTransition,
    VRadioGroup,
    VRadio,
    VSelect,
    VDataTable,
    VChip,
    VMenu,
    VList,
    VListItem,
    VListItemTitle,
    VDivider
  },
  data() {
    return {
      customers: [],
      quickSearch: '',
      showAdvancedSearch: false,
      advancedSearch: {
        name: '',
        email: '',
        city: '',
        postalCode: '',
        documentNumber: '',
        shopNumber: ''
      },
      filters: {
        customerType: 'all',
        country: 'all',
        lastOrderYears: 'all',
        minRevenue: null,
        maxRevenue: null
      },
      currentPage: 1,
      pageSize: 10,
      headers: [
        { title: 'Kunde', key: 'name', sortable: true },
        { title: 'Typ', key: 'type', sortable: true },
        { title: 'Telefon', key: 'phone', sortable: true },
        { title: 'Stadt', key: 'city', sortable: true },
        { title: 'Land', key: 'country', sortable: true },
        { title: 'Letzte Bestellung', key: 'lastOrderDate', sortable: true },
        { title: 'Kundennummer', key: 'customerNumber', sortable: true },
        { title: 'Umsatz (365 Tage)', key: 'revenue365Days', sortable: true },
        { title: 'Aktionen', key: 'actions', sortable: false, align: 'end' }
      ],
      loading: false,
      totalCustomers: 0,
      error: null
    };
  },

  computed: {
    filteredCustomers() {
      return this.customers.filter((customer) => {
        // Quick search
        if (this.quickSearch) {
          const searchTerm = this.quickSearch.toLowerCase();
          const searchableFields = [
            customer.name.toLowerCase(),
            customer.email.toLowerCase(),
            customer.city.toLowerCase(),
            customer.customerNumber.toLowerCase(),
            customer.phone.toLowerCase()
          ];

          if (!searchableFields.some((field) => field.includes(searchTerm))) {
            return false;
          }
        }

        // Advanced search
        if (
          this.advancedSearch.name &&
          !customer.name.toLowerCase().includes(this.advancedSearch.name.toLowerCase())
        ) {
          return false;
        }

        if (
          this.advancedSearch.email &&
          !customer.email.toLowerCase().includes(this.advancedSearch.email.toLowerCase())
        ) {
          return false;
        }

        if (
          this.advancedSearch.city &&
          !customer.city.toLowerCase().includes(this.advancedSearch.city.toLowerCase())
        ) {
          return false;
        }

        if (
          this.advancedSearch.postalCode &&
          !customer.postalCode.includes(this.advancedSearch.postalCode)
        ) {
          return false;
        }

        if (
          this.advancedSearch.documentNumber &&
          !customer.customerNumber.includes(this.advancedSearch.documentNumber)
        ) {
          return false;
        }

        if (
          this.advancedSearch.shopNumber &&
          !customer.shopNumber.includes(this.advancedSearch.shopNumber)
        ) {
          return false;
        }

        // Customer type filter
        if (this.filters.customerType !== 'all' && customer.type !== this.filters.customerType) {
          return false;
        }

        // Country filter
        if (this.filters.country !== 'all' && customer.country !== this.filters.country) {
          return false;
        }

        // Last order filter
        if (this.filters.lastOrderYears !== 'all') {
          const now = new Date();
          if (this.filters.lastOrderYears !== 'older') {
            const yearsAgo = new Date();
            yearsAgo.setFullYear(now.getFullYear() - parseInt(this.filters.lastOrderYears));
            if (customer.lastOrderDate < yearsAgo) {
              return false;
            }
          } else {
            const fiveYearsAgo = new Date();
            fiveYearsAgo.setFullYear(now.getFullYear() - 5);
            if (customer.lastOrderDate >= fiveYearsAgo) {
              return false;
            }
          }
        }

        // Revenue filter
        if (this.filters.minRevenue && customer.revenue365Days < this.filters.minRevenue) {
          return false;
        }
        if (this.filters.maxRevenue && customer.revenue365Days > this.filters.maxRevenue) {
          return false;
        }

        return true;
      });
    },

    countryItems() {
      const countries = [...new Set(this.customers.map((c) => c.country))].sort();
      return [
        { title: 'Alle Länder', value: 'all' },
        ...countries.map((country) => ({ title: country, value: country }))
      ];
    },

    lastOrderItems() {
      return [
        { title: 'Alle', value: 'all' },
        { title: 'Innerhalb des letzten Jahres', value: '1' },
        { title: 'Innerhalb der letzten 2 Jahre', value: '2' },
        { title: 'Innerhalb der letzten 3 Jahre', value: '3' },
        { title: 'Innerhalb der letzten 4 Jahre', value: '4' },
        { title: 'Innerhalb der letzten 5 Jahre', value: '5' },
        { title: 'Älter als 5 Jahre', value: 'older' }
      ];
    }
  },

  mounted() {
    this.loadCustomers();
  },

  methods: {
    async loadCustomers() {
      this.loading = true;
      this.error = null;

      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          search: this.quickSearch,
          customer_type:
            this.filters.customerType !== 'all' ? this.filters.customerType : undefined,
          country: this.filters.country !== 'all' ? this.filters.country : undefined,
          min_revenue: this.filters.minRevenue,
          max_revenue: this.filters.maxRevenue,
          // Add advanced search params
          name: this.advancedSearch.name || undefined,
          email: this.advancedSearch.email || undefined,
          city: this.advancedSearch.city || undefined,
          postal_code: this.advancedSearch.postalCode || undefined,
          customer_number: this.advancedSearch.documentNumber || undefined
        };

        const response = await salesApi.getCustomers(params);
        this.customers = response.data.results.map((customer) => {
          const formatDate = (dateString) => {
            if (!dateString) return null;
            const date = new Date(dateString);
            return isNaN(date.getTime()) ? null : date;
          };

          return {
            id: customer.id,
            name:
              customer.company_name ||
              `${customer.first_name || ''} ${customer.last_name || ''}`.trim(),
            email: customer.email || '',
            type: customer.customer_group
              ? customer.customer_group.toLowerCase().includes('b2b')
                ? 'b2b'
                : 'b2c'
              : 'b2c',
            phone: customer.phone || '',
            city: customer.addresses?.[0]?.city || '',
            postalCode: customer.addresses?.[0]?.postal_code || '',
            country: customer.addresses?.[0]?.country || '',
            lastOrderDate: formatDate(customer.last_order_date),
            customerNumber: customer.customer_number || '',
            revenue365Days: customer.revenue_365_days || 0,
            shopNumber: customer.legacy_address_number || ''
          };
        });
        this.totalCustomers = response.data.count;
      } catch (error) {
        console.error('Error loading customers:', error);
        this.error = 'Failed to load customers. Please try again.';
      } finally {
        this.loading = false;
      }
    },

    applyFilters() {
      this.currentPage = 1;
      this.loadCustomers();
    },

    resetFilters() {
      this.quickSearch = '';
      this.advancedSearch = {
        name: '',
        email: '',
        city: '',
        postalCode: '',
        documentNumber: '',
        shopNumber: ''
      };
      this.filters = {
        customerType: 'all',
        country: 'all',
        lastOrderYears: 'all',
        minRevenue: null,
        maxRevenue: null
      };
      this.currentPage = 1;
      this.loadCustomers();
    },

    viewCustomerDetails(customer) {
      this.$router.push({ name: 'CustomerDetail', params: { id: customer.id } });
    },

    editCustomer(customer) {
      console.log('Edit customer:', customer);
    },

    viewOrders(customer) {
      console.log('View orders:', customer);
    },

    async deleteCustomer(customer) {
      if (confirm(`Sind Sie sicher, dass Sie ${customer.name} löschen möchten?`)) {
        try {
          await salesApi.deleteCustomer(customer.id);
          const index = this.customers.findIndex((c) => c.id === customer.id);
          if (index !== -1) {
            this.customers.splice(index, 1);
          }
        } catch (error) {
          console.error('Error deleting customer:', error);
          alert('Failed to delete customer. Please try again.');
        }
      }
    },

    formatDate(date) {
      return new Intl.DateTimeFormat('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      }).format(new Date(date));
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount);
    }
  }
};
</script>

<style>
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

.v-radio-group .v-label {
  opacity: 1;
}

.b2b-chip {
  background-color: #dbeafe !important; /* Tailwind blue-100 */
  color: #1e40af !important; /* Tailwind blue-800 */
  font-weight: 600 !important;
}

.b2c-chip {
  background-color: #dcfce7 !important; /* Tailwind green-100 */
  color: #166534 !important; /* Tailwind green-800 */
  font-weight: 600 !important;
}
</style>
