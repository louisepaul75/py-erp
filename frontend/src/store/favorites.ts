import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useAuthStore } from './auth';

export interface FavoriteItem {
  id: string;
  title: string;
  icon: string;
  route?: string;
  type: 'module' | 'customer' | 'order' | 'report' | 'other';
}

export const useFavoritesStore = defineStore('favorites', () => {
  const authStore = useAuthStore();
  const favorites = ref<FavoriteItem[]>([]);
  
  // Load favorites from localStorage based on user ID
  function loadFavorites() {
    if (!authStore.user) {
      favorites.value = [];
      return;
    }
    
    const userId = authStore.user.id || authStore.user.username || 'anonymous';
    const storageKey = `favorites_${userId}`;
    const storedFavorites = localStorage.getItem(storageKey);
    
    favorites.value = storedFavorites ? JSON.parse(storedFavorites) : [];
  }

  // Save favorites to localStorage with user-specific key
  function saveFavorites() {
    if (!authStore.user) return;
    
    const userId = authStore.user.id || authStore.user.username || 'anonymous';
    const storageKey = `favorites_${userId}`;
    localStorage.setItem(storageKey, JSON.stringify(favorites.value));
  }

  // Add an item to favorites
  function addFavorite(item: FavoriteItem) {
    // Check if item already exists in favorites
    if (!favorites.value.some(fav => fav.id === item.id)) {
      favorites.value.push(item);
      saveFavorites();
    }
  }

  // Remove an item from favorites
  function removeFavorite(id: string) {
    const index = favorites.value.findIndex(item => item.id === id);
    if (index !== -1) {
      favorites.value.splice(index, 1);
      saveFavorites();
    }
  }

  // Check if an item is in favorites
  function isFavorite(id: string): boolean {
    return favorites.value.some(item => item.id === id);
  }

  // Toggle favorite status
  function toggleFavorite(item: FavoriteItem) {
    if (isFavorite(item.id)) {
      removeFavorite(item.id);
    } else {
      addFavorite(item);
    }
  }

  // Initialize favorites when store is created
  loadFavorites();

  // Watch for auth changes to reload favorites
  watch(() => authStore.user, () => {
    loadFavorites();
  });

  return {
    favorites,
    addFavorite,
    removeFavorite,
    isFavorite,
    toggleFavorite
  };
}); 