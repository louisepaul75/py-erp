<template>
  <div class="dashboard">
    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      permanent
      class="bg-grey-lighten-4"
      :width="240"
    >
      <div class="d-flex align-center px-4 py-3 border-b">
        <v-icon icon="mdi-star" color="warning" class="mr-2"></v-icon>
        <span class="text-body-2 font-weight-medium text-grey-darken-3">Favoriten</span>
        <v-btn
          variant="text"
          density="comfortable"
          icon="mdi-chevron-left"
          size="small"
          class="ml-auto"
          @click="toggleDrawer"
        ></v-btn>
      </div>

      <v-list class="px-2">
        <v-list-item
          prepend-icon="mdi-account-group"
          title="Kundenliste"
          class="mb-1 rounded text-body-2"
          density="comfortable"
          color="primary"
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-cart"
          title="Neue Bestellung"
          class="mb-1 rounded text-body-2"
          density="comfortable"
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-chart-bar"
          title="Umsatzstatistik"
          class="mb-1 rounded text-body-2"
          density="comfortable"
        ></v-list-item>
      </v-list>

      <v-divider class="my-2"></v-divider>

      <div class="px-4 py-2">
        <span class="text-caption font-weight-medium text-grey-darken-1">LETZTE ZUGRIFFE</span>
      </div>

      <v-list class="px-2">
        <v-list-item
          v-for="item in recentAccess"
          :key="item.title"
          :prepend-icon="item.icon"
          :title="item.title"
          class="mb-1 rounded text-body-2"
          density="comfortable"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main class="bg-grey-lighten-4">
      <v-container class="py-4">
        <!-- Recent Orders -->
        <v-card class="mb-6" flat>
          <div class="d-flex align-center px-6 py-4 border-b">
            <span class="text-h6 font-weight-medium">Bestellungen nach Liefertermin</span>
            <v-spacer></v-spacer>
            <v-text-field
              v-model="searchQuery"
              prepend-inner-icon="mdi-magnify"
              placeholder="Suchen..."
              hide-details
              density="compact"
              variant="outlined"
              class="max-w-xs"
            ></v-text-field>
          </div>
          <v-table>
            <thead>
              <tr>
                <th class="text-caption font-weight-medium text-grey-darken-1">AUFTRAG</th>
                <th class="text-caption font-weight-medium text-grey-darken-1">KUNDE</th>
                <th class="text-caption font-weight-medium text-grey-darken-1">LIEFERTERMIN</th>
                <th class="text-caption font-weight-medium text-grey-darken-1">STATUS</th>
                <th class="text-caption font-weight-medium text-grey-darken-1">BETRAG</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.id" class="text-body-2">
                <td>{{ order.id }}</td>
                <td>{{ order.customer }}</td>
                <td>{{ order.deliveryDate }}</td>
                <td>
                  <v-chip
                    :color="getStatusColor(order.status)"
                    size="small"
                    class="font-weight-medium text-caption"
                    variant="tonal"
                  >
                    {{ order.status }}
                  </v-chip>
                </td>
                <td>{{ order.amount }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>

        <!-- Quick Access -->
        <v-card class="mb-6" flat>
          <div class="px-6 py-4 border-b">
            <span class="text-h6 font-weight-medium">Schnellzugriff</span>
          </div>
          <v-card-text>
            <v-row>
              <v-col v-for="tile in menuTiles" :key="tile.title" cols="6" sm="4" md="3" lg="2">
                <v-hover v-slot="{ isHovering, props }">
                  <v-card
                    v-bind="props"
                    :elevation="isHovering ? 2 : 0"
                    class="pa-4 text-center transition-all duration-200"
                    :class="{ 'bg-grey-lighten-4': isHovering }"
                  >
                    <v-icon :icon="tile.icon" size="24" class="mb-2 text-grey-darken-1"></v-icon>
                    <div class="text-body-2">{{ tile.title }}</div>
                  </v-card>
                </v-hover>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-row>
          <!-- Important Links -->
          <v-col cols="12" md="6">
            <v-card flat>
              <div class="px-6 py-4 border-b">
                <span class="text-h6 font-weight-medium">Wichtige Links</span>
              </div>
              <v-list class="pa-2">
                <v-list-item
                  v-for="link in importantLinks"
                  :key="link"
                  :title="link"
                  prepend-icon="mdi-link"
                  class="rounded text-body-2"
                  density="comfortable"
                ></v-list-item>
              </v-list>
            </v-card>
          </v-col>

          <!-- News Board -->
          <v-col cols="12" md="6">
            <v-card flat>
              <div class="px-6 py-4 border-b">
                <span class="text-h6 font-weight-medium">Interne Pinnwand</span>
              </div>
              <v-card-text>
                <div v-for="news in newsItems" :key="news.title" class="mb-4 pb-4 border-b">
                  <div class="d-flex align-center mb-2">
                    <span class="text-body-2 font-weight-medium">{{ news.title }}</span>
                    <span class="text-caption text-grey-darken-1 ml-auto">{{ news.date }}</span>
                  </div>
                  <p class="text-body-2 text-grey-darken-1 mb-0">{{ news.content }}</p>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  VHover, 
  VIcon, 
  VBtn, 
  VList, 
  VListItem, 
  VDivider, 
  VNavigationDrawer,
  VAppBar, 
  VAppBarNavIcon, 
  VAppBarTitle, 
  VSpacer, 
  VBadge, 
  VAvatar, 
  VImg,
  VMain, 
  VContainer, 
  VCard, 
  VCardText, 
  VTextField, 
  VTable, 
  VChip,
  VRow, 
  VCol
} from 'vuetify/components'

// UI state
const drawer = ref(true)
const searchQuery = ref('')

const toggleDrawer = () => {
  drawer.value = !drawer.value
}

// Recent access items
const recentAccess = [
  { title: 'Kunde: Müller GmbH', icon: 'mdi-account' },
  { title: 'Auftrag #1082', icon: 'mdi-file-document' },
  { title: 'Kunde: Schmidt AG', icon: 'mdi-account' },
  { title: 'Auftrag #1079', icon: 'mdi-file-document' },
  { title: 'Kunde: Weber KG', icon: 'mdi-account' }
]

// Sample data for recent orders
const recentOrders = [
  { id: 'A-1085', customer: 'Müller GmbH', deliveryDate: '15.03.2025', status: 'Offen', amount: '€2,450.00' },
  { id: 'A-1084', customer: 'Schmidt AG', deliveryDate: '18.03.2025', status: 'In Bearbeitung', amount: '€1,875.50' },
  { id: 'A-1083', customer: 'Weber KG', deliveryDate: '20.03.2025', status: 'Offen', amount: '€3,120.75' },
  { id: 'A-1082', customer: 'Becker GmbH', deliveryDate: '22.03.2025', status: 'Versandt', amount: '€950.25' },
  { id: 'A-1081', customer: 'Fischer & Co.', deliveryDate: '25.03.2025', status: 'Offen', amount: '€4,280.00' },
  { id: 'A-1080', customer: 'Hoffmann AG', deliveryDate: '28.03.2025', status: 'In Bearbeitung', amount: '€1,650.30' }
]

// Filtered orders based on search
const filteredOrders = computed(() => {
  if (!searchQuery.value) return recentOrders
  const query = searchQuery.value.toLowerCase()
  return recentOrders.filter(order => 
    order.id.toLowerCase().includes(query) ||
    order.customer.toLowerCase().includes(query)
  )
})

// Menu tiles
const menuTiles = [
  { title: 'Kunden', icon: 'mdi-account-group' },
  { title: 'Bestellungen', icon: 'mdi-cart' },
  { title: 'Produkte', icon: 'mdi-package-variant' },
  { title: 'Rechnungen', icon: 'mdi-credit-card' },
  { title: 'Kalender', icon: 'mdi-calendar' },
  { title: 'Berichte', icon: 'mdi-file-chart' },
  { title: 'Lieferungen', icon: 'mdi-truck' },
  { title: 'Aufgaben', icon: 'mdi-clipboard-list' },
  { title: 'Datenbank', icon: 'mdi-database' },
  { title: 'Statistiken', icon: 'mdi-chart-bar' },
  { title: 'Analysen', icon: 'mdi-chart-pie' },
  { title: 'Kontakte', icon: 'mdi-account-plus' }
]

// Important links
const importantLinks = [
  'Unternehmenshandbuch',
  'Intranet',
  'Supportportal',
  'Schulungsvideos',
  'Produktkatalog',
  'Preisliste 2025',
  'Urlaubsplaner',
  'IT-Helpdesk',
  'Qualitätsmanagement',
  'Mitarbeiterportal'
]

// News items
const newsItems = [
  { 
    title: 'Neue Produktlinie ab April', 
    date: '09.03.2025', 
    content: 'Ab April führen wir eine neue Produktlinie ein. Schulungen finden nächste Woche statt.' 
  },
  { 
    title: 'Systemwartung am Wochenende', 
    date: '08.03.2025', 
    content: 'Das System wird am Samstag von 22:00 bis 02:00 Uhr für Wartungsarbeiten nicht verfügbar sein.' 
  },
  { 
    title: 'Neue Vertriebspartnerschaft', 
    date: '05.03.2025', 
    content: 'Wir freuen uns, eine neue Partnerschaft mit der Firma XYZ bekannt zu geben.' 
  }
]

// Helper function for order status colors
const getStatusColor = (status) => {
  switch (status) {
    case 'Offen': return 'warning'
    case 'In Bearbeitung': return 'info'
    case 'Versandt': return 'success'
    default: return 'grey'
  }
}
</script>

<style>
:root {
  --v-theme-surface: #ffffff;
}

.v-card {
  border: 1px solid #e5e7eb !important;
  box-shadow: none !important;
}

.border-b {
  border-bottom: 1px solid #e5e7eb !important;
}

.v-list-item--density-comfortable {
  min-height: 40px !important;
}

.v-navigation-drawer {
  border-right: 1px solid #e5e7eb !important;
}
</style>