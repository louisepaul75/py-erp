<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <!-- Tab navigation -->
        <v-tabs v-model="activeTab" color="primary" class="mb-6">
          <v-tab value="orders">
            <v-icon start>mdi-cart</v-icon>
            Sales Orders
          </v-tab>
          <v-tab value="customers">
            <v-icon start>mdi-account-group</v-icon>
            Customers
          </v-tab>
        </v-tabs>

        <!-- Tab content -->
        <v-window v-model="activeTab">
          <v-window-item value="orders">
            <SalesOrderList />
          </v-window-item>
          <v-window-item value="customers">
            <CustomerList />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SalesOrderList from './SalesOrderList.vue';
import CustomerList from './CustomerList.vue';

const activeTab = ref('orders');
</script> 