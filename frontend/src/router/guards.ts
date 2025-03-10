import { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';
import { useAuthStore } from '../store/auth';

/**
 * Authentication guard for routes that require authentication
 * Redirects to login page if user is not authenticated
 */
export async function authGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  const authStore = useAuthStore();

  try {
    // If auth store is loading, wait for it to finish
    if (authStore.isLoading) {
      await new Promise<void>((resolve) => {
        const checkLoading = setInterval(() => {
          if (!authStore.isLoading) {
            clearInterval(checkLoading);
            resolve();
          }
        }, 100);
      });
    }

    // Wait for auth initialization if not already initialized
    if (!authStore.initialized) {
      await authStore.init();
    }

    // If user is authenticated, allow access
    if (authStore.isAuthenticated) {
      // If we're already on the login page and authenticated, redirect to home
      if (to.name === 'Login') {
        return next({ name: 'Home' });
      }
      return next();
    }

    // If not authenticated and on login page, allow access
    if (to.name === 'Login') {
      return next();
    }

    // If not authenticated, redirect to login
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  } catch (error) {
    console.error('Auth guard error:', error);
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  }
}

/**
 * Admin guard for routes that require admin privileges
 * Redirects to home page if user is not an admin
 */
export async function adminGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  const authStore = useAuthStore();

  try {
    // Wait for auth initialization if not already initialized
    if (!authStore.initialized) {
      await authStore.init();
    }

    // If user is authenticated and is an admin, allow access
    if (authStore.isAuthenticated && authStore.isAdmin) {
      next();
      return;
    }

    // If user is authenticated but not an admin, redirect to home
    if (authStore.isAuthenticated) {
      next({ name: 'Home' });
      return;
    }

    // If not authenticated, redirect to login
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  } catch (error) {
    console.error('Admin guard error:', error);
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  }
}

/**
 * Guest guard for routes that should only be accessible to guests
 * Redirects to home page if user is already authenticated
 */
export async function guestGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  const authStore = useAuthStore();

  try {
    // Wait for auth initialization if not already initialized
    if (!authStore.initialized) {
      await authStore.init();
    }

    // If user is authenticated, redirect to home or the intended destination
    if (authStore.isAuthenticated) {
      const redirectPath = to.query.redirect as string;
      if (redirectPath) {
        next(redirectPath);
        return;
      }
      next({ name: 'Home' });
      return;
    }

    // If not authenticated, allow access
    next();
  } catch (error) {
    console.error('Guest guard error:', error);
    next();
  }
}
