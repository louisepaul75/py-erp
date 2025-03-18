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
</template>

<script setup>
import { computed } from 'vue';
import { useFavoritesStore } from '../../store/favorites';

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

const favoritesStore = useFavoritesStore();

// News items
const newsItems = [
  {
    title: 'Neue Produktlinie ab April',
    date: '09.03.2025',
    content:
      'Ab April führen wir eine neue Produktlinie ein. Schulungen finden nächste Woche statt.'
  },
  {
    title: 'Systemwartung am Wochenende',
    date: '08.03.2025',
    content:
      'Das System wird am Samstag von 22:00 bis 02:00 Uhr für Wartungsarbeiten nicht verfügbar sein.'
  },
  {
    title: 'Neue Vertriebspartnerschaft',
    date: '05.03.2025',
    content: 'Wir freuen uns, eine neue Partnerschaft mit der Firma XYZ bekannt zu geben.'
  }
];

// Favorites functionality
const isFavorite = computed(() => {
  return favoritesStore.isFavorite(props.module.id);
});

const toggleFavorite = () => {
  const favoriteItem = {
    id: props.module.id,
    title: props.module.title,
    icon: 'mdi-bulletin-board',
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

.border-b {
  border-bottom: 1px solid #e5e7eb !important;
}

.border-b:last-child {
  border-bottom: none !important;
}
</style>
