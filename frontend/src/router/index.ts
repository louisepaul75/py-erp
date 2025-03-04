import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { authGuard, adminGuard, guestGuard } from './guards';

// Define routes
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  
  // Authentication routes
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    beforeEnter: guestGuard
  },
  {
    path: '/logout',
    name: 'Logout',
    component: () => import('../views/auth/Logout.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/auth/Profile.vue'),
    beforeEnter: authGuard
  },
  
  // Product routes
  {
    path: '/products',
    name: 'ProductList',
    component: () => import('../views/products/ProductList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('../views/products/ProductDetail.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/products/variant/:id',
    name: 'VariantDetail',
    component: () => import('../views/products/VariantDetail.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/products/categories',
    name: 'CategoryList',
    component: () => import('../views/products/CategoryList.vue'),
    meta: { requiresAuth: true }
  },
  
  // Sales routes
  {
    path: '/sales',
    name: 'SalesList',
    component: () => import('../views/sales/SalesList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/sales/:id',
    name: 'SalesOrderDetail',
    component: () => import('../views/sales/SalesOrderDetail.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  
  // Catch-all route for 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Global navigation guard
router.beforeEach(async (to, from, next) => {
  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Apply the auth guard
    authGuard(to, from, next);
  } else {
    // No auth required, proceed
    next();
  }
});

export default router; 