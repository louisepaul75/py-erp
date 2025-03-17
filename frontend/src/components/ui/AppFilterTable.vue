<template>
  <div class="app-filter-table">
    <div class="filter-section mb-4" v-if="showFilters">
      <v-card variant="outlined" class="pa-3">
        <div class="d-flex align-center mb-2">
          <h3 class="text-subtitle-1 font-weight-bold">Filters</h3>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            density="compact"
            color="primary"
            @click="resetFilters"
            prepend-icon="mdi-refresh"
          >
            Reset
          </v-btn>
        </div>
        
        <v-row dense>
          <v-col v-for="(filter, key) in availableFilters" :key="key" cols="12" sm="6" md="4" lg="3">
            <component
              :is="getFilterComponent(filter.type)"
              v-model="activeFilters[key]"
              :label="filter.label"
              :items="filter.options || []"
              :clearable="true"
              density="compact"
              hide-details
              class="filter-input"
            ></component>
          </v-col>
        </v-row>
      </v-card>
    </div>
    
    <app-data-table
      :headers="headers"
      :items="items"
      :filters="activeFilters"
      :size="size"
      :searchable="searchable"
      :show-select="showSelect"
      :loading="loading"
      :item-value="itemValue"
      :hover="hover"
      :table-class="tableClass"
      @update:options="$emit('update:options', $event)"
    >
      <template v-for="(_, name) in $slots" #[name]="slotData">
        <slot :name="name" v-bind="slotData"></slot>
      </template>
      
      <template #toolbar-actions>
        <v-btn
          v-if="showFilters"
          icon
          variant="text"
          color="primary"
          @click="filtersExpanded = !filtersExpanded"
        >
          <v-icon>{{ filtersExpanded ? 'mdi-filter-off' : 'mdi-filter' }}</v-icon>
        </v-btn>
        <slot name="additional-actions"></slot>
      </template>
    </app-data-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import AppDataTable from './AppDataTable.vue';

const props = defineProps({
  headers: {
    type: Array,
    required: true
  },
  items: {
    type: Array,
    required: true
  },
  filters: {
    type: Object,
    default: () => ({})
  },
  size: {
    type: String,
    default: 'default'
  },
  searchable: {
    type: Boolean,
    default: true
  },
  showSelect: {
    type: Boolean,
    default: false
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  itemValue: {
    type: String,
    default: 'id'
  },
  hover: {
    type: Boolean,
    default: true
  },
  tableClass: {
    type: String,
    default: 'elevation-1'
  }
});

const emit = defineEmits(['update:options', 'filter-change']);

const filtersExpanded = ref(false);
const activeFilters = ref({...props.filters});

// Computed property to determine if filters should be shown
const showFilters = computed(() => {
  return props.showFilters && filtersExpanded.value;
});

// Available filters based on headers
const availableFilters = computed(() => {
  const filters = {};
  
  props.headers.forEach(header => {
    if (header.filterable !== false) {
      filters[header.key] = {
        label: header.title,
        type: header.filterType || 'text',
        options: header.filterOptions || []
      };
    }
  });
  
  return filters;
});

// Get the appropriate component based on filter type
function getFilterComponent(type) {
  switch (type) {
    case 'select':
      return 'v-select';
    case 'date':
      return 'v-text-field';
    case 'boolean':
      return 'v-checkbox';
    default:
      return 'v-text-field';
  }
}

// Reset all filters
function resetFilters() {
  activeFilters.value = {};
  emit('filter-change', {});
}
</script>

<style scoped>
.app-filter-table {
  width: 100%;
}

.filter-section {
  transition: all 0.3s ease;
}

.filter-input {
  width: 100%;
}
</style> 