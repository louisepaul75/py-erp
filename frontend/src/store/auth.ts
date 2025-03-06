import { defineStore } from 'pinia';
import authService, { User, LoginCredentials, AuthState } from '../services/auth';

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null
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
      this.isLoading = true;
      try {
        // Check if we have a token
        if (authService.isAuthenticated()) {
          // Get the current user
          const user = await authService.getCurrentUser();
          if (user) {
            this.user = user;
            this.isAuthenticated = true;
          } else {
            // If we couldn't get the user, clear the auth state
            this.logout();
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        this.error = 'Failed to initialize authentication';
      } finally {
        this.isLoading = false;
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
        return user;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Login failed. Please check your credentials.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    // Logout user
    logout() {
      authService.logout();
      this.user = null;
      this.isAuthenticated = false;
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
