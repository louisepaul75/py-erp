import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { authGuard, adminGuard, guestGuard } from './guards';

// Define routes
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },

  // Health status page (no auth required)
  {
    path: '/Health',
    name: 'Health',
    component: () => import('../views/Health.vue'),
    meta: { requiresAuth: false }
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
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/auth/Settings.vue'),
    meta: { requiresAuth: true }
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
  {
    path: '/artikel-management',
    name: 'ArtikelManagement',
    component: () => import('../views/products/ArtikelManagement.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/artikel-management/:id',
    name: 'ArtikelManagementWithProduct',
    component: () => import('../views/products/ArtikelManagement.vue'),
    props: true,
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
  {
    path: '/sales/customer/:id',
    name: 'CustomerDetail',
    component: () => import('../views/customers/CustomerDetail.vue'),
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
router.beforeEach((to, from, next) => {
  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Return the Promise from authGuard
    return authGuard(to, from, next);
  } else {
    // No auth required, proceed
    return next();
  }
});

export default router;
