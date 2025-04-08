import ky, { KyResponse, HTTPError } from 'ky';
import { jwtDecode } from 'jwt-decode';
import { API_URL, AUTH_CONFIG } from '../config';
import { User, LoginCredentials, JwtPayload, TokenResponse } from './authTypes';
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

// Log when the auth module is loaded
console.log('[AuthService] Module initialized');

// Initialize CSRF functionality
export const csrfService = {
  // Get the CSRF token from the document
  getToken: () => {
    if (typeof document !== 'undefined') {
      // Try to get it from the meta tag first
      const meta = document.querySelector('meta[name="csrf-token"]');
      if (meta && meta.getAttribute('content')) {
        const metaToken = meta.getAttribute('content');
        if (metaToken && metaToken.length > 0) {
          return metaToken;
        }
      }
      
      // Fallback to cookie
      const csrfCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
      
      if (csrfCookie) {
        return csrfCookie.split('=')[1];
      }
    }
    
    return null;
  },
  
  // Fetch a new CSRF token
  fetchToken: async () => {
    try {
      // Call the CSRF endpoint (path relative to API_URL)
      const response = await fetch(`${API_URL}/csrf/`, {
        method: 'GET',
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch CSRF token: ${response.status}`);
      }
      
      // The server should set the CSRF cookie/meta tag in the response
      // Extract from the response header for debugging
      const csrfHeader = response.headers.get('X-CSRFToken');
      
      if (csrfHeader) {
        // We could update our meta tag directly
        if (typeof document !== 'undefined') {
          const meta = document.querySelector('meta[name="csrf-token"]');
          if (meta) {
            meta.setAttribute('content', csrfHeader);
          }
        }
      }
      
      // Get the token from the cookie/meta tag
      const token = csrfService.getToken();
      return token;
    } catch (error) {
      console.error('Error fetching CSRF token:', error);
      return null;
    }
  },
  
  // Add CSRF token to headers
  addToken: (headers: Headers) => {
    const token = csrfService.getToken();
    if (token) {
      headers.set('X-CSRFToken', token);
    }
    return headers;
  },
};

// Centralized API instance for authenticated requests
export const api = ky.create({
  prefixUrl: API_URL,
  timeout: 30000,
  credentials: 'include',  // Include cookies in requests
  hooks: {
    beforeRequest: [
      async request => {
        // Add CSRF token to all non-GET requests
        if (request.method !== 'GET' && typeof window !== 'undefined') {
          // Try to get existing token
          let csrfToken = csrfService.getToken();
          
          // If no token, try to fetch one
          if (!csrfToken) {
            csrfToken = await csrfService.fetchToken();
          }
          
          // Add token to request if available
          if (csrfToken) {
            request.headers.set('X-CSRFToken', csrfToken);
          }
        }
        
        // Add authorization token to all requests
        const token = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
      }
    ],
    beforeError: [
      async error => {
        // Check if error is due to 401 Unauthorized
        if (error instanceof HTTPError && error.response.status === 401) {
          console.log('[API] Received 401 response, attempting to refresh token...');
          
          // Check if we can attempt to refresh the token
          const refreshToken = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
          if (refreshToken && !error.request.url.toString().includes('token/refresh') && !error.request.url.toString().includes('auth/logout')) {
            try {
              // Attempt to refresh token
              const refreshed = await authService.refreshToken();
              
              if (refreshed) {
                console.log('[API] Token refreshed successfully, retrying original request...');
                
                // Clone the original request options
                const options = {
                  method: error.request.method,
                  credentials: 'include',
                  headers: {},
                };
                
                // Copy headers (except possibly outdated Authorization)
                error.request.headers.forEach((value, key) => {
                  if (key.toLowerCase() !== 'authorization') {
                    options.headers[key] = value;
                  }
                });
                
                // Add fresh token
                const freshToken = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
                if (freshToken) {
                  options.headers['Authorization'] = `Bearer ${freshToken}`;
                }
                
                // Add body if it existed (for PUT/POST/etc)
                if (error.request.body) {
                  try {
                    // Clone the body as best as possible
                    if (error.request.body instanceof FormData) {
                      options.body = error.request.body;
                    } else if (typeof error.request.body === 'string') {
                      options.body = error.request.body;
                    }
                  } catch (bodyError) {
                    console.warn('Could not clone request body:', bodyError);
                  }
                }
                
                // Retry with fresh token
                const retryResponse = await fetch(error.request.url, options);
                
                // Create a new response with the retry response data
                const clonedResponse = new Response(await retryResponse.blob(), {
                  status: retryResponse.status,
                  statusText: retryResponse.statusText,
                  headers: retryResponse.headers
                });
                
                // Prevent ky from treating this as an error
                const modifiedError = error;
                modifiedError.response = clonedResponse;
                
                // If retry successful, don't treat as error
                if (retryResponse.ok) {
                  console.log('[API] Request retry successful after token refresh');
                  // Prevent Ky from treating this as an error
                  return new Response(await retryResponse.blob(), {
                    status: 200,
                    statusText: 'OK',
                    headers: retryResponse.headers
                  });
                }
              }
            } catch (refreshError) {
              console.error('[API] Error refreshing token:', refreshError);
            }
          }
        }
        
        // Process API error response
        try {
          const { response } = error;
          const contentType = response.headers.get('content-type');
          
          if (contentType && contentType.includes('application/json')) {
            try {
              const data = await response.json();
              if (data && typeof data === 'object') {
                if (data.detail) {
                  error.message = data.detail;
                } else if (data.message) {
                  error.message = data.message;
                } else {
                  error.message = JSON.stringify(data);
                }
              }
            } catch (jsonError) {
              console.warn('Error parsing JSON error response:', jsonError);
              error.message = await response.text() || response.statusText;
            }
          } else {
            error.message = await response.text() || response.statusText;
          }
        } catch (processError) {
          console.warn('Error processing API error:', processError);
        }
        
        return error;
      }
    ],
  },
});

// Helper function to clear auth tokens
export const clearAuthTokens = async (): Promise<void> => {
  try {
    await clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.accessToken);
    await clientCookieStorage.removeItem(AUTH_CONFIG.tokenStorage.refreshToken);
    console.log('[clearAuthTokens] Auth tokens cleared');
  } catch (error) {
    console.error('[clearAuthTokens] Error clearing auth tokens:', error);
  }
};

// Export the auth service functions
export const authService = {
  getCurrentUser: async (): Promise<User | null> => {
    console.log('[getCurrentUser] Starting function.');
    try {
      // Get the current access token (needed for the initial request header)
      // Let the beforeError hook handle cases where the initial token might be missing/invalid
      const token = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
      // If no token exists upfront, we can return null early
      if (!token) {
         console.warn('[getCurrentUser] No access token found in storage.');
         return null;
      }
      
      // Attempt the fetch. The beforeError hook will handle 401/refresh/retry.
      console.log(`[getCurrentUser] Attempting api.get('auth/user/')...`);
      const user = await api.get('auth/user/', {
        // We still need to provide the initial token for the first attempt
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }).json<User>(); 
      console.log('[getCurrentUser] Fetched user successfully:', user);
      return user;
    } catch (error) {
      // Catch ANY error during the process (initial 401 not handled by hook, non-401, hook refresh fail, hook retry fail, JSON parse error)
      console.error('[getCurrentUser] Error caught during user fetch process:', error); 
      // Regardless of the error, if we end up here, authentication failed or user couldn't be fetched.
      // Attempt to clear tokens just in case, but don't await it strictly if it fails
      try { 
        await clearAuthTokens(); 
      } catch (clearError) {
        console.error('[getCurrentUser] Failed to clear tokens during error handling:', clearError);
      }
      console.log('[getCurrentUser] Returning null due to error.');
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
      
      // Get tokens from the token endpoint (use path relative to API_URL prefix)
      const tokenResponse = await authApi.post('token/', { json: credentials }).json<{
        access: string;
        refresh: string;
      }>();
      
      // Store tokens
      await clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, tokenResponse.access);
      await clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.refreshToken, tokenResponse.refresh);
      
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
    console.log('[refreshToken] Starting function.'); // Log start
    try {
      const refreshToken = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
      if (!refreshToken) {
        console.warn('[refreshToken] No refresh token available. Returning false.'); // Log no token
        return false;
      }
      console.log(`[refreshToken] Refresh token found (len: ${refreshToken.length}). Decoding...`); // Log found

      // Validate refresh token format before using
      try {
        jwtDecode(refreshToken);
        console.log('[refreshToken] Refresh token format valid.'); // Log valid format
      } catch (tokenError) {
        console.error('[refreshToken] Invalid refresh token format. Clearing tokens & returning false:', tokenError); // Log invalid format
        await clearAuthTokens();
        return false;
      }
      
      console.log(`[refreshToken] Attempting authApi.post('token/refresh/')...`); // Log refresh attempt
      const response = await authApi.post('token/refresh/', {
        json: { refresh: refreshToken }
      }).json<{ access: string }>();
      console.log('[refreshToken] Refresh API call successful. New access token received.'); // Log refresh success

      await clientCookieStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, response.access);
      console.log('[refreshToken] New access token stored. Returning true.'); // Log store success
      return true;
    } catch (error) {
      console.error('[refreshToken] Refresh failed during API call or processing. Clearing tokens & returning false:', error); // Log refresh fail
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
    await api.post('auth/change-password/', {
      json: {
        old_password: oldPassword,
        new_password: newPassword,
      },
    });
  },
};

// Prefetch user on module load to speed up initial authentication
if (typeof window !== 'undefined') {
  // Schedule prefetching after the module loads
  console.log('[AuthService] Scheduling immediate user prefetch');
  setTimeout(() => {
    authService.getCurrentUser()
      .then(user => {
        console.log('[AuthService] Initial user prefetch complete:', user ? 'Authenticated' : 'Not authenticated');
      })
      .catch(error => {
        console.error('[AuthService] Initial user prefetch failed:', error);
      });
  }, 0);
}

const refreshAuthToken = async () => {
  const refreshToken = await clientCookieStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch('/auth/token/refresh/', {
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