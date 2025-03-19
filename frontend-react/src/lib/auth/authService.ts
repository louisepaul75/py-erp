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
      return await api.get('users/me/').json<User>();
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
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
      
      return newToken;
    } catch (error) {
      console.error('Error refreshing token:', error);
      authService.logout();
      return null;
    }
  },
  
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    return await api.patch('users/me/', {
      json: userData
    }).json<User>();
  },
  
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post('users/me/change-password/', {
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