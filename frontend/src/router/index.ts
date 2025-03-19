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

  // SMTP Settings route
  {
    path: '/settings/smtp',
    name: 'SMTPSettings',
    component: () => import('../views/settings/SMTPSettings.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },

  // Data Viewer route
  {
    path: '/settings/data-viewer',
    name: 'DataViewer',
    component: () => import('../views/settings/DataViewer.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },

  // Users & Permissions routes are now integrated in the admin settings page

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
    name: 'Sales',
    component: () => import('../views/sales/SalesBase.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/sales/orders/:id',
    name: 'SalesOrderDetail',
    component: () => import('../views/sales/SalesOrderDetail.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/sales/orders/:id/edit',
    name: 'SalesOrderEdit',
    component: () => import('../views/sales/SalesOrderEdit.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/sales/customers/:id',
    name: 'CustomerDetail',
    component: () => import('../views/sales/CustomerDetail.vue'),
    props: true,
    meta: { requiresAuth: true }
  },

  // Inventory routes
  {
    path: '/inventory',
    component: () => import('../views/inventory/InventoryBase.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'InventoryDashboard',
        component: () => import('../views/inventory/InventoryDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'warehouse',
        component: () => import('../views/inventory/warehouse/WarehouseManagement.vue'),
        meta: { requiresAuth: true },
        children: [
          {
            path: '',
            name: 'WarehouseManagement',
            redirect: { name: 'StorageLocations' }
          },
          {
            path: 'locations',
            name: 'StorageLocations',
            component: () => import('../views/inventory/warehouse/StorageLocations.vue'),
            meta: { requiresAuth: true }
          },
          {
            path: 'boxes',
            name: 'BoxManagement',
            component: () => import('../views/inventory/warehouse/BoxManagement.vue'),
            meta: { requiresAuth: true }
          },
          {
            path: 'map',
            name: 'WarehouseMap',
            component: () => import('../views/inventory/warehouse/WarehouseMap.vue'),
            meta: { requiresAuth: true }
          }
        ]
      },
      {
        path: 'products',
        name: 'ProductInventory',
        component: () => import('../views/inventory/ProductInventory.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'movements',
        name: 'InventoryMovements',
        component: () => import('../views/inventory/InventoryMovements.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },

  // Testing routes
  {
    path: '/testing',
    name: 'Testing',
    component: () => import('../views/Testing.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/testing/components',
    name: 'Components',
    component: () => import('../views/Components.vue'),
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
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    // Return the Promise from authGuard
    return authGuard(to, from, next);
  } else {
    // No auth required, proceed
    return next();
  }
});

export default router;
