<template>
  <div class="app-data-table" :class="sizeClass">
    <div v-if="showToolbar" class="table-toolbar mb-2">
      <v-text-field
        v-if="searchable"
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
        density="compact"
        class="table-search"
      ></v-text-field>
      
      <v-spacer></v-spacer>
      
      <slot name="toolbar-actions"></slot>
    </div>
    
    <v-data-table
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="filteredItems"
      :search="search"
      :loading="loading"
      :item-value="itemValue"
      :show-select="showSelect"
      :density="density"
      :hover="hover"
      :class="tableClass"
      @update:options="$emit('update:options', $event)"
    >
      <template v-for="(_, name) in $slots" #[name]="slotData">
        <slot :name="name" v-bind="slotData"></slot>
      </template>
    </v-data-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const props = defineProps({
  headers: {
    type: Array,
    required: true
  },
  items: {
    type: Array,
    required: true
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
  filters: {
    type: Object,
    default: () => ({})
  },
  tableClass: {
    type: String,
    default: 'elevation-1'
  }
});

const emit = defineEmits(['update:options']);

const search = ref('');
const itemsPerPage = ref(10);

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

// Compute size class
const sizeClass = computed(() => {
  return `table-size-${props.size}`;
});

// Filter items based on filters prop
const filteredItems = computed(() => {
  let result = [...props.items];
  
  // Apply filters
  Object.entries(props.filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      result = result.filter(item => {
        if (typeof value === 'function') {
          return value(item[key]);
        } else {
          return String(item[key]).toLowerCase().includes(String(value).toLowerCase());
        }
      });
    }
  });
  
  return result;
});
</script>

<style scoped>
.app-data-table {
  width: 100%;
}

.table-toolbar {
  display: flex;
  align-items: center;
}

.table-search {
  max-width: 300px;
}

.table-size-small :deep(th),
.table-size-small :deep(td) {
  padding: 0 8px !important;
  font-size: 0.875rem;
}

.table-size-large :deep(th),
.table-size-large :deep(td) {
  padding: 0 16px !important;
  font-size: 1.05rem;
}
</style> 