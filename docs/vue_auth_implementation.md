# Vue.js Authentication Implementation

## Overview

This document provides technical details about the authentication implementation in the Vue.js frontend of the pyERP system. The authentication system uses JWT tokens to securely authenticate users with the Django backend and provides a seamless user experience with automatic token refresh.

## Architecture

The authentication system is built on the following components:

1. **Authentication Service**: Handles communication with the Django authentication endpoints
2. **API Service**: Manages API requests with authentication tokens
3. **Pinia Store**: Centralizes authentication state management
4. **Router Guards**: Protects routes based on authentication status
5. **Authentication Components**: Provides UI for login, logout, and profile management

## Authentication Flow

1. User enters credentials in the login form
2. Frontend sends credentials to Django's JWT token endpoint
3. Backend validates credentials and returns access and refresh tokens
4. Frontend stores tokens in localStorage
5. Frontend fetches user profile information
6. User is redirected to the intended destination

## Implementation Details

### Authentication Service (`auth.ts`)

The authentication service provides methods for interacting with the Django authentication endpoints:

```typescript
// Key methods in the authentication service
const authService = {
  login: async (credentials: LoginCredentials): Promise<User> => { ... },
  logout: () => { ... },
  isAuthenticated: (): boolean => { ... },
  getCurrentUser: async (): Promise<User | null> => { ... },
  refreshToken: async (): Promise<string | null> => { ... },
  updateProfile: async (userData: Partial<User>): Promise<User> => { ... },
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => { ... }
};
```

### API Service (`api.ts`)

The API service handles authentication tokens in requests and implements automatic token refresh:

```typescript
// Request interceptor for authentication tokens
api.interceptors.request.use((config) => {
  // Get CSRF token from cookie
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  
  // Add JWT token if available
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  
  return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle 401 errors with token refresh
    // ...
  }
);
```

### Pinia Store (`auth.ts`)

The Pinia store centralizes authentication state management:

```typescript
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
  }),
  
  getters: { ... },
  
  actions: {
    async init() { ... },
    async login(credentials: LoginCredentials) { ... },
    logout() { ... },
    async updateProfile(userData: Partial<User>) { ... },
    async changePassword(oldPassword: string, newPassword: string) { ... },
    clearError() { ... }
  }
});
```

### Router Guards (`guards.ts`)

Router guards protect routes based on authentication status:

```typescript
// Authentication guard for protected routes
export async function authGuard(to, from, next) {
  const authStore = useAuthStore();
  
  if (!authStore.isAuthenticated && !authStore.isLoading) {
    await authStore.init();
  }
  
  if (authStore.isAuthenticated) {
    next();
  } else {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  }
}

// Admin guard for admin-only routes
export async function adminGuard(to, from, next) { ... }

// Guest guard for guest-only routes
export async function guestGuard(to, from, next) { ... }
```

### Authentication Components

The authentication system includes the following components:

- **Login.vue**: Handles user login with form validation
- **Logout.vue**: Handles user logout with redirect
- **Profile.vue**: Allows users to view and update their profile information
- **Navbar.vue**: Displays authentication-related links based on auth state

## Security Considerations

1. **Token Storage**: Tokens are stored in localStorage for simplicity, but this approach has security implications. Consider using more secure alternatives like HttpOnly cookies in production.

2. **Token Refresh**: The system automatically refreshes tokens when they expire, providing a seamless user experience.

3. **CSRF Protection**: The system maintains Django's CSRF protection for non-JWT endpoints.

4. **Protected Routes**: Routes are protected with navigation guards to prevent unauthorized access.

5. **Role-Based Access**: The system implements role-based access control for admin-only routes.

## Future Enhancements

1. **Remember Me Functionality**: Add option for persistent login
2. **Multi-Factor Authentication**: Implement additional authentication factors for sensitive operations
3. **OAuth Integration**: Add support for third-party authentication providers
4. **Secure Token Storage**: Explore more secure alternatives to localStorage
5. **Comprehensive Testing**: Implement thorough testing for authentication components

## Conclusion

The Vue.js authentication implementation provides a secure and user-friendly authentication experience that integrates seamlessly with Django's authentication system. The modular design allows for easy extension and maintenance as the application evolves. 