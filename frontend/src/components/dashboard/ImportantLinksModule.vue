<template>
  <v-card flat>
    <div class="px-6 py-4 border-b d-flex align-center">
      <span class="text-h6 font-weight-medium">{{ module.title }}</span>
      <v-spacer></v-spacer>

      <v-tooltip v-if="editMode && isAdmin" text="Hier können Sie die wichtigen Links bearbeiten">
        <template v-slot:activator="{ props }">
          <v-icon
            v-bind="props"
            icon="mdi-information-outline"
            class="mr-2"
            size="small"
            color="info"
          ></v-icon>
        </template>
      </v-tooltip>

      <v-btn
        v-if="!editMode"
        :icon="isFavorite ? 'mdi-star' : 'mdi-star-outline'"
        :color="isFavorite ? 'warning' : 'grey-darken-1'"
        size="small"
        variant="text"
        class="favorite-toggle-btn"
        :class="{ 'show-on-hover': !isFavorite }"
        @click="toggleFavorite"
      ></v-btn>
    </div>
    <v-list class="pa-2">
      <!-- Display links in normal mode -->
      <template v-if="!editMode || !isAdmin">
        <v-list-item
          v-for="link in importantLinks"
          :key="link.id"
          :title="link.text"
          prepend-icon="mdi-link"
          class="rounded text-body-2"
          density="comfortable"
          :href="link.url"
          target="_blank"
          link
        ></v-list-item>
      </template>

      <!-- Edit mode for admin -->
      <template v-else>
        <v-list-item
          v-for="(link, index) in importantLinks"
          :key="link.id"
          class="rounded mb-2 pa-2 links-edit-item"
        >
          <div class="d-flex align-center w-100">
            <v-text-field
              v-model="link.text"
              density="compact"
              hide-details
              placeholder="Link text"
              class="mr-2"
              :rules="[(v) => !!v || 'Text ist erforderlich']"
            ></v-text-field>
            <v-text-field
              v-model="link.url"
              density="compact"
              hide-details
              placeholder="URL (z.B. https://example.com)"
              class="mr-2"
              :rules="[
                (v) => !!v || 'URL ist erforderlich',
                (v) => isValidUrl(v) || 'Ungültige URL (muss mit http:// oder https:// beginnen)'
              ]"
            ></v-text-field>
            <v-tooltip text="Link entfernen">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-delete"
                  color="error"
                  size="small"
                  variant="text"
                  @click="removeLink(index)"
                ></v-btn>
              </template>
            </v-tooltip>
          </div>
        </v-list-item>

        <!-- Add new link button -->
        <v-btn
          block
          color="primary"
          variant="text"
          prepend-icon="mdi-plus"
          @click="addNewLink"
          class="mt-3"
        >
          Link hinzufügen
        </v-btn>
      </template>
    </v-list>
  </v-card>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useFavoritesStore } from '../../store/favorites';
import { useAuthStore } from '../../store/auth';
import api from '../../services/api';

const props = defineProps({
  module: {
    type: Object,
    required: true
  },
  editMode: {
    type: Boolean,
    default: false
  }
});

const authStore = useAuthStore();
const favoritesStore = useFavoritesStore();

// Check if user is admin
const isAdmin = computed(() => authStore.isAdmin);

// Convert the static array to a ref with structured data
const importantLinks = ref([]);

// Initialize the links data
onMounted(() => {
  // Use module settings if available, otherwise use defaults
  if (props.module.settings && props.module.settings.links) {
    importantLinks.value = [...props.module.settings.links];
  } else {
    // Default links
    importantLinks.value = [
      { id: 1, text: 'Unternehmenshandbuch', url: 'https://docs.company.de/handbook' },
      { id: 2, text: 'Intranet', url: 'https://intranet.company.de' },
      { id: 3, text: 'Supportportal', url: 'https://support.company.de' },
      { id: 4, text: 'Schulungsvideos', url: 'https://training.company.de/videos' },
      { id: 5, text: 'Produktkatalog', url: 'https://catalog.company.de' },
      { id: 6, text: 'Preisliste 2025', url: 'https://docs.company.de/prices2025' },
      { id: 7, text: 'Urlaubsplaner', url: 'https://vacation.company.de' },
      { id: 8, text: 'IT-Helpdesk', url: 'https://helpdesk.company.de' },
      { id: 9, text: 'Qualitätsmanagement', url: 'https://quality.company.de' },
      { id: 10, text: 'Mitarbeiterportal', url: 'https://staff.company.de' }
    ];
  }
});

// Validate URLs
const isValidUrl = (url) => {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch (e) {
    return false;
  }
};

// Save links to module settings when they change in edit mode
watch(
  importantLinks,
  (newLinks) => {
    if (props.editMode && isAdmin.value) {
      // Update the module settings
      if (!props.module.settings) {
        props.module.settings = {};
      }
      props.module.settings.links = [...newLinks];
    }
  },
  { deep: true }
);

// Link management functions
const addNewLink = () => {
  const newId =
    importantLinks.value.length > 0
      ? Math.max(...importantLinks.value.map((link) => link.id)) + 1
      : 1;

  importantLinks.value.push({
    id: newId,
    text: 'Neuer Link',
    url: 'https://'
  });
};

const removeLink = (index) => {
  importantLinks.value.splice(index, 1);
};

// Favorites functionality
const isFavorite = computed(() => {
  return favoritesStore.isFavorite(props.module.id);
});

const toggleFavorite = () => {
  const favoriteItem = {
    id: props.module.id,
    title: props.module.title,
    icon: 'mdi-link',
    type: 'module'
  };
  favoritesStore.toggleFavorite(favoriteItem);
};
</script>

<style scoped>
.show-on-hover {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.v-card:hover .show-on-hover {
  opacity: 1;
}

.links-edit-item {
  border: 1px dashed #e0e0e0;
}

.links-edit-item:hover {
  background-color: #f5f5f5;
}
</style>
