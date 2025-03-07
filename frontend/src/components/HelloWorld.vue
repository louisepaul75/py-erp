<template>
  <v-card class="mx-auto my-5" max-width="600">
    <v-card-text class="pa-4">
      <h2 class="text-h4 text-primary mb-2">{{ title }}</h2>
      <p class="text-body-1 mb-4">{{ message }}</p>
      <v-btn color="primary" @click="incrementCount">
        Count: {{ count }}
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, defineProps, withDefaults } from 'vue';

// Define component props with TypeScript interface
interface Props {
  title?: string;
  message?: string;
}

// Set default values for props
const props = withDefaults(defineProps<Props>(), {
  title: 'Hello World',
  message: 'Welcome to the Vue.js 3.5 integration with pyERP!'
});

// Component state
const count = ref(0);

// Component methods
const incrementCount = () => {
  count.value++;
};
</script>

<style scoped>
.hello-world {
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin: 20px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

h2 {
  color: #d2bc9b;
  margin-top: 0;
}

.btn {
  background-color: #d2bc9b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #c0a989;
}
</style>
