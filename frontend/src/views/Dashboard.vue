<template>
  <div class="flex min-h-screen flex-col">
    <!-- Top Navigation Bar with Main Menu -->
    <header class="sticky top-0 z-30 flex h-16 items-center border-b bg-white px-4 md:px-6">
      <div class="flex items-center gap-2">
        <button @click="toggleSidebar" class="md:hidden h-9 w-9 rounded-md p-2 hover:bg-gray-100">
          <Menu class="h-5 w-5" />
          <span class="sr-only">Toggle sidebar</span>
        </button>
        <a href="/" class="flex items-center gap-2 font-semibold">
          <Package class="h-6 w-6" />
          <span>ERP System</span>
        </a>
      </div>
      
      <!-- Main Menu in Top Bar -->
      <div class="hidden md:flex items-center ml-8 space-x-1">
        <a href="#" class="px-3 py-2 rounded-md text-sm font-medium text-gray-900 bg-gray-100">Dashboard</a>
        <a href="#" class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">Produkte</a>
        <a href="#" class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">Bestellungen</a>
        <a href="#" class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">Kunden</a>
        <a href="#" class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100">Einstellungen</a>
      </div>
      
      <!-- Mobile Menu Dropdown -->
      <div class="relative md:hidden ml-2">
        <button 
          @click="isMenuOpen = !isMenuOpen" 
          class="flex items-center gap-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100"
        >
          Menü
          <ChevronDown class="h-4 w-4" />
        </button>
        <div 
          v-if="isMenuOpen" 
          class="absolute left-0 mt-2 w-48 rounded-md border border-gray-200 bg-white py-1 shadow-lg z-50"
        >
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100 bg-gray-100">Dashboard</a>
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Produkte</a>
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Bestellungen</a>
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Kunden</a>
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Einstellungen</a>
        </div>
      </div>
      
      <div class="flex-1"></div>
      
      <!-- Language Selection -->
      <div class="relative mr-2">
        <button 
          @click="isLanguageMenuOpen = !isLanguageMenuOpen" 
          class="flex items-center gap-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100"
        >
          <Globe class="h-4 w-4" />
          <span class="hidden sm:inline">Deutsch</span>
          <ChevronDown class="h-4 w-4" />
        </button>
        <div 
          v-if="isLanguageMenuOpen" 
          class="absolute right-0 mt-2 w-40 rounded-md border border-gray-200 bg-white py-1 shadow-lg z-50"
        >
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100 bg-gray-100">Deutsch</a>
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">English</a>
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Français</a>
          <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Español</a>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <button class="h-9 w-9 rounded-md p-2 hover:bg-gray-100">
          <Bell class="h-5 w-5" />
          <span class="sr-only">Benachrichtigungen</span>
        </button>
        <div class="relative">
          <button 
            @click="isUserMenuOpen = !isUserMenuOpen" 
            class="flex h-8 w-8 items-center justify-center rounded-full border"
          >
            <img
              src="https://via.placeholder.com/32"
              width="32"
              height="32"
              alt="Avatar"
              class="rounded-full"
            />
            <span class="sr-only">Benutzermenü</span>
          </button>
          <div 
            v-if="isUserMenuOpen" 
            class="absolute right-0 mt-2 w-48 rounded-md border border-gray-200 bg-white py-1 shadow-lg z-50"
          >
            <div class="px-4 py-2 text-sm font-medium">Max Mustermann</div>
            <div class="h-px bg-gray-200 my-1"></div>
            <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Profil</a>
            <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Einstellungen</a>
            <div class="h-px bg-gray-200 my-1"></div>
            <a href="#" class="block px-4 py-2 text-sm hover:bg-gray-100">Abmelden</a>
          </div>
        </div>
      </div>
    </header>

    <div class="flex flex-1">
      <!-- Sidebar with Favorites and Recent Items -->
      <aside 
        :class="[
          'fixed inset-y-0 left-0 z-20 flex w-64 flex-col border-r bg-gray-50 transition-transform duration-300 md:static',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
          isSidebarCollapsed && !isMobile ? 'md:w-16' : ''
        ]"
      >
        <div class="flex h-16 items-center border-b px-4">
          <div class="flex items-center gap-2">
            <Star class="h-5 w-5 text-yellow-500" />
            <span v-if="!isSidebarCollapsed || isMobile" class="font-semibold">Favoriten</span>
          </div>
          <button 
            v-if="!isMobile" 
            @click="isSidebarCollapsed = !isSidebarCollapsed" 
            class="ml-auto h-8 w-8 rounded-md p-1.5 hover:bg-gray-200"
          >
            <PanelLeft v-if="!isSidebarCollapsed" class="h-5 w-5" />
            <PanelRight v-else class="h-5 w-5" />
          </button>
        </div>
        
        <!-- Favorites Section -->
        <div class="p-4" v-if="!isSidebarCollapsed || isMobile">
          <h3 class="mb-2 text-xs font-semibold uppercase text-gray-500">Favoriten</h3>
          <div class="space-y-2">
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <Users class="h-4 w-4 text-blue-500" />
              <span>Kundenliste</span>
            </a>
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <ShoppingCart class="h-4 w-4 text-green-500" />
              <span>Neue Bestellung</span>
            </a>
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <BarChart class="h-4 w-4 text-purple-500" />
              <span>Umsatzstatistik</span>
            </a>
          </div>
        </div>
        <div v-else class="py-4">
          <div class="flex flex-col items-center space-y-4">
            <a href="#" class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-gray-200">
              <Users class="h-5 w-5 text-blue-500" />
            </a>
            <a href="#" class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-gray-200">
              <ShoppingCart class="h-5 w-5 text-green-500" />
            </a>
            <a href="#" class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-gray-200">
              <BarChart class="h-5 w-5 text-purple-500" />
            </a>
          </div>
        </div>
        
        <!-- Recent Items Section -->
        <div class="border-t p-4" v-if="!isSidebarCollapsed || isMobile">
          <h3 class="mb-2 text-xs font-semibold uppercase text-gray-500">Letzte Zugriffe</h3>
          <div class="space-y-2">
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <User class="h-4 w-4 text-gray-500" />
              <span>Kunde: Müller GmbH</span>
            </a>
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <FileText class="h-4 w-4 text-gray-500" />
              <span>Auftrag #1082</span>
            </a>
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <User class="h-4 w-4 text-gray-500" />
              <span>Kunde: Schmidt AG</span>
            </a>
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <FileText class="h-4 w-4 text-gray-500" />
              <span>Auftrag #1079</span>
            </a>
            <a href="#" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-700 hover:bg-gray-200">
              <User class="h-4 w-4 text-gray-500" />
              <span>Kunde: Weber KG</span>
            </a>
          </div>
        </div>
        <div v-else class="border-t py-4">
          <div class="flex flex-col items-center space-y-4">
            <a href="#" class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-gray-200">
              <User class="h-5 w-5 text-gray-500" />
            </a>
            <a href="#" class="flex h-8 w-8 items-center justify-center rounded-md hover:bg-gray-200">
              <FileText class="h-5 w-5 text-gray-500" />
            </a>
          </div>
        </div>
      </aside>

      <!-- Backdrop for mobile sidebar -->
      <div 
        v-if="isSidebarOpen && isMobile" 
        @click="isSidebarOpen = false" 
        class="fixed inset-0 z-10 bg-black/50 md:hidden"
      ></div>

      <!-- Main Content -->
      <main class="flex-1 overflow-auto p-4 md:p-6">
        <!-- Recent Orders by Delivery Date -->
        <div class="mb-8">
          <h2 class="text-lg font-semibold mb-4">Bestellungen nach Liefertermin</h2>
          <div class="rounded-lg border bg-white shadow-sm overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Auftrag</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kunde</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Liefertermin</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Betrag</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(order, index) in recentOrders" :key="index">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ order.id }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ order.customer }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ order.deliveryDate }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="[
                      'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                      order.status === 'Offen' ? 'bg-yellow-100 text-yellow-800' : 
                      order.status === 'In Bearbeitung' ? 'bg-blue-100 text-blue-800' : 
                      order.status === 'Versandt' ? 'bg-green-100 text-green-800' : 
                      'bg-gray-100 text-gray-800'
                    ]">
                      {{ order.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ order.amount }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Menu Tiles -->
        <div class="mb-8">
          <h2 class="text-lg font-semibold mb-4">Schnellzugriff</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <a v-for="(menuItem, index) in menuTiles" :key="index" href="#" 
              class="flex flex-col items-center justify-center p-4 rounded-lg border bg-white shadow-sm hover:bg-gray-50 transition-colors">
              <component :is="menuItem.icon" class="h-8 w-8 mb-2 text-gray-700" />
              <span class="text-sm font-medium text-center">{{ menuItem.title }}</span>
            </a>
          </div>
        </div>
        
        <!-- Link Collection -->
        <div class="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Links -->
          <div class="rounded-lg border bg-white p-4 shadow-sm">
            <h2 class="text-lg font-semibold mb-4">Wichtige Links</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <a v-for="(link, index) in importantLinks" :key="index" href="#" 
                class="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800">
                <Link2 class="h-4 w-4" />
                <span>{{ link }}</span>
              </a>
            </div>
          </div>
          
          <!-- News Pinboard -->
          <div class="rounded-lg border bg-white p-4 shadow-sm">
            <h2 class="text-lg font-semibold mb-4">Interne Pinnwand</h2>
            <div class="space-y-3">
              <div v-for="(news, index) in newsItems" :key="index" class="border-l-4 border-blue-500 pl-3 py-1">
                <p class="text-sm font-medium">{{ news.title }}</p>
                <p class="text-xs text-gray-500">{{ news.date }}</p>
                <p class="text-sm mt-1">{{ news.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  Menu, Bell, Package, Users, Star, User, FileText, 
  PanelLeft, PanelRight, ChevronDown, Globe, Link2,
  ShoppingCart, BarChart, Settings, Search, CreditCard,
  Calendar, FileSpreadsheet, Truck, Clipboard, Database,
  BarChart2, PieChart, UserPlus, Mail, Phone
} from 'lucide-vue-next'

// UI state
const isSidebarOpen = ref(false)
const isSidebarCollapsed = ref(false)
const isMobile = ref(false)
const isUserMenuOpen = ref(false)
const isMenuOpen = ref(false)
const isLanguageMenuOpen = ref(false)

// Toggle sidebar for mobile
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

// Check if we're on mobile
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    isSidebarCollapsed.value = false
  }
}

// Sample data for recent orders
const recentOrders = [
  { id: 'A-1085', customer: 'Müller GmbH', deliveryDate: '15.03.2025', status: 'Offen', amount: '€2,450.00' },
  { id: 'A-1084', customer: 'Schmidt AG', deliveryDate: '18.03.2025', status: 'In Bearbeitung', amount: '€1,875.50' },
  { id: 'A-1083', customer: 'Weber KG', deliveryDate: '20.03.2025', status: 'Offen', amount: '€3,120.75' },
  { id: 'A-1082', customer: 'Becker GmbH', deliveryDate: '22.03.2025', status: 'Versandt', amount: '€950.25' },
  { id: 'A-1081', customer: 'Fischer & Co.', deliveryDate: '25.03.2025', status: 'Offen', amount: '€4,280.00' },
  { id: 'A-1080', customer: 'Hoffmann AG', deliveryDate: '28.03.2025', status: 'In Bearbeitung', amount: '€1,650.30' },
]

// Menu tiles
const menuTiles = [
  { title: 'Kunden', icon: Users },
  { title: 'Bestellungen', icon: ShoppingCart },
  { title: 'Produkte', icon: Package },
  { title: 'Rechnungen', icon: CreditCard },
  { title: 'Kalender', icon: Calendar },
  { title: 'Berichte', icon: FileSpreadsheet },
  { title: 'Lieferungen', icon: Truck },
  { title: 'Aufgaben', icon: Clipboard },
  { title: 'Datenbank', icon: Database },
  { title: 'Statistiken', icon: BarChart2 },
  { title: 'Analysen', icon: PieChart },
  { title: 'Kontakte', icon: UserPlus },
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

// Watch for window resize
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  // Cleanup event listener
  return () => {
    window.removeEventListener('resize', checkMobile)
  }
})
</script>

<style>
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

body {
  @apply bg-gray-50;
}
</style>