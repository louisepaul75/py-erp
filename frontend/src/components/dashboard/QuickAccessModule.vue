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
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
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

const router = useRouter();
const favoritesStore = useFavoritesStore();

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
];

// Navigation function
const navigateTo = (tile) => {
  if (tile.route) {
    router.push(tile.route);
  }
};

// Favorites functionality
const isFavorite = computed(() => {
  return favoritesStore.isFavorite(props.module.id);
});

const toggleFavorite = () => {
  const favoriteItem = {
    id: props.module.id,
    title: props.module.title,
    icon: props.module.icon,
    type: 'module'
  };
  favoritesStore.toggleFavorite(favoriteItem);
};

// Favorites functionality for tiles
const isTileFavorite = (tile) => {
  const tileId = `tile-${tile.title}`;
  return favoritesStore.isFavorite(tileId);
};

const toggleTileFavorite = (tile) => {
  const favoriteItem = {
    id: `tile-${tile.title}`,
    title: tile.title,
    icon: tile.icon,
    route: tile.route,
    type: 'tile'
  };
  favoritesStore.toggleFavorite(favoriteItem);
};
</script>

<style scoped>
.favorite-toggle-btn {
  position: absolute;
  top: 5px;
  right: 5px;
}

.position-relative {
  position: relative !important;
}

.show-on-hover {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.v-hover:hover .show-on-hover,
.v-card:hover .show-on-hover {
  opacity: 1;
}
</style>
