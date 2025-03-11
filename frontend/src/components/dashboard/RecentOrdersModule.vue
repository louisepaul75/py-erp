<template>
  <v-card flat>
    <div class="d-flex align-center px-6 py-4 border-b">
      <span class="text-h6 font-weight-medium">{{ module.title }}</span>
      <v-spacer></v-spacer>

      <v-text-field
        v-model="searchQuery"
        prepend-inner-icon="mdi-magnify"
        placeholder="Suchen..."
        hide-details
        density="compact"
        variant="outlined"
        class="max-w-xs"
      ></v-text-field>

      <v-btn
        v-if="!editMode"
        :icon="isFavorite ? 'mdi-star' : 'mdi-star-outline'"
        :color="isFavorite ? 'warning' : 'grey-darken-1'"
        size="small"
        variant="text"
        class="ml-2 favorite-toggle-btn"
        :class="{ 'show-on-hover': !isFavorite }"
        @click="toggleFavorite"
      ></v-btn>
    </div>
    <v-table>
      <thead>
        <tr>
          <th class="text-caption font-weight-medium text-grey-darken-1">AUFTRAG</th>
          <th class="text-caption font-weight-medium text-grey-darken-1">KUNDE</th>
          <th class="text-caption font-weight-medium text-grey-darken-1">LIEFERTERMIN</th>
          <th class="text-caption font-weight-medium text-grey-darken-1">STATUS</th>
          <th class="text-caption font-weight-medium text-grey-darken-1">BETRAG</th>
          <th class="text-caption font-weight-medium text-grey-darken-1">FAVORIT</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in filteredOrders" :key="order.id" class="text-body-2">
          <td>{{ order.id }}</td>
          <td>{{ order.customer }}</td>
          <td>{{ order.deliveryDate }}</td>
          <td>
            <v-chip
              :color="getStatusColor(order.status)"
              size="small"
              class="font-weight-medium text-caption"
              variant="tonal"
            >
              {{ order.status }}
            </v-chip>
          </td>
          <td>{{ order.amount }}</td>
          <td>
            <v-btn
              :icon="isOrderFavorite(order) ? 'mdi-star' : 'mdi-star-outline'"
              :color="isOrderFavorite(order) ? 'warning' : 'grey'"
              size="small"
              variant="text"
              :class="{ 'show-on-hover': !isOrderFavorite(order) }"
              @click="toggleOrderFavorite(order)"
            ></v-btn>
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue';
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
const searchQuery = ref('');

// Sample data for recent orders
const recentOrders = [
  {
    id: 'A-1085',
    customer: 'Müller GmbH',
    deliveryDate: '15.03.2025',
    status: 'Offen',
    amount: '€2,450.00'
  },
  {
    id: 'A-1084',
    customer: 'Schmidt AG',
    deliveryDate: '18.03.2025',
    status: 'In Bearbeitung',
    amount: '€1,875.50'
  },
  {
    id: 'A-1083',
    customer: 'Weber KG',
    deliveryDate: '20.03.2025',
    status: 'Offen',
    amount: '€3,120.75'
  },
  {
    id: 'A-1082',
    customer: 'Becker GmbH',
    deliveryDate: '22.03.2025',
    status: 'Versandt',
    amount: '€950.25'
  },
  {
    id: 'A-1081',
    customer: 'Fischer & Co.',
    deliveryDate: '25.03.2025',
    status: 'Offen',
    amount: '€4,280.00'
  },
  {
    id: 'A-1080',
    customer: 'Hoffmann AG',
    deliveryDate: '28.03.2025',
    status: 'In Bearbeitung',
    amount: '€1,650.30'
  }
];

// Filtered orders based on search
const filteredOrders = computed(() => {
  if (!searchQuery.value) return recentOrders;
  const query = searchQuery.value.toLowerCase();
  return recentOrders.filter(
    (order) =>
      order.id.toLowerCase().includes(query) || order.customer.toLowerCase().includes(query)
  );
});

// Helper function for order status colors
const getStatusColor = (status) => {
  switch (status) {
    case 'Offen':
      return 'warning';
    case 'In Bearbeitung':
      return 'info';
    case 'Versandt':
      return 'success';
    default:
      return 'grey';
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

// Favorites functionality for orders
const isOrderFavorite = (order) => {
  const orderId = `order-${order.id}`;
  return favoritesStore.isFavorite(orderId);
};

const toggleOrderFavorite = (order) => {
  const favoriteItem = {
    id: `order-${order.id}`,
    title: `Auftrag: ${order.id} - ${order.customer}`,
    icon: 'mdi-file-document',
    type: 'order'
  };
  favoritesStore.toggleFavorite(favoriteItem);
};
</script>

<style scoped>
.max-w-xs {
  max-width: 240px;
}

.show-on-hover {
  opacity: 0;
  transition: opacity 0.2s ease;
}

tr:hover .show-on-hover {
  opacity: 1;
}
</style>
