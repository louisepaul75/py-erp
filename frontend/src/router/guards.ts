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

    // If not initialized and not loading, initialize
    if (!authStore.isAuthenticated && !authStore.isLoading) {
      await authStore.init();
    }

    // After initialization, check authentication
    if (authStore.isAuthenticated) {
      // If we're already on the login page and authenticated, redirect to home
      if (to.name === 'Login') {
        return next({ name: 'Home' });
      }
      return next();
    } else {
      // If we're already on the login page, don't redirect again
      if (to.name === 'Login') {
        return next();
      }
      // Store the full path including query parameters for other routes
      return next({
        name: 'Login',
        query: { redirect: to.fullPath }
      });
    }
  } catch (error) {
    console.error('Auth guard error:', error);
    // In case of error, redirect to login
    return next({
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
