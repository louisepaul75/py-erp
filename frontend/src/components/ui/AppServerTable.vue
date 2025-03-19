<template>
  <div class="app-server-table">
    <div class="server-table-toolbar mb-2" v-if="showToolbar">
      <v-text-field
        v-if="searchable"
        v-model="searchQuery"
        prepend-inner-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
        density="compact"
        class="server-table-search"
        @update:model-value="onSearchDebounced"
      ></v-text-field>
      
      <v-spacer></v-spacer>
      
      <div class="d-flex align-center">
        <v-progress-circular
          v-if="loading"
          indeterminate
          color="primary"
          size="24"
          class="mr-2"
        ></v-progress-circular>
        
        <slot name="toolbar-actions"></slot>
      </div>
    </div>
    
    <v-data-table
      v-model:items-per-page="options.itemsPerPage"
      v-model:page="options.page"
      v-model:sort-by="options.sortBy"
      :headers="headers"
      :items="items"
      :items-length="totalItems"
      :loading="loading"
      :item-value="itemValue"
      :show-select="showSelect"
      :density="density"
      :hover="hover"
      :class="tableClass"
      :items-per-page-options="itemsPerPageOptions"
      @update:options="handleOptionsUpdate"
    >
      <template v-for="(_, name) in $slots" #[name]="slotData">
        <slot :name="name" v-bind="slotData"></slot>
      </template>
    </v-data-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import debounce from 'lodash/debounce';

const props = defineProps({
  headers: {
    type: Array,
    required: true
  },
  items: {
    type: Array,
    required: true
  },
  totalItems: {
    type: Number,
    default: 0
  },
  itemValue: {
    type: String,
    default: 'id'
  },
  size: {
    type: String,
    default: 'default',
    validator: (value: string) => ['small', 'default', 'large'].includes(value)
  },
  searchable: {
    type: Boolean,
    default: true
  },
  showSelect: {
    type: Boolean,
    default: false
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  hover: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  tableClass: {
    type: String,
    default: 'elevation-1'
  },
  itemsPerPageOptions: {
    type: Array,
    default: () => [5, 10, 15, 20, 25, 50, 100]
  },
  initialOptions: {
    type: Object,
    default: () => ({
      page: 1,
      itemsPerPage: 10,
      sortBy: []
    })
  }
});

const emit = defineEmits(['update:options', 'search']);

const searchQuery = ref('');
const options = ref({
  page: props.initialOptions.page || 1,
  itemsPerPage: props.initialOptions.itemsPerPage || 10,
  sortBy: props.initialOptions.sortBy || []
});

// Compute density based on size
const density = computed(() => {
  switch (props.size) {
    case 'small':
      return 'compact';
    case 'large':
      return 'default';
    default:
      return 'comfortable';
  }
});

// Create debounced search function
const onSearchDebounced = debounce(() => {
  emit('search', searchQuery.value);
}, 300);

// Handle options update
function handleOptionsUpdate(newOptions) {
  options.value = {
    page: newOptions.page,
    itemsPerPage: newOptions.itemsPerPage,
    sortBy: newOptions.sortBy
  };
  
  emit('update:options', options.value);
}

// Initialize with default options
onMounted(() => {
  emit('update:options', options.value);
});
</script>

<style scoped>
.app-server-table {
  width: 100%;
}

.server-table-toolbar {
  display: flex;
  align-items: center;
}

.server-table-search {
  max-width: 300px;
}
</style> 