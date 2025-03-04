<template>
    <div class="home">
        <div class="welcome-section mb-5">
            <h1>Welcome to pyERP</h1>
            <p class="lead text-muted">A comprehensive ERP system for managing your business operations.</p>
        </div>
        
        <div class="modules">
            <div class="module-card" @click="navigateTo('/products')">
                <div class="icon-container mb-3">
                    <i class="fas fa-box fa-2x"></i>
                </div>
                <h3>Products</h3>
                <p class="text-muted">Manage your product catalog, variants, and categories</p>
            </div>
            
            <div class="module-card" @click="navigateTo('/sales')">
                <div class="icon-container mb-3">
                    <i class="fas fa-chart-line fa-2x"></i>
                </div>
                <h3>Sales</h3>
                <p class="text-muted">Track orders, invoices, and customer information</p>
            </div>
            
            <div class="module-card" @click="navigateTo('/inventory')">
                <div class="icon-container mb-3">
                    <i class="fas fa-warehouse fa-2x"></i>
                </div>
                <h3>Inventory</h3>
                <p class="text-muted">Monitor stock levels and manage warehouses</p>
            </div>
            
            <div class="module-card" @click="navigateTo('/production')">
                <div class="icon-container mb-3">
                    <i class="fas fa-industry fa-2x"></i>
                </div>
                <h3>Production</h3>
                <p class="text-muted">Plan and track manufacturing processes</p>
            </div>
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
  padding: 40px 20px;
}

.welcome-section {
  max-width: 700px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
  color: var(--text-color);
  font-weight: 600;
}

.modules {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30px;
  margin-top: 40px;
}

.module-card {
  background-color: white;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 30px;
  width: 280px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
}

.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
  border-color: var(--primary-color);
}

.module-card h3 {
  color: var(--text-color);
  margin-bottom: 10px;
  font-weight: 600;
}

.icon-container {
  color: var(--primary-color);
  margin-bottom: 15px;
}
</style> 
