<template>
    <div class="home">
        <div class="welcome-section mb-5">
            <h1>{{ $t('home.welcome') }}</h1>
            <p class="lead text-muted">{{ $t('home.subtitle') }}</p>
        </div>

        <div class="modules">
            <div class="module-card" @click="navigateTo('/products')">
                <div class="icon-container mb-3">
                    <i class="fas fa-box fa-2x"></i>
                </div>
                <h3>{{ $t('home.products.title') }}</h3>
                <p class="text-muted">{{ $t('home.products.description') }}</p>
            </div>

            <div class="module-card" @click="navigateTo('/sales')">
                <div class="icon-container mb-3">
                    <i class="fas fa-chart-line fa-2x"></i>
                </div>
                <h3>{{ $t('home.sales.title') }}</h3>
                <p class="text-muted">{{ $t('home.sales.description') }}</p>
            </div>

            <div class="module-card" @click="navigateTo('/inventory')">
                <div class="icon-container mb-3">
                    <i class="fas fa-warehouse fa-2x"></i>
                </div>
                <h3>{{ $t('home.inventory.title') }}</h3>
                <p class="text-muted">{{ $t('home.inventory.description') }}</p>
            </div>

            <div class="module-card" @click="navigateTo('/production')">
                <div class="icon-container mb-3">
                    <i class="fas fa-industry fa-2x"></i>
                </div>
                <h3>{{ $t('home.production.title') }}</h3>
                <p class="text-muted">{{ $t('home.production.description') }}</p>
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
