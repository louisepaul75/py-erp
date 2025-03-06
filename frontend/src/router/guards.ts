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

  // If auth store is not initialized yet, initialize it
  if (!authStore.isAuthenticated && !authStore.isLoading) {
    await authStore.init();
  }

  // If user is authenticated, allow access
  if (authStore.isAuthenticated) {
    next();
  } else {
    // Redirect to login page with the intended destination
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

  // If auth store is not initialized yet, initialize it
  if (!authStore.isAuthenticated && !authStore.isLoading) {
    await authStore.init();
  }

  // If user is authenticated and is an admin, allow access
  if (authStore.isAuthenticated && authStore.isAdmin) {
    next();
  } else if (authStore.isAuthenticated) {
    // If user is authenticated but not an admin, redirect to home
    next({ name: 'Home' });
  } else {
    // If user is not authenticated, redirect to login
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

  // If auth store is not initialized yet, initialize it
  if (!authStore.isLoading) {
    await authStore.init();
  }

  // If user is authenticated, redirect to home or the intended destination
  if (authStore.isAuthenticated) {
    // If there's a redirect query parameter, go there
    const redirectPath = to.query.redirect as string;
    if (redirectPath) {
      next(redirectPath);
    } else {
      // Otherwise go to home
      next({ name: 'Home' });
    }
  } else {
    // If user is not authenticated, allow access
    next();
  }
}
