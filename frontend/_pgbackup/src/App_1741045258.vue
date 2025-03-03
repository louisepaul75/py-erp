<template>
  <div class="vue-app-container">
    <header>
      <h1>pyERP</h1>
      <nav>
        <router-link to="/">Home</router-link> |
        <router-link to="/products">Products</router-link> |
        <router-link to="/products/categories">Categories</router-link> |
        <router-link to="/sales">Sales</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
    <footer>
      <p>© {{ currentYear }} pyERP</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

// Compute the current year for the footer
const currentYear = computed(() => new Date().getFullYear());
</script>

<style scoped>
.vue-app-container {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

header {
  padding: 20px 0;
  border-bottom: 1px solid #eaeaea;
}

h1 {
  color: #d2bc9b;
  margin-bottom: 15px;
}

nav {
  padding: 10px 0;
}

nav a {
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
  font-weight: bold;
}

nav a.router-link-active {
  color: #d2bc9b;
}

main {
  padding: 20px 0;
  min-height: 70vh;
}

footer {
  margin-top: 40px;
  padding: 20px 0;
  font-size: 0.8em;
  color: #666;
  border-top: 1px solid #eaeaea;
  text-align: center;
}
</style> 