<template>
  <div class="global-search">
    <v-autocomplete
      v-model="selected"
      :loading="loading"
      :items="searchResults"
      :search-input.sync="searchQuery"
      :menu-props="{ maxHeight: 500 }"
      :placeholder="t('search.placeholder')"
      :hide-selected="true"
      :no-filter="true"
      item-title="primaryText"
      item-value="id"
      return-object
      variant="solo"
      density="comfortable"
      hide-details
      clearable
      rounded
      class="global-search-input"
      @update:search="onSearchUpdate"
      @update:model-value="onSelect"
    >
      <template v-slot:prepend-inner>
        <v-icon icon="mdi-magnify" color="grey-darken-1"></v-icon>
      </template>

      <template v-slot:no-data>
        <v-list-item v-if="loading">
          <v-list-item-title>
            <v-progress-circular indeterminate size="16" class="mr-2"></v-progress-circular>
            {{ t('search.searching') }}
          </v-list-item-title>
        </v-list-item>
        <v-list-item v-else-if="searchQuery && searchQuery.length > 0">
          <v-list-item-title>
            {{ t('search.noResults', { query: searchQuery }) }}
          </v-list-item-title>
        </v-list-item>
        <v-list-item v-else>
          <v-list-item-title>
            {{ t('search.startTyping') }}
          </v-list-item-title>
        </v-list-item>
      </template>

      <!-- Group results by category -->
      <template v-slot:item="{ item, props }">
        <v-list-item
          v-bind="props"
          :title="item.raw.primaryText"
          :subtitle="item.raw.secondaryText"
          :prepend-icon="item.raw.icon"
          class="search-result-item"
        >
          <template v-slot:append>
            <v-chip size="small" color="grey" text-color="white" class="result-type-chip">
              {{ item.raw.categoryLabel }}
            </v-chip>
          </template>
        </v-list-item>
      </template>
    </v-autocomplete>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import searchService, { SearchResult, SearchResponse } from '@/services/search';
import { useI18n } from 'vue-i18n';
import { useSearchStore } from '@/store/search';

// Props
const props = defineProps({
  placeholder: {
    type: String,
    default: 'Search...'
  },
  width: {
    type: [String, Number],
    default: '100%'
  }
});

// Dependencies
const router = useRouter();
const { t } = useI18n();
const searchStore = useSearchStore();

// State
const searchQuery = ref('');
const selected = ref(null);
const debounceTimeout = ref<number | null>(null);

// Use values from the store
const loading = computed(() => searchStore.loading);
const searchResponse = computed(() => searchStore.searchResponse);

// Format search results for the autocomplete component
const searchResults = computed(() => {
  if (!searchResponse.value) return [];

  const results: any[] = [];
  
  // Process each category of results
  Object.entries(searchResponse.value.results).forEach(([category, items]) => {
    if (items.length === 0) return;
    
    const categoryLabel = t(`search.categories.${category}`);
    
    // Add each result with formatted display text
    items.forEach(item => {
      results.push({
        id: `${item.type}-${item.id}`,
        primaryText: searchService.getPrimaryText(item),
        secondaryText: searchService.getSecondaryText(item),
        icon: searchService.getIconForResult(item),
        categoryLabel,
        original: item
      });
    });
  });
  
  return results;
});

// Methods
const onSearchUpdate = (val: string) => {
  searchQuery.value = val;
  
  // Debounce search to avoid too many requests
  if (debounceTimeout.value) {
    clearTimeout(debounceTimeout.value);
  }
  
  if (val && val.length >= 2) {
    debounceTimeout.value = setTimeout(() => {
      searchStore.performSearch(val);
    }, 300) as unknown as number;
  } else {
    searchStore.clearSearch();
  }
};

const onSelect = (item: any) => {
  if (!item) return;
  
  const result = item.original;
  const route = searchService.getRouteForResult(result);
  
  // Navigate to the appropriate route
  router.push(route);
  
  // Reset the search
  searchQuery.value = '';
  selected.value = null;
  searchStore.clearSearch();
};

// Watch for changes to search query
watch(searchQuery, (newVal) => {
  if (!newVal || newVal.length < 2) {
    searchStore.clearSearch();
  }
});
</script>

<style scoped>
.global-search {
  position: relative;
  width: v-bind(width);
  max-width: 100%;
}

.global-search-input {
  border-radius: 4px;
}

.search-result-item {
  margin-bottom: 4px;
}

.result-type-chip {
  font-size: 0.7rem;
  height: 20px;
}

:deep(.v-field__input) {
  padding: 8px 16px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}
</style> 