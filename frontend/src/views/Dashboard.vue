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
          :icon="drawer ? 'mdi-chevron-left' : 'mdi-chevron-right'"
          size="small"
          class="ml-auto"
          @click="toggleDrawer"
        ></v-btn>
      </div>

      <!-- Favorites List -->
      <div v-if="favoritesStore.favorites.length > 0">
        <v-list class="px-2">
          <v-list-item
            v-for="item in favoritesStore.favorites"
            :key="item.id"
            :prepend-icon="item.icon"
            :title="item.title"
            class="mb-1 rounded text-body-2"
            density="comfortable"
            @click="navigateToFavorite(item)"
          >
            <template v-slot:append>
              <v-btn
                icon="mdi-star"
                size="small"
                color="warning"
                variant="text"
                class="favorite-remove-btn"
                @click.stop="favoritesStore.removeFavorite(item.id)"
              ></v-btn>
            </template>
          </v-list-item>
        </v-list>
      </div>
      <div v-else class="pa-4 text-center text-body-2 text-grey-darken-1">
        Keine Favoriten hinzugefügt. Markieren Sie Elemente mit dem Stern, um sie hier anzuzeigen.
      </div>

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

    <!-- Reopen Sidebar Button (shown when sidebar is closed) -->
    <v-btn
      v-show="!drawer"
      icon="mdi-chevron-right"
      variant="flat"
      size="small"
      color="primary"
      class="sidebar-toggle-btn"
      @click="toggleDrawer"
    ></v-btn>

    <!-- Main Content -->
    <v-main class="bg-grey-lighten-4">
      <v-container class="py-4">
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
                    class="pa-4 text-center transition-all duration-200 position-relative"
                    :class="{ 'bg-grey-lighten-4': isHovering }"
                    @click="navigateTo(tile)"
                  >
                    <v-icon :icon="tile.icon" size="24" class="mb-2 text-grey-darken-1"></v-icon>
                    <div class="text-body-2">{{ tile.title }}</div>
                    
                    <!-- Favorite Toggle Button -->
                    <v-btn
                      :icon="isTileFavorite(tile) ? 'mdi-star' : 'mdi-star-outline'"
                      :color="isTileFavorite(tile) ? 'warning' : 'grey-darken-1'"
                      size="small"
                      variant="text"
                      class="favorite-toggle-btn"
                      :class="{ 'show-on-hover': !isTileFavorite(tile) }"
                      @click.stop="toggleTileFavorite(tile)"
                    ></v-btn>
                  </v-card>
                </v-hover>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

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
                <th class="text-caption font-weight-medium text-grey-darken-1">FAVORIT</th>
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
                <td>
                  <v-btn
                    :icon="isOrderFavorite(order) ? 'mdi-star' : 'mdi-star-outline'"
                    :color="isOrderFavorite(order) ? 'warning' : 'grey'"
                    size="small"
                    variant="text"
                    :class="{ 'show-on-hover': !isOrderFavorite(order) }"
                    @click="toggleOrderFavorite(order)"
                  ></v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>

        <v-row>
          <!-- Important Links -->
          <v-col cols="12" md="6">
            <v-card flat>
              <div class="px-6 py-4 border-b d-flex align-center">
                <span class="text-h6 font-weight-medium">Wichtige Links</span>
                <v-spacer></v-spacer>
                <v-btn
                  variant="text"
                  icon="mdi-star"
                  color="warning"
                  size="small"
                  v-if="linkIsFavorites"
                  @click="removeLinksFromFavorites"
                  title="Von Favoriten entfernen"
                ></v-btn>
                <v-btn
                  variant="text"
                  icon="mdi-star-outline"
                  size="small"
                  class="show-on-hover"
                  v-else
                  @click="addLinksToFavorites"
                  title="Zu Favoriten hinzufügen"
                ></v-btn>
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
              <div class="px-6 py-4 border-b d-flex align-center">
                <span class="text-h6 font-weight-medium">Interne Pinnwand</span>
                <v-spacer></v-spacer>
                <v-btn
                  variant="text"
                  icon="mdi-star"
                  color="warning"
                  size="small"
                  v-if="newsBoardIsFavorite"
                  @click="removeNewsBoardFromFavorites"
                  title="Von Favoriten entfernen"
                ></v-btn>
                <v-btn
                  variant="text"
                  icon="mdi-star-outline"
                  size="small"
                  class="show-on-hover"
                  v-else
                  @click="addNewsBoardToFavorites"
                  title="Zu Favoriten hinzufügen"
                ></v-btn>
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
  VCol,
  VTabs,
  VTab
} from 'vuetify/components'
import { useRouter } from 'vue-router'
import { useFavoritesStore } from '../store/favorites'
import { useAuthStore } from '../store/auth'

// Initialize stores
const favoritesStore = useFavoritesStore()
const authStore = useAuthStore()

// UI state
const drawer = ref(true)
const searchQuery = ref('')
const activeTab = ref('dashboard')

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
  { title: 'Kontakte', icon: 'mdi-account-plus' },
  { title: 'Admin Settings', icon: 'mdi-cog-outline', route: '/settings' }
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

// Import router
const router = useRouter()

// Navigation function
const navigateTo = (tile) => {
  if (tile.route) {
    router.push(tile.route)
  }
}

// Navigate to a favorite item
const navigateToFavorite = (item) => {
  if (item.route) {
    router.push(item.route)
  }
}

// Favorites functionality for tiles
const isTileFavorite = (tile) => {
  const tileId = `module-${tile.title}`
  return favoritesStore.isFavorite(tileId)
}

const toggleTileFavorite = (tile) => {
  const favoriteItem = {
    id: `module-${tile.title}`,
    title: tile.title,
    icon: tile.icon,
    route: tile.route,
    type: 'module'
  }
  favoritesStore.toggleFavorite(favoriteItem)
}

// Favorites functionality for orders
const isOrderFavorite = (order) => {
  const orderId = `order-${order.id}`
  return favoritesStore.isFavorite(orderId)
}

const toggleOrderFavorite = (order) => {
  const favoriteItem = {
    id: `order-${order.id}`,
    title: `Auftrag: ${order.id} - ${order.customer}`,
    icon: 'mdi-file-document',
    type: 'order'
  }
  favoritesStore.toggleFavorite(favoriteItem)
}

// Favorites functionality for important links
const linkIsFavorites = computed(() => {
  return favoritesStore.isFavorite('important-links')
})

const addLinksToFavorites = () => {
  favoritesStore.addFavorite({
    id: 'important-links',
    title: 'Wichtige Links',
    icon: 'mdi-link',
    type: 'other'
  })
}

const removeLinksFromFavorites = () => {
  favoritesStore.removeFavorite('important-links')
}

// Favorites functionality for news board
const newsBoardIsFavorite = computed(() => {
  return favoritesStore.isFavorite('news-board')
})

const addNewsBoardToFavorites = () => {
  favoritesStore.addFavorite({
    id: 'news-board',
    title: 'Interne Pinnwand',
    icon: 'mdi-bulletin-board',
    type: 'other'
  })
}

const removeNewsBoardFromFavorites = () => {
  favoritesStore.removeFavorite('news-board')
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

.sidebar-toggle-btn {
  position: fixed;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  border-radius: 0 4px 4px 0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.favorite-toggle-btn {
  position: absolute;
  top: 5px;
  right: 5px;
}

.show-on-hover {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.v-hover:hover .show-on-hover,
tr:hover .show-on-hover,
.v-card:hover .show-on-hover {
  opacity: 1;
}

.favorite-remove-btn:hover {
  color: #f44336 !important;
}

.position-relative {
  position: relative !important;
}
</style>