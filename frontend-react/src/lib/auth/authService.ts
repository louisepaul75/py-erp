import ky, { KyResponse, HTTPError } from 'ky';
import { jwtDecode } from 'jwt-decode';
import { cookies } from 'next/headers';
import { API_URL, AUTH_CONFIG } from '../config';
import { User, LoginCredentials, JwtPayload } from './authTypes';

// API-Instanz ohne Auth für Token-Endpunkte
const authApi = ky.create({
  prefixUrl: API_URL,
  timeout: 30000,
  hooks: {
    beforeError: [
      async (error) => {
        const { response } = error;
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
      const token = authService.getToken();
      if (!token) {
        console.error("No JWT token available for CSRF token fetch");
        return null;
      }
      
      // Try to fetch from dedicated CSRF endpoint
      const csrfResponse = await fetch(`${API_URL}/csrf/`, {
        method: "GET",
        headers: {
          "Accept": "application/json",
          "Authorization": `Bearer ${token}`
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

export const authService = {
  getCurrentUser: async (): Promise<User | null> => {
    const token = cookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
    
    if (!token) {
      return null;
    }
    
    try {
      // Token dekodieren, um Benutzer-ID zu erhalten
      const decoded: JwtPayload = jwtDecode<JwtPayload>(token);
      
      // Prüfen, ob Token abgelaufen ist
      const currentTime = Date.now() / 1000;
      if (decoded.exp && decoded.exp < currentTime) {
        // Token abgelaufen, versuche zu erneuern
        const newToken = await authService.refreshToken();
        if (!newToken) {
          return null;
        }
      }
      
      // Benutzerdetails von API abrufen
      return await api.get('profile/').json<User>();
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
      const response = await authApi.post(AUTH_CONFIG.tokenEndpoint, {
        json: credentials
      }).json<{ access: string; refresh: string }>();
      
      // Save in cookies with HttpOnly and secure flags in production
      cookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, response.access, {
        maxAge: 15 * 60, // 15 minutes
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      
      cookieStorage.setItem(AUTH_CONFIG.tokenStorage.refreshToken, response.refresh, {
        maxAge: 7 * 24 * 60 * 60, // 7 days
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      
      // Try to fetch and store CSRF token after login
      await csrfService.fetchToken();
      
      // Token dekodieren, um grundlegende Benutzerinfos zu erhalten
      const decoded: JwtPayload = jwtDecode<JwtPayload>(response.access);
      
      // Grundlegende Benutzerinfos zurückgeben
      return {
        id: decoded.user_id,
        username: decoded.username || '',
        email: decoded.email || '',
        firstName: decoded.first_name || '',
        lastName: decoded.last_name || '',
        isAdmin: decoded.is_staff || false,
      };
    } catch (error) {
      console.error('Login error:', error);
      throw new Error('Ungültige Anmeldedaten. Bitte versuche es erneut.');
    }
  },
  
  logout: (): void => {
    cookieStorage.removeItem(AUTH_CONFIG.tokenStorage.accessToken);
    cookieStorage.removeItem(AUTH_CONFIG.tokenStorage.refreshToken);
  },
  
  refreshToken: async (): Promise<string | null> => {
    const refreshToken = cookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
    
    if (!refreshToken) {
      return null;
    }
    
    try {
      const response = await authApi.post(AUTH_CONFIG.refreshEndpoint, {
        json: { refresh: refreshToken }
      }).json<{ access: string }>();
      
      const newToken = response.access;
      cookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, newToken, {
        maxAge: 15 * 60, // 15 minutes
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      
      // Try to refresh CSRF token as well
      await csrfService.fetchToken();
      
      return newToken;
    } catch (error) {
      console.error('Error refreshing token:', error);
      authService.logout();
      return null;
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

// API-Instanz mit Auth für reguläre API-Aufrufe
const api = ky.extend({
  prefixUrl: API_URL,
  timeout: 30000,
  hooks: {
    beforeRequest: [
      request => {
        const token = cookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
        
        // Add CSRF token to non-GET requests if available
        if (request.method !== 'GET') {
          const csrfToken = csrfService.getToken();
          if (csrfToken) {
            request.headers.set('X-CSRFToken', csrfToken);
          }
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
            const newToken = await authService.refreshToken();
            
            if (newToken) {
              // Request mit neuem Token wiederholen - aber als error zurückgeben
              const request = error.request.clone();
              request.headers.set('Authorization', `Bearer ${newToken}`);
              try {
                await ky(request);
              } catch (e) {
                // Ignorieren und mit dem ursprünglichen Fehler fortfahren
              }
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
              try {
                await ky(request);
              } catch (e) {
                // Ignore and continue with original error
              }
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

export { api }; 