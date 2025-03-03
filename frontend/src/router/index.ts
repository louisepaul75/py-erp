import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

// Define routes
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/products',
    name: 'ProductList',
    component: () => import('../views/products/ProductList.vue')
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('../views/products/ProductDetail.vue'),
    props: true
  },
  {
    path: '/products/variant/:id',
    name: 'VariantDetail',
    component: () => import('../views/products/VariantDetail.vue'),
    props: true
  },
  {
    path: '/products/categories',
    name: 'CategoryList',
    component: () => import('../views/products/CategoryList.vue')
  }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

export default router; 