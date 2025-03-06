import api from './api';

// Define types for authentication
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Authentication service
const authService = {
  // Login with username and password
  login: async (credentials: LoginCredentials): Promise<User> => {
    try {
      // Get JWT tokens
      const tokenResponse = await api.post<TokenResponse>('/api/token/', credentials);

      // Store tokens in localStorage
      localStorage.setItem('access_token', tokenResponse.data.access);
      localStorage.setItem('refresh_token', tokenResponse.data.refresh);

      // Set the token in the API headers for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${tokenResponse.data.access}`;

      // Get user profile
      const userResponse = await api.get<User>('/api/v1/profile/');
      return userResponse.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },

  // Logout user
  logout: () => {
    // Remove tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Remove Authorization header
    delete api.defaults.headers.common['Authorization'];
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  // Get current user profile
  getCurrentUser: async (): Promise<User | null> => {
    try {
      // Check if we have a token
      const token = localStorage.getItem('access_token');
      if (!token) {
        return null;
      }

      // Set the token in the API headers
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // Get user profile
      const response = await api.get<User>('/api/v1/profile/');
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  },

  // Refresh the access token using the refresh token
  refreshToken: async (): Promise<string | null> => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        return null;
      }

      const response = await api.post<{ access: string }>('/api/token/refresh/', {
        refresh: refreshToken
      });

      const newAccessToken = response.data.access;
      localStorage.setItem('access_token', newAccessToken);
      api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;

      return newAccessToken;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, logout the user
      authService.logout();
      return null;
    }
  },

  // Update the user's profile
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await api.patch<User>('/api/v1/profile/', userData);
    return response.data;
  },

  // Change the user's password
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post('/accounts/password_change/', {
      old_password: oldPassword,
      new_password1: newPassword,
      new_password2: newPassword
    });
  }
};

export default authService;
