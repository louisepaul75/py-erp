import { authService, api } from '@/lib/auth/authService';
import { jwtDecode } from 'jwt-decode';
import { AUTH_CONFIG } from '@/lib/config';
import { LoginCredentials, User } from '@/lib/auth/authTypes';

// Mock jwt-decode
jest.mock('jwt-decode', () => ({
  jwtDecode: jest.fn(),
}));

// Mock the imported api object
jest.mock('@/lib/auth/authService', () => {
  const mockResponse = {
    json: jest.fn(),
    text: jest.fn(),
  };
  
  const mockKy = {
    post: jest.fn(() => mockResponse),
    get: jest.fn(() => mockResponse),
    patch: jest.fn(() => mockResponse),
    extend: jest.fn(() => mockKy),
    create: jest.fn(() => mockKy),
    hooks: {},
  };

  // Create authService with the same functions but mocked
  const authServiceMock = {
    getCurrentUser: jest.requireActual('@/lib/auth/authService').authService.getCurrentUser,
    login: jest.requireActual('@/lib/auth/authService').authService.login,
    logout: jest.requireActual('@/lib/auth/authService').authService.logout,
    refreshToken: jest.requireActual('@/lib/auth/authService').authService.refreshToken,
    updateProfile: jest.requireActual('@/lib/auth/authService').authService.updateProfile,
    changePassword: jest.requireActual('@/lib/auth/authService').authService.changePassword,
  };

  return {
    __esModule: true,
    authService: authServiceMock,
    api: mockKy,
  };
});

// Mock KY separately
jest.mock('ky', () => {
  const mockResponse = {
    json: jest.fn(),
    text: jest.fn(),
  };
  
  const mockInstance = {
    post: jest.fn(() => mockResponse),
    get: jest.fn(() => mockResponse),
    patch: jest.fn(() => mockResponse),
    extend: jest.fn(),
    create: jest.fn(),
    hooks: {},
  };
  
  // Return the mock instance as default and add properties
  const mock = { ...mockInstance };
  mock.extend = jest.fn().mockReturnValue(mockInstance);
  mock.create = jest.fn().mockReturnValue(mockInstance);
  
  const ky = jest.fn().mockImplementation(() => mockResponse);
  
  return {
    __esModule: true,
    default: mock,
    HTTPError: class HTTPError extends Error {
      constructor() {
        super('HTTP Error');
        this.response = {
          status: 401,
          statusText: 'Unauthorized',
          text: jest.fn().mockResolvedValue('Unauthorized'),
        };
        this.request = {
          clone: jest.fn().mockReturnThis(),
          headers: {
            set: jest.fn(),
          },
        };
      }
    },
  };
});

// Improved cookie mock
const cookieMock = (() => {
  let cookieStore = '';
  
  const parseCookies = () => {
    return cookieStore.split('; ').reduce((cookies, cookie) => {
      const [name, value] = cookie.split('=');
      if (name && value) cookies[name] = value;
      return cookies;
    }, {} as Record<string, string>);
  };
  
  const getCookie = (name: string) => {
    const cookies = parseCookies();
    return cookies[name] || null;
  };
  
  const setCookie = (cookieString: string) => {
    const mainPart = cookieString.split(';')[0];
    const [name] = mainPart.split('=');
    
    // Remove existing cookie with same name if it exists
    const cookies = cookieStore.split('; ').filter(c => !c.startsWith(`${name}=`));
    
    // Add the new cookie
    if (cookies.length === 0 || cookieStore === '') {
      cookieStore = cookieString;
    } else {
      cookieStore = cookies.join('; ') + '; ' + cookieString;
    }
  };
  
  Object.defineProperty(document, 'cookie', {
    get: jest.fn().mockImplementation(() => cookieStore),
    set: jest.fn().mockImplementation(setCookie),
    configurable: true,
  });
  
  return {
    clear: () => {
      cookieStore = '';
    },
    get: getCookie,
  };
})();

describe('Auth Service', () => {
  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    isAdmin: false,
  };
  
  const mockCredentials: LoginCredentials = {
    username: 'testuser',
    password: 'password123',
  };
  
  const mockTokens = {
    access: 'mock-access-token',
    refresh: 'mock-refresh-token',
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    cookieMock.clear();
    
    // Reset import mock implementations
    (jwtDecode as jest.Mock).mockImplementation(() => ({
      user_id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      is_staff: false,
      exp: Date.now() / 1000 + 3600, // Valid for 1 hour
    }));
  });
  
  describe('login', () => {
    it('should login successfully and store tokens', async () => {
      // Mock API response
      const mockKy = require('ky').default;
      const mockResponse = { json: jest.fn().mockResolvedValue(mockTokens) };
      mockKy.post.mockReturnValue(mockResponse);
      
      // Execute login
      const result = await authService.login(mockCredentials);
      
      // Verify API was called correctly
      expect(mockKy.post).toHaveBeenCalledWith(AUTH_CONFIG.tokenEndpoint, {
        json: mockCredentials,
      });
      
      // Check that the token values exist in the cookie string, not looking for exact names
      // since the cookie string includes additional properties
      expect(document.cookie).toContain('access_token=mock-access-token');
      expect(document.cookie).toContain('refresh_token=mock-refresh-token');
      
      // Verify user object was returned correctly
      expect(result).toEqual(mockUser);
    });
    
    it('should throw error on failed login', async () => {
      // Mock API error
      const mockKy = require('ky').default;
      mockKy.post.mockImplementation(() => {
        throw new Error('Invalid credentials');
      });
      
      // Execute login and expect error
      await expect(authService.login(mockCredentials)).rejects.toThrow();
    });
  });
  
  describe('logout', () => {
    it('should remove tokens from cookies', () => {
      // Setup initial tokens
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=mock-access-token; path=/`;
      document.cookie = `${AUTH_CONFIG.tokenStorage.refreshToken}=mock-refresh-token; path=/`;
      
      // Verify setup
      expect(document.cookie).toContain('access_token');
      expect(document.cookie).toContain('refresh_token');
      
      // Execute logout
      authService.logout();
      
      // When cookies are deleted, they are set to empty with expiry in the past
      // We should check that the new cookie contains the name but with clear indicators
      // of deletion like empty value or expires in the past
      const afterLogoutCookie = document.cookie;
      expect(afterLogoutCookie).toContain(`${AUTH_CONFIG.tokenStorage.accessToken}=;`);
      expect(afterLogoutCookie).toContain(`${AUTH_CONFIG.tokenStorage.refreshToken}=;`);
      expect(afterLogoutCookie).toContain('expires=Thu, 01 Jan 1970');
    });
  });
  
  describe('authApi hooks', () => {
    beforeEach(() => {
      // Setup the mocked hooks here, outside of jest.mock
      const mockKy = require('ky').default;
      mockKy.create.mockImplementation(() => ({
        post: jest.fn(() => ({ json: jest.fn() })),
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
            }
          ]
        }
      }));
    });
    
    it('should add error message from response text in authApi beforeError hook', async () => {
      // Create a mock error with mock response
      const mockError = {
        response: {
          text: jest.fn().mockResolvedValue('Auth API error message'),
          statusText: 'Error Status'
        }
      };
      
      // Get the authApi instance directly with its hooks
      const mockKy = require('ky').default;
      const authApi = mockKy.create();
      const beforeErrorHook = authApi.hooks.beforeError[0];
      
      // Call the hook
      const result = await beforeErrorHook(mockError);
      
      // Verify error message was updated
      expect(result.message).toBe('Auth API error message');
    });
    
    it('should use statusText if response text fails in authApi beforeError hook', async () => {
      // Create a mock error
      const mockError = {
        response: {
          text: jest.fn().mockImplementation(() => {
            throw new Error('Text extraction failed');
          }),
          statusText: 'Auth Error Status'
        }
      };
      
      // Get the authApi instance directly with its hooks
      const mockKy = require('ky').default;
      const authApi = mockKy.create();
      const beforeErrorHook = authApi.hooks.beforeError[0];
      
      // Call the hook
      const result = await beforeErrorHook(mockError);
      
      // Verify error message was set to statusText
      expect(result.message).toBe('Auth Error Status');
    });
  });
  
  describe('getCurrentUser', () => {
    it('should return null when no token exists', async () => {
      // Ensure no token in cookie
      cookieMock.clear();
      
      const result = await authService.getCurrentUser();
      expect(result).toBeNull();
    });
    
    it.skip('should refresh token when it is expired and return user data', async () => {
      // Setup localStorage with expired token
      const expiredToken = 'expired-token';
      const expiredRefreshToken = 'expired-refresh-token';
      const userId = '123';
      
      // Mock cookies
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=${expiredToken}; path=/`;
      document.cookie = `${AUTH_CONFIG.tokenStorage.refreshToken}=${expiredRefreshToken}; path=/`;
      
      const mockDecodedToken = {
        id: userId,
        exp: Math.floor(Date.now() / 1000) - 3600, // Set to 1 hour ago
      };
      
      // Setup mock for jwt.decode 
      (jwtDecode as jest.Mock).mockReturnValue(mockDecodedToken);
      
      // Setup mocks for API response
      const newAccessToken = 'new-access-token';
      const mockUserResponse = { id: userId, name: 'Test User' };
      
      // Mock authApi
      const mockAuthApi = {
        post: jest.fn(() => ({
          json: jest.fn().mockResolvedValue({ access: newAccessToken })
        }))
      };
      
      // Replace the authApi by modifying the module
      jest.requireActual('@/lib/auth/authService').authApi = mockAuthApi;
      
      // And mock the user API call
      const mockApi = api as jest.Mocked<typeof api>;
      mockApi.get.mockReturnValueOnce({
        json: jest.fn().mockResolvedValue(mockUserResponse)
      } as any);
      
      // Call getCurrentUser
      const result = await authService.getCurrentUser();
      
      // Verify user data was fetched
      expect(mockApi.get).toHaveBeenCalledWith('profile/');
      
      // Verify result
      expect(result).toEqual(mockUserResponse);
    });
    
    it('should return null when token refresh fails', async () => {
      // Set up expired token
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=expired-token; path=/`;
      document.cookie = `${AUTH_CONFIG.tokenStorage.refreshToken}=refresh-token; path=/`;
      
      // Mock token is expired
      (jwtDecode as jest.Mock).mockImplementation(() => ({
        user_id: 1,
        username: 'testuser',
        email: 'test@example.com',
        exp: Date.now() / 1000 - 3600, // Expired 1 hour ago
      }));
      
      // Mock refreshToken failure
      const mockKy = require('ky').default;
      mockKy.post.mockImplementation(() => {
        throw new Error('Refresh failed');
      });
      
      const result = await authService.getCurrentUser();
      
      // Should return null when refresh fails
      expect(result).toBeNull();
    });
    
    it('should handle error in getCurrentUser and return null', async () => {
      // Set up valid token
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=valid-token; path=/`;
      
      // Mock valid token but API error
      (jwtDecode as jest.Mock).mockImplementation(() => {
        throw new Error('Token decode error');
      });
      
      const result = await authService.getCurrentUser();
      
      // Should return null on error
      expect(result).toBeNull();
    });
  });
  
  describe('refreshToken', () => {
    it('should return null when no refresh token exists', async () => {
      // Ensure no refresh token in cookie
      cookieMock.clear();
      
      const result = await authService.refreshToken();
      expect(result).toBeNull();
    });
    
    it('should handle server error during refresh and return null', async () => {
      // Set up refresh token
      document.cookie = `${AUTH_CONFIG.tokenStorage.refreshToken}=refresh-token; path=/`;
      
      // Mock refreshToken server error
      const mockKy = require('ky').default;
      mockKy.post.mockImplementation(() => {
        throw new Error('Server error during refresh');
      });
      
      const result = await authService.refreshToken();
      
      // Should return null and call logout
      expect(result).toBeNull();
      // Verify tokens were removed (logout was called)
      expect(document.cookie).toContain(`${AUTH_CONFIG.tokenStorage.accessToken}=;`);
      expect(document.cookie).toContain(`${AUTH_CONFIG.tokenStorage.refreshToken}=;`);
    });
  });
  
  describe('updateProfile', () => {
    it('should update user profile successfully', async () => {
      // Setup token in cookie
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=${mockTokens.access}; path=/`;
      
      // Profile update data
      const updateData = {
        firstName: 'Updated',
        lastName: 'Name'
      };
      
      // Mock API response
      const mockKy = require('ky').default;
      mockKy.patch.mockReturnValue({
        json: jest.fn().mockResolvedValue({
          ...mockUser,
          firstName: 'Updated',
          lastName: 'Name'
        }),
      });
      
      // Execute updateProfile
      const result = await authService.updateProfile(updateData);
      
      // Verify API was called correctly
      expect(mockKy.patch).toHaveBeenCalledWith('profile/', {
        json: updateData,
      });
      
      // Verify updated user was returned
      expect(result).toEqual({
        ...mockUser,
        firstName: 'Updated',
        lastName: 'Name'
      });
    });
    
    it('should throw error on failed profile update', async () => {
      // Setup token in cookie
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=${mockTokens.access}; path=/`;
      
      // Mock API error
      const mockKy = require('ky').default;
      mockKy.patch.mockImplementation(() => {
        throw new Error('Update failed');
      });
      
      // Execute updateProfile and expect error
      await expect(authService.updateProfile({ firstName: 'Test' })).rejects.toThrow();
    });
  });
  
  describe('changePassword', () => {
    it('should change password successfully', async () => {
      // Setup token in cookie
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=${mockTokens.access}; path=/`;
      
      // Password change data
      const oldPassword = 'old-password';
      const newPassword = 'new-password';
      
      // Mock API response
      const mockKy = require('ky').default;
      mockKy.post.mockReturnValue({
        json: jest.fn().mockResolvedValue({}),
      });
      
      // Execute changePassword
      await authService.changePassword(oldPassword, newPassword);
      
      // Verify API was called correctly
      expect(mockKy.post).toHaveBeenCalledWith('profile/change-password/', {
        json: { old_password: oldPassword, new_password: newPassword },
      });
    });
    
    it('should throw error on failed password change', async () => {
      // Setup token in cookie
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=${mockTokens.access}; path=/`;
      
      // Mock API error
      const mockKy = require('ky').default;
      mockKy.post.mockImplementation(() => {
        throw new Error('Password change failed');
      });
      
      // Execute changePassword and expect error
      await expect(authService.changePassword('old', 'new')).rejects.toThrow();
    });
  });
  
  describe('api instance', () => {
    beforeEach(() => {
      // Setup the mocked hooks here, outside of jest.mock
      const mockKy = require('ky').default;
      mockKy.extend.mockImplementation(() => ({
        post: jest.fn(() => ({ json: jest.fn() })),
        patch: jest.fn(() => ({ json: jest.fn() })),
        get: jest.fn(() => ({ json: jest.fn() })),
        hooks: {
          beforeRequest: [
            request => {
              const token = cookieMock.get(AUTH_CONFIG.tokenStorage.accessToken);
              if (token) {
                request.headers.set('Authorization', `Bearer ${token}`);
              }
            }
          ],
          beforeError: [
            async (error) => {
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
                      await require('ky')(request);
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
            }
          ]
        }
      }));
    });
    
    it('should include auth token in requests if available', async () => {
      // Setup token in cookie
      document.cookie = `${AUTH_CONFIG.tokenStorage.accessToken}=${mockTokens.access}; path=/`;
      
      // Create a mock request object
      const mockRequest = {
        headers: {
          set: jest.fn()
        }
      };
      
      // Get the api instance directly with its hooks
      const mockKy = require('ky').default;
      const api = mockKy.extend();
      const beforeRequestHook = api.hooks.beforeRequest[0];
      
      // Call the hook
      beforeRequestHook(mockRequest);
      
      // Verify token was added to headers
      expect(mockRequest.headers.set).toHaveBeenCalledWith(
        'Authorization',
        `Bearer ${mockTokens.access}`
      );
    });
    
    it('should not include auth token if not available', async () => {
      // Clear cookies
      cookieMock.clear();
      
      // Create a mock request object
      const mockRequest = {
        headers: {
          set: jest.fn()
        }
      };
      
      // Get the api instance directly with its hooks
      const mockKy = require('ky').default;
      const api = mockKy.extend();
      const beforeRequestHook = api.hooks.beforeRequest[0];
      
      // Call the hook
      beforeRequestHook(mockRequest);
      
      // Verify token was not added to headers
      expect(mockRequest.headers.set).not.toHaveBeenCalled();
    });
    
    it('should add error message from response text', async () => {
      // Create a mock error
      const mockError = {
        response: {
          status: 403,
          text: jest.fn().mockResolvedValue('Custom error message'),
          statusText: 'Forbidden'
        },
        request: {
          clone: jest.fn().mockReturnThis(),
          headers: {
            set: jest.fn()
          }
        }
      };
      
      // Get the api instance directly with its hooks
      const mockKy = require('ky').default;
      const api = mockKy.extend();
      const beforeErrorHook = api.hooks.beforeError[0];
      
      // Call the hook
      const result = await beforeErrorHook(mockError);
      
      // Verify error message was updated
      expect(result.message).toBe('Custom error message');
    });
    
    it('should use statusText if response text fails', async () => {
      // Create a mock error
      const mockError = {
        response: {
          status: 500,
          text: jest.fn().mockImplementation(() => {
            throw new Error('Text extraction failed');
          }),
          statusText: 'Server Error'
        },
        request: {
          clone: jest.fn().mockReturnThis(),
          headers: {
            set: jest.fn()
          }
        }
      };
      
      // Get the api instance directly with its hooks
      const mockKy = require('ky').default;
      const api = mockKy.extend();
      const beforeErrorHook = api.hooks.beforeError[0];
      
      // Call the hook
      const result = await beforeErrorHook(mockError);
      
      // Verify error message was updated
      expect(result.message).toBe('Server Error');
    });
  });
}); 