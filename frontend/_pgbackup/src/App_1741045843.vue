<template>
    <div class="vue-app-container">
        <header>
            <nav>
                <router-link to="/">
                    <img src="@/assets/wsz_logo_long.png" alt="Wilhelm-Schweizer Logo" class="nav-logo">
                    Home
                </router-link>                 |
                <router-link to="/products">Products</router-link>                 |
                <router-link to="/products/categories">Categories</router-link>                 |
                <router-link to="/sales">Sales</router-link>
            </nav>
        </header>
        <main>
            <router-view/>
        </main>
        <footer>
            <p>&copy; {{ currentYear }} Wilhelm-Schweizer |</p>
            <p> pyERP</p>
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

nav {
  padding: 10px 0;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

nav a {
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
  font-weight: bold;
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
}

.nav-logo {
  height: 2.7em;
  margin-right: 5px;
  vertical-align: middle;
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
