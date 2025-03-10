import { defineStore } from 'pinia';
import authService, { User, LoginCredentials, AuthState } from '../services/auth';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    initialized: false
  }),

  getters: {
    // Get the current user
    currentUser: (state) => state.user,

    // Check if user is authenticated
    userIsAuthenticated: (state) => state.isAuthenticated,

    // Check if user is admin
    isAdmin: (state) => state.user?.is_staff || state.user?.is_superuser || false,

    // Get user's full name
    fullName: (state) => {
      if (!state.user) return '';
      if (state.user.first_name || state.user.last_name) {
        return `${state.user.first_name} ${state.user.last_name}`.trim();
      }
      return state.user.username;
    }
  },

  actions: {
    // Initialize the auth state
    async init() {
      // If already initialized or currently loading, return
      if (this.initialized || this.isLoading) {
        console.debug('Auth store already initialized or loading');
        return;
      }

      this.isLoading = true;
      try {
        console.debug('Initializing auth store...');
        // Check if we have both tokens before attempting any auth operations
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
        
        console.debug('Tokens found:', {
          hasAccessToken: !!accessToken,
          hasRefreshToken: !!refreshToken
        });

        if (!accessToken && !refreshToken) {
          // No tokens available, mark as initialized and return
          console.debug('No tokens available, marking as initialized');
          this.initialized = true;
          return;
        }

        // First try to get the current user with the existing access token
        if (accessToken) {
          try {
            console.debug('Attempting to get user with current token');
            const user = await authService.getCurrentUser();
            if (user) {
              console.debug('Successfully retrieved user');
              this.user = user;
              this.isAuthenticated = true;
              this.initialized = true;
              return;
            }
          } catch (error) {
            // If getting user fails, we'll try to refresh the token below
            console.debug('Failed to get user with current token:', error);
          }
        }

        // If we reach here, either:
        // 1. We don't have an access token but have a refresh token
        // 2. The access token failed to get the user
        // In either case, try to refresh the token if we have a refresh token
        if (refreshToken) {
          try {
            console.debug('Attempting to refresh token');
            const newToken = await authService.refreshToken();
            if (newToken) {
              console.debug('Token refresh successful, getting user');
              // Try to get user with the new token
              const user = await authService.getCurrentUser();
              if (user) {
                console.debug('Successfully retrieved user after token refresh');
                this.user = user;
                this.isAuthenticated = true;
                this.initialized = true;
                return;
              }
            }
          } catch (error) {
            console.error('Token refresh failed:', error);
          }
        }

        // If we reach here, authentication failed
        console.debug('Authentication failed, logging out');
        await this.logout();
      } catch (error) {
        console.error('Auth initialization failed:', error);
        this.error = 'Failed to initialize authentication';
        await this.logout();
      } finally {
        this.isLoading = false;
        this.initialized = true;
        console.debug('Auth store initialization complete:', {
          isAuthenticated: this.isAuthenticated,
          hasUser: !!this.user,
          error: this.error
        });
      }
    },

    // Login user
    async login(credentials: LoginCredentials) {
      this.isLoading = true;
      this.error = null;

      try {
        const user = await authService.login(credentials);
        this.user = user;
        this.isAuthenticated = true;
        this.initialized = true;
        return user;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Login failed. Please check your credentials.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Logout user
    async logout() {
      authService.logout();
      this.user = null;
      this.isAuthenticated = false;
      this.error = null;
    },

    // Update user profile
    async updateProfile(userData: Partial<User>) {
      this.isLoading = true;
      this.error = null;

      try {
        const updatedUser = await authService.updateProfile(userData);
        this.user = updatedUser;
        return updatedUser;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to update profile';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Change password
    async changePassword(oldPassword: string, newPassword: string) {
      this.isLoading = true;
      this.error = null;

      try {
        await authService.changePassword(oldPassword, newPassword);
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to change password';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Clear any error messages
    clearError() {
      this.error = null;
    }
  }
});
