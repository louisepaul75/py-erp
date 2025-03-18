<template>
  <div class="home">
    <h1>Welcome to pyERP</h1>
    <p>A comprehensive ERP system for managing your business operations.</p>
    <div class="modules">
      <div class="module-card" @click="navigateTo('/products')">
        <h3>Products</h3>
        <p>Manage your product catalog, variants, and categories</p>
      </div>
      <!-- Add more module cards as needed -->
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateTo = (path: string) => {
  router.push(path);
};
</script>
<style scoped>
.home {
  text-align: center;
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.modules {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.module-card {
  background-color: #f8f9fa;
  border: 1px solid #eaeaea;
  border-radius: 8px;
  padding: 20px;
  width: 250px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  border-color: #d2bc9b;
}

.module-card h3 {
  color: #d2bc9b;
  margin-bottom: 10px;
}
</style>
