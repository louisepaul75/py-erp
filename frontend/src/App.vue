<template>
  <div class="vue-app-container">
    <header>
      <h1>Vue.js 3.5 Integration with pyERP</h1>
    </header>
    <main>
      <p>Vue.js is successfully integrated with the Django application!</p>
      <HelloWorld />
    </main>
    <footer>
      <p>© {{ currentYear }} pyERP</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import HelloWorld from './components/HelloWorld.vue';

// Compute the current year for the footer
const currentYear = computed(() => new Date().getFullYear());

// Component state
const message = ref('Hello from Vue.js 3.5!');
</script>

<style scoped>
.vue-app-container {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1 {
  color: #d2bc9b;
}

footer {
  margin-top: 40px;
  font-size: 0.8em;
  color: #666;
}
</style> 