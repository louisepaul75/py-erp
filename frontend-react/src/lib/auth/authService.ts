import ky, { KyResponse, HTTPError } from 'ky';
import { jwtDecode } from 'jwt-decode';
import { API_URL, AUTH_CONFIG } from '../config';
import { User, LoginCredentials, JwtPayload } from './authTypes';
import { clientCookieStorage } from './clientCookies';

// API-Instanz ohne Auth für Token-Endpunkte
const authApi = ky.create({
  prefixUrl: API_URL,
  timeout: 30000,
  credentials: 'include',  // Include cookies in requests
  hooks: {
    beforeRequest: [
      request => {
        // For token/refresh endpoint, add the Authorization header if we have a token
        if (request.url.toString().includes('token/refresh')) {
          const token = clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
          if (token) {
            request.headers.set('Authorization', `Bearer ${token}`);
            console.log(`Adding Bearer token to refresh request (token length: ${token.length})`);
          }
        }
      }
    ],
    beforeError: [
      async (error) => {
        const { response } = error;
        try {
          const errorText = await response.text();
          console.error(`Auth API error (${response.status}):`, errorText);
          error.message = errorText;
        } catch (e) {
          error.message = response.statusText;
        }
        return error;
      },
    ],
  },
});

// CSRF token management
export const csrfService = {
  // Get CSRF token from various sources
  getToken: (): string | null => {
    // First try meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (metaToken && metaToken.length > 0) {
      return metaToken;
    }
    
    // Try cookie
    const cookieToken = clientCookieStorage.getItem('csrftoken');
    if (cookieToken) {
      return cookieToken;
    }
    
    // Try Django settings
    const settingsToken = (window as any)?.DJANGO_SETTINGS?.CSRF_TOKEN;
    if (settingsToken) {
      return settingsToken;
    }
    
    return null;
  },
  
  // Set CSRF token in meta tag for future use
  setToken: (token: string): void => {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
      metaTag.setAttribute('content', token);
    } else {
      // Create meta tag if it doesn't exist
      const newMetaTag = document.createElement('meta');
      newMetaTag.name = 'csrf-token';
      newMetaTag.content = token;
      document.head.appendChild(newMetaTag);
    }
  },
  
  // Fetch fresh CSRF token from the server
  fetchToken: async (): Promise<string | null> => {
    try {
      // Try to fetch from dedicated CSRF endpoint
      const csrfResponse = await fetch(`${API_URL}/csrf/`, {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        credentials: "include" // Include cookies
      });
      
      if (csrfResponse.ok) {
        const data = await csrfResponse.json();
        if (data.csrf_token) {
          csrfService.setToken(data.csrf_token);
          return data.csrf_token;
        }
      }
      
      // Fallback: check if the server set a CSRF cookie during the request
      const newCookieToken = clientCookieStorage.getItem('csrftoken');
      if (newCookieToken) {
        csrfService.setToken(newCookieToken);
        return newCookieToken;
      }
      
      return null;
    } catch (error) {
      console.error("Error fetching CSRF token:", error);
      return null;
    }
  }
};

// API-Instanz mit Auth für reguläre API-Aufrufe
const api = ky.extend({
  prefixUrl: API_URL,
  timeout: 30000,
  credentials: 'include',  // Include cookies in requests
  hooks: {
    beforeRequest: [
      request => {
        // Add CSRF token to non-GET requests if available
        if (request.method !== 'GET') {
          const csrfToken = csrfService.getToken();
          if (csrfToken) {
            request.headers.set('X-CSRFToken', csrfToken);
            console.log(`Adding CSRF token to ${request.method} request to ${request.url}`);
          } else {
            console.warn(`No CSRF token available for ${request.method} request to ${request.url}`);
          }
        }
        
        // Add Authorization header with JWT token if available
        const token = clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
          console.log(`Adding Bearer token to request to ${request.url} (token length: ${token.length})`);
        } else {
          console.warn(`No access token available for request to ${request.url}`);
        }
      }
    ],
    beforeError: [
      async (error: HTTPError) => {
        const { response } = error;
        
        // 401 Unauthorized Fehler behandeln (Token abgelaufen)
        if (response.status === 401) {
          try {
            // Versuche, den Token zu erneuern
            const refreshSuccess = await authService.refreshToken();
            
            if (refreshSuccess) {
              // Request mit neuem Token wiederholen
              const token = clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
              const request = error.request.clone();
              if (token) {
                request.headers.set('Authorization', `Bearer ${token}`);
              }
              // Explicitly handle the response type to satisfy TypeScript
              const newResponse = await ky(request);
              // Don't return the response directly, throw a new error with the right type
              throw new HTTPError(newResponse, request, error.options);
            }
          } catch (refreshError) {
            // Wenn Token-Erneuerung fehlschlägt, ausloggen
            authService.logout();
            window.location.href = '/login';
          }
        }
        
        // 403 Forbidden could be CSRF related
        if (response.status === 403) {
          try {
            // Try to refresh CSRF token
            const newCsrfToken = await csrfService.fetchToken();
            if (newCsrfToken && error.request.method !== 'GET') {
              // Retry request with new CSRF token
              const request = error.request.clone();
              request.headers.set('X-CSRFToken', newCsrfToken);
              // Explicitly handle the response type to satisfy TypeScript
              const newResponse = await ky(request);
              // Don't return the response directly, throw a new error with the right type
              throw new HTTPError(newResponse, request, error.options);
            }
          } catch (csrfError) {
            console.error('CSRF token refresh failed:', csrfError);
          }
        }
        
        try {
          error.message = await response.text();
        } catch (e) {
          error.message = response.statusText;
        }
        
        return error;
      },
    ],
  },
});

// Export the auth service functions
export const authService = {
  getCurrentUser: async (): Promise<User | null> => {
    try {
      const token = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
      if (!token) {
        return null;
      }

      // Validate the token before using it
      try {
        const decoded = jwtDecode<JwtPayload>(token);
        const currentTime = Math.floor(Date.now() / 1000);
        
        // If token is expired, try to refresh before proceeding
        if (decoded.exp && decoded.exp < currentTime) {
          const refreshSuccess = await authService.refreshToken();
          if (!refreshSuccess) {
            await clearAuthTokens();
            return null;
          }
        }
      } catch (tokenError) {
        console.error('Invalid token format:', tokenError);
        await clearAuthTokens();
        return null;
      }

      const response = await api.get('auth/user/').json<User>();
      return response;
    } catch (error) {
      if (error instanceof HTTPError && error.response.status === 401) {
        // Try to refresh the token
        const refreshSuccess = await authService.refreshToken();
        if (refreshSuccess) {
          // Retry getting user info
          try {
            const response = await api.get('auth/user/').json<User>();
            return response;
          } catch (retryError) {
            console.error('Failed to get user info after token refresh:', retryError);
            await clearAuthTokens();
            return null;
          }
        }
        await clearAuthTokens();
        return null;
      }
      console.error('Error getting current user:', error);
      return null;
    }
  },
  
  getToken: async (): Promise<string | null> => {
    const token = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
    if (!token) {
      // Try to refresh if we have a refresh token
      const refreshSuccess = await authService.refreshToken();
      if (refreshSuccess) {
        return await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
      }
      return null;
    }
    return token;
  },
  
  login: async (credentials: LoginCredentials): Promise<User> => {
    try {
      // Ensure we have a CSRF token for the login request
      await csrfService.fetchToken();
      
      // Get tokens from the token endpoint
      const tokenResponse = await authApi.post('token/', { json: credentials }).json<{
        access: string;
        refresh: string;
      }>();
      
      // Store tokens
      await setAuthTokens(tokenResponse);
      
      // Get user info with the new token
      const user = await authService.getCurrentUser();
      if (!user) {
        throw new Error('Failed to get user info after login');
      }
      
      return user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  logout: async (): Promise<void> => {
    try {
      // Try to call logout endpoint, but don't fail if it doesn't work
      try {
        await api.post('auth/logout/');
      } catch (error) {
        console.warn('Logout endpoint call failed:', error);
      }
    } finally {
      // Always clear tokens
      await clearAuthTokens();
    }
  },
  
  refreshToken: async (): Promise<boolean> => {
    try {
      const refreshToken = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
      if (!refreshToken) {
        console.warn('No refresh token available');
        return false;
      }

      // Validate refresh token format before using
      try {
        jwtDecode(refreshToken);
      } catch (tokenError) {
        console.error('Invalid refresh token format:', tokenError);
        await clearAuthTokens();
        return false;
      }

      const response = await authApi.post('token/refresh/', {
        json: { refresh: refreshToken }
      }).json<{ access: string }>();

      await clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, response.access);
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear tokens on refresh failure
      await clearAuthTokens();
      return false;
    }
  },
  
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await api.patch('auth/user/', { json: userData }).json<User>();
    return response;
  },
  
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post('auth/password/change/', {
      json: {
        old_password: oldPassword,
        new_password: newPassword
      }
    });
  }
};

const getAuthToken = async () => {
  return await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
};

const setAuthTokens = async (tokenResponse: TokenResponse) => {
  await clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, tokenResponse.access);
  await clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.refreshToken, tokenResponse.refresh);
};

const clearAuthTokens = async () => {
  await clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.accessToken);
  await clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.refreshToken);
};

const refreshAuthToken = async () => {
  const refreshToken = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch('/api/auth/token/refresh/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const data = await response.json();
    await clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, data.access);
    return data.access;
  } catch (error) {
    console.error('Error refreshing token:', error);
    throw error;
  }
};

export { api }; 