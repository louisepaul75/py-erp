import { defineStore } from 'pinia';
import searchService, { SearchResponse } from '@/services/search';

interface SearchState {
  searchQuery: string;
  recentSearches: string[];
  searchResponse: SearchResponse | null;
  loading: boolean;
  error: string | null;
}

export const useSearchStore = defineStore('search', {
  state: (): SearchState => ({
    searchQuery: '',
    recentSearches: [],
    searchResponse: null,
    loading: false,
    error: null
  }),

  actions: {
    async performSearch(query: string) {
      if (!query || query.length < 2) {
        this.searchResponse = null;
        this.loading = false;
        return;
      }

      this.searchQuery = query;
      this.loading = true;
      this.error = null;

      try {
        this.searchResponse = await searchService.globalSearch(query);

        // Add to recent searches
        if (!this.recentSearches.includes(query)) {
          this.recentSearches.unshift(query);
          // Keep only the last 10 searches
          if (this.recentSearches.length > 10) {
            this.recentSearches.pop();
          }
        }
      } catch (error) {
        this.error = 'Failed to perform search';
        console.error('Search failed:', error);
      } finally {
        this.loading = false;
      }
    },

    clearSearch() {
      this.searchQuery = '';
      this.searchResponse = null;
    },

    clearRecentSearches() {
      this.recentSearches = [];
    },

    clearError() {
      this.error = null;
    }
  },

  getters: {
    hasResults: (state) => {
      if (!state.searchResponse) return false;

      // Check if any category has results
      return Object.values(state.searchResponse.results).some(results => results.length > 0);
    },

    totalResultsCount: (state) => {
      if (!state.searchResponse) return 0;
      return state.searchResponse.total_count;
    },

    resultsByCategoryCount: (state) => {
      if (!state.searchResponse) return {};
      return state.searchResponse.counts;
    }
  }
});
