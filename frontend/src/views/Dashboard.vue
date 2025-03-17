<template>
  <div class="dashboard">
    <!-- Navigation Drawer -->
    <v-navigation-drawer v-model="drawer" permanent class="bg-grey-lighten-4" :width="240">
      <!-- Global search -->
      <div class="px-4 py-4">
        <GlobalSearch placeholder="Search..." />
      </div>

      <!-- Favorites header -->
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
      variant="plain"
      size="small"
      color="primary"
      class="sidebar-toggle-btn"
      @click="toggleDrawer"
    ></v-btn>

    <!-- Main Content -->
    <v-main class="bg-grey-lighten-4">
      <v-container class="py-4">
        <!-- Dashboard Controls -->
        <v-card class="mb-6" flat>
          <div class="px-6 py-4 border-b d-flex align-center">
            <span class="text-h6 font-weight-medium">Dashboard</span>
            <v-spacer></v-spacer>

            <v-btn
              v-if="!editMode"
              prepend-icon="mdi-pencil"
              color="primary"
              variant="text"
              @click="enableEditMode"
            >
              Dashboard anpassen
            </v-btn>

            <template v-else>
              <v-btn
                color="success"
                variant="text"
                class="mr-2"
                prepend-icon="mdi-content-save"
                @click="saveDashboardConfig"
              >
                Speichern
              </v-btn>
              <v-btn color="error" variant="text" prepend-icon="mdi-close" @click="cancelEditMode">
                Abbrechen
              </v-btn>
            </template>
          </div>
        </v-card>

        <!-- Add Module Menu (only visible in edit mode) -->
        <v-card v-if="editMode" class="mb-6" flat>
          <div class="px-6 py-4 border-b">
            <span class="text-subtitle-1 font-weight-medium">Module hinzufügen</span>
          </div>
          <v-card-text>
            <v-row>
              <v-col
                v-for="module in availableModules"
                :key="module.id"
                cols="6"
                sm="4"
                md="3"
                lg="2"
              >
                <v-hover v-slot="{ isHovering, props }">
                  <v-card
                    v-bind="props"
                    :elevation="isHovering ? 2 : 0"
                    class="pa-4 text-center transition-all duration-200"
                    :class="{ 'bg-grey-lighten-4': isHovering }"
                    @click="addModule(module)"
                  >
                    <v-icon :icon="module.icon" size="24" class="mb-2 text-grey-darken-1"></v-icon>
                    <div class="text-body-2">{{ module.title }}</div>
                    <v-btn
                      icon="mdi-plus"
                      size="small"
                      color="primary"
                      variant="text"
                      class="add-module-btn position-absolute"
                      style="top: 8px; right: 8px"
                    ></v-btn>
                  </v-card>
                </v-hover>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Dashboard Modules -->
        <div v-if="loading" class="d-flex justify-center align-center my-6">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <template v-else>
          <!-- Grid Stack Container -->
          <div class="grid-stack">
            <!-- GridStack will automatically create grid-stack-item containers -->
            <template v-for="(module, index) in dashboardModules" :key="module.id">
              <div
                v-if="module.enabled"
                class="grid-stack-item"
                :gs-id="module.id"
                :gs-x="module.settings?.x || (index % 2) * 6"
                :gs-y="module.settings?.y || Math.floor(index / 2) * 4"
                :gs-w="module.settings?.w || 6"
                :gs-h="module.settings?.h || 4"
              >
                <div class="grid-stack-item-content">
                  <!-- Module Header -->
                  <div class="module-header d-flex align-center px-4 py-2 border-b">
                    <v-icon
                      :icon="getModuleIcon(module.type)"
                      size="small"
                      class="mr-2 text-grey-darken-1"
                    ></v-icon>
                    <span class="text-subtitle-2 font-weight-medium">{{ module.title }}</span>

                    <!-- Module Actions (only visible in edit mode) -->
                    <div v-if="editMode" class="module-actions d-flex align-center ml-auto">
                      <v-btn
                        icon="mdi-delete"
                        size="small"
                        color="error"
                        variant="text"
                        @click="removeModule(module)"
                      ></v-btn>
                    </div>
                  </div>

                  <!-- Module Content -->
                  <div class="pa-4">
                    <component
                      :is="getModuleComponent(module.type)"
                      :module="module"
                      :edit-mode="editMode"
                    ></component>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </template>
      </v-container>
    </v-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import draggable from 'vuedraggable';
import { GridStack } from 'gridstack';
import 'gridstack/dist/gridstack.min.css';
import api from '@/services/api';
import GlobalSearch from '@/components/GlobalSearch.vue';
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
  VTab,
  VProgressCircular
} from 'vuetify/components';
import { useRouter } from 'vue-router';
import { useFavoritesStore } from '@/store/favorites';
import { useAuthStore } from '@/store/auth';
import { useSearchStore } from '@/store/search';

// Import module components
import QuickAccessModule from '@/components/dashboard/QuickAccessModule.vue';
import RecentOrdersModule from '@/components/dashboard/RecentOrdersModule.vue';
import ImportantLinksModule from '@/components/dashboard/ImportantLinksModule.vue';
import NewsBoardModule from '@/components/dashboard/NewsBoardModule.vue';

// Initialize stores
const favoritesStore = useFavoritesStore();
const authStore = useAuthStore();
const searchStore = useSearchStore();
const router = useRouter();

// UI state
const drawer = ref(true);
const searchQuery = ref('');
const activeTab = ref('dashboard');
const loading = ref(true);
const editMode = ref(false);

// Dashboard state
const dashboardModules = ref([]);
const originalModules = ref([]);
const grid = ref(null);

// Toggle functions
const toggleDrawer = () => {
  drawer.value = !drawer.value;
};

// Dashboard edit mode functions
const enableEditMode = () => {
  originalModules.value = JSON.parse(JSON.stringify(dashboardModules.value));
  editMode.value = true;
};

const cancelEditMode = () => {
  dashboardModules.value = JSON.parse(JSON.stringify(originalModules.value));
  editMode.value = false;
};

const saveDashboardConfig = async () => {
  try {
    await api.patch('/dashboard/', {
      modules: dashboardModules.value
    });
    editMode.value = false;
    // Save successful notification would go here
  } catch (error) {
    console.error('Failed to save dashboard configuration:', error);
    // Error notification would go here
  }
};

// Module management functions
const addModule = (module) => {
  const existingModule = dashboardModules.value.find((m) => m.id === module.id);
  if (existingModule) {
    existingModule.enabled = true;
  } else {
    dashboardModules.value.push({
      ...module,
      position: dashboardModules.value.length,
      enabled: true
    });
  }
};

const removeModule = (module) => {
  const index = dashboardModules.value.findIndex((m) => m.id === module.id);
  if (index !== -1) {
    // Instead of removing, just disable it
    dashboardModules.value[index].enabled = false;
  }
};

// Component mapping
const getModuleComponent = (type) => {
  const moduleComponents = {
    'quick-access': QuickAccessModule,
    'recent-orders': RecentOrdersModule,
    'important-links': ImportantLinksModule,
    'news-board': NewsBoardModule
  };
  return moduleComponents[type] || null;
};

// Get module icon
const getModuleIcon = (type) => {
  const moduleIcons = {
    'quick-access': 'mdi-apps',
    'recent-orders': 'mdi-cart',
    'important-links': 'mdi-link',
    'news-board': 'mdi-bulletin-board'
  };
  return moduleIcons[type] || 'mdi-view-dashboard';
};

// Available modules definition
const availableModules = [
  {
    id: 'quick-access',
    title: 'Schnellzugriff',
    type: 'quick-access',
    icon: 'mdi-apps',
    settings: {}
  },
  {
    id: 'recent-orders',
    title: 'Bestellungen',
    type: 'recent-orders',
    icon: 'mdi-cart',
    settings: {}
  },
  {
    id: 'important-links',
    title: 'Wichtige Links',
    type: 'important-links',
    icon: 'mdi-link',
    settings: {}
  },
  {
    id: 'news-board',
    title: 'Interne Pinnwand',
    type: 'news-board',
    icon: 'mdi-bulletin-board',
    settings: {}
  }
];

// Initialize GridStack
onMounted(async () => {
  try {
    const response = await api.get('/dashboard/');
    if (response.data && response.data.dashboard_modules) {
      dashboardModules.value = response.data.dashboard_modules;
      // Sort modules by position
      dashboardModules.value.sort((a, b) => a.position - b.position);
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  } finally {
    loading.value = false;
    // Initialize GridStack after loading is complete and DOM is updated
    await nextTick();
    initializeGrid();
  }
});

// Watch edit mode changes to enable/disable grid functionality
watch(editMode, (newValue) => {
  if (grid.value) {
    if (newValue) {
      grid.value.enable();
    } else {
      grid.value.disable();
    }
  }
});

const initializeGrid = () => {
  // Verify grid container exists before initialization
  const gridElement = document.querySelector('.grid-stack');
  if (!gridElement) {
    console.error('Grid container not found. Retrying in 100ms...');
    setTimeout(initializeGrid, 100);
    return;
  }

  try {
    // Initialize GridStack with options
    grid.value = GridStack.init({
      column: 12,
      cellHeight: 'auto',
      animate: true,
      float: true,
      draggable: { handle: '.module-header' },
      resizable: {
        handles: 'e, se, s, sw, w'
      },
      disableDrag: !editMode.value,
      disableResize: !editMode.value
    });

    if (grid.value) {
      grid.value.on('change', saveGridLayout);
      console.log('GridStack initialized successfully');
    } else {
      console.error('Grid initialization returned null');
    }
  } catch (error) {
    console.error('Failed to initialize GridStack:', error);
  }
};

const saveGridLayout = () => {
  if (!grid.value) return;

  const layout = grid.value.save();
  const updatedModules = dashboardModules.value.map((module) => {
    const gridItem = layout.find((item) => item.id === module.id);
    if (gridItem) {
      return {
        ...module,
        settings: {
          ...module.settings,
          x: gridItem.x,
          y: gridItem.y,
          w: gridItem.w,
          h: gridItem.h
        }
      };
    }
    return module;
  });

  dashboardModules.value = updatedModules;
};

// Recent access items
const recentAccess = [
  { title: 'Kunde: Müller GmbH', icon: 'mdi-account' },
  { title: 'Auftrag #1082', icon: 'mdi-file-document' },
  { title: 'Kunde: Schmidt AG', icon: 'mdi-account' },
  { title: 'Auftrag #1079', icon: 'mdi-file-document' },
  { title: 'Kunde: Weber KG', icon: 'mdi-account' }
];

// Navigation functions
const navigateTo = (tile) => {
  if (tile.route) {
    router.push(tile.route);
  }
};

// Navigate to a favorite item
const navigateToFavorite = (item) => {
  if (item.route) {
    router.push(item.route);
  }
};
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

.dashboard-modules-container {
  min-height: 200px;
}

.cursor-move {
  cursor: move;
}

.show-on-hover {
  opacity: 0;
  transition: opacity 0.2s;
}

*:hover > .show-on-hover {
  opacity: 1;
}

.add-module-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.sidebar-toggle-btn {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 100;
}

/* GridStack Styles */
.grid-stack {
  background: transparent;
}

.grid-stack-item {
  min-width: 300px !important;
}

.grid-stack-item-content {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  inset: 4px !important;
}

.module-header {
  background-color: #f8f9fa;
  cursor: move;
}

.grid-stack-placeholder {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  border: 1px dashed #ccc;
}

.grid-stack-item.ui-draggable-dragging {
  z-index: 100;
}

.grid-stack-item.ui-resizable-resizing {
  z-index: 100;
}

/* Edit mode styles */
.grid-stack.grid-stack-animate .grid-stack-item.ui-draggable-dragging,
.grid-stack.grid-stack-animate .grid-stack-item.ui-resizable-resizing,
.grid-stack.grid-stack-animate .grid-stack-item.grid-stack-placeholder {
  transition: none;
}
</style>
