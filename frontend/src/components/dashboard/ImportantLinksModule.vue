<template>
  <v-card flat>
    <div class="px-6 py-4 border-b d-flex align-center">
      <span class="text-h6 font-weight-medium">{{ module.title }}</span>
      <v-spacer></v-spacer>
      
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
</template>

<script setup>
import { computed } from 'vue'
import { useFavoritesStore } from '../../store/favorites'

const props = defineProps({
  module: {
    type: Object,
    required: true
  },
  editMode: {
    type: Boolean,
    default: false
  }
})

const favoritesStore = useFavoritesStore()

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

// Favorites functionality
const isFavorite = computed(() => {
  return favoritesStore.isFavorite(props.module.id)
})

const toggleFavorite = () => {
  const favoriteItem = {
    id: props.module.id,
    title: props.module.title,
    icon: 'mdi-link',
    type: 'module'
  }
  favoritesStore.toggleFavorite(favoriteItem)
}
</script>

<style scoped>
.show-on-hover {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.v-card:hover .show-on-hover {
  opacity: 1;
}
</style> 