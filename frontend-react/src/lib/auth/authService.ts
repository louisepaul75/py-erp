import ky, { KyResponse, HTTPError } from 'ky';
import { jwtDecode } from 'jwt-decode';
import { cookies } from 'next/headers';
import { API_URL, AUTH_CONFIG } from '../config';
import { User, LoginCredentials, JwtPayload } from './authTypes';

// API-Instanz ohne Auth für Token-Endpunkte
const authApi = ky.create({
  prefixUrl: API_URL,
  timeout: 30000,
  credentials: 'include',  // Include cookies in requests
  hooks: {
    beforeRequest: [
      request => {
        // For token/refresh endpoint, add the Authorization header if we have a token
        // This is a backup in case cookies aren't working properly
        if (request.url.toString().includes('token/refresh')) {
          const token = cookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
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

// Client-side cookie operations
const cookieStorage = {
  setItem: (name: string, value: string, options = {}) => {
    document.cookie = `${name}=${value}; path=/; ${Object.entries(options).map(([k, v]) => `${k}=${v}`).join('; ')}`;
  },
  getItem: (name: string) => {
    const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
    return match ? match[2] : null;
  },
  removeItem: (name: string) => {
    document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
  },
  // Helper to list all cookies for debugging
  listAll: () => {
    const cookies = document.cookie.split(';').map(cookie => cookie.trim());
    const cookieMap: Record<string, string> = {};
    
    cookies.forEach(cookie => {
      if (cookie) {
        const [name, value] = cookie.split('=');
        cookieMap[name] = value;
      }
    });
    
    console.log('All cookies:', cookieMap);
    return cookieMap;
  }
};

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
    const cookieToken = cookieStorage.getItem('csrftoken');
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
      const newCookieToken = cookieStorage.getItem('csrftoken');
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
        const token = cookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
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
              const token = cookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
              const request = error.request.clone();
              if (token) {
                request.headers.set('Authorization', `Bearer ${token}`);
              }
              return ky(request);
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
              return ky(request);
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

export const authService = {
  getCurrentUser: async (): Promise<User | null> => {
    try {
      const user = await api.get('profile/').json<User>();
      return user;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  },
  
  getToken: (): string | null => {
    return cookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
  },
  
  login: async (credentials: LoginCredentials): Promise<User> => {
    try {
      // Log cookies before login attempt
      console.log('Cookies before login:');
      cookieStorage.listAll();
      
      // Send login request - backend will set cookies
      const response = await authApi.post(AUTH_CONFIG.tokenEndpoint, {
        json: credentials,
        credentials: 'include'  // Ensure cookies are included
      }).json<{ access: string; refresh: string }>();
      
      console.log('Login response received', { 
        hasAccess: !!response.access, 
        hasRefresh: !!response.refresh,
        accessTokenLength: response.access?.length,
        refreshTokenLength: response.refresh?.length 
      });
      
      // Store tokens in cookies
      if (response.access) {
        cookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, response.access);
        console.log('Access token stored in cookie');
      }
      
      if (response.refresh) {
        cookieStorage.setItem(AUTH_CONFIG.tokenStorage.refreshToken, response.refresh);
        console.log('Refresh token stored in cookie');
      }
      
      // Log cookies after setting them
      console.log('Cookies after login:');
      cookieStorage.listAll();
      
      // Fetch CSRF token after successful login
      await csrfService.fetchToken();
      
      // Decode token to get basic user info
      const decoded: JwtPayload = jwtDecode(response.access);
      
      // Get full user profile
      try {
        const userProfile = await api.get('profile/').json<User>();
        return userProfile;
      } catch (profileError) {
        console.warn('Error getting full profile, using basic info from token:', profileError);
        
        // Return basic user info from token if profile fetch fails
        return {
          id: decoded.user_id,
          username: decoded.username || '',
          email: decoded.email || '',
          firstName: decoded.first_name || '',
          lastName: decoded.last_name || '',
          isAdmin: decoded.is_staff || false,
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error instanceof HTTPError) {
        const errorText = await error.response.text();
        throw new Error(errorText || 'Ungültige Anmeldedaten. Bitte versuche es erneut.');
      }
      throw new Error('Ungültige Anmeldedaten. Bitte versuche es erneut.');
    }
  },
  
  logout: async (): Promise<void> => {
    try {
      await api.post('logout/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  },
  
  refreshToken: async (): Promise<boolean> => {
    try {
      // Log cookies before refresh
      console.log('Cookies before token refresh:');
      cookieStorage.listAll();
      
      // Get refresh token from cookie
      const refreshToken = cookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
      
      if (!refreshToken) {
        console.error('No refresh token available');
        return false;
      }
      
      console.log('Refreshing token with refresh token:', refreshToken);
      
      // Send refresh token in request body
      const response = await authApi.post(AUTH_CONFIG.refreshEndpoint, {
        json: {
          refresh: refreshToken
        },
        credentials: 'include'  // Ensure cookies are included
      }).json<{ access: string }>();
      
      console.log('Refresh token response received');
      
      // Store the new access token
      if (response.access) {
        cookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, response.access);
        console.log('New access token stored in cookie');
      }
      
      // Log cookies after refresh
      console.log('Cookies after token refresh:');
      cookieStorage.listAll();
      
      return true;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return false;
    }
  },
  
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    return await api.patch('profile/', {
      json: userData
    }).json<User>();
  },
  
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post('profile/change-password/', {
      json: { old_password: oldPassword, new_password: newPassword }
    });
  }
};

export { api }; 