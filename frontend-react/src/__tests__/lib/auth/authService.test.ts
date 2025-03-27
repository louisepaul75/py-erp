import { authService } from '@/lib/auth/authService';
import { User, LoginCredentials } from '@/lib/auth/authTypes';
import { HTTPError } from 'ky';

// Mock ky
const mockKy = {
  get: jest.fn(),
  post: jest.fn(),
  patch: jest.fn(),
  extend: jest.fn().mockReturnThis(),
  create: jest.fn().mockReturnThis(),
};

// Mock next/headers
jest.mock('next/headers', () => ({
  cookies: () => ({
    get: jest.fn(),
    set: jest.fn(),
    delete: jest.fn(),
  }),
}));

// Mock ky
jest.mock('ky', () => ({
  __esModule: true,
  default: mockKy,
  HTTPError: class HTTPError extends Error {
    response: any;
    request: any;
    constructor(response: any, request: any, options: any) {
      super('HTTP Error');
      this.response = response;
      this.request = request;
    }
  },
}));

describe('Auth Service', () => {
  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    name: 'Test User',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Clear cookies
    document.cookie = '';
  });

  describe('getCurrentUser', () => {
    it('should return user when authenticated', async () => {
      mockKy.get.mockResolvedValueOnce({
        json: () => Promise.resolve(mockUser),
      });

      const user = await authService.getCurrentUser();
      expect(user).toEqual(mockUser);
      expect(mockKy.get).toHaveBeenCalledWith('auth/user/');
    });

    it('should return null when not authenticated', async () => {
      mockKy.get.mockRejectedValueOnce(
        new HTTPError(
          { status: 401, text: () => Promise.resolve('Unauthorized') },
          { url: 'auth/user/' },
          {}
        )
      );

      const user = await authService.getCurrentUser();
      expect(user).toBeNull();
    });

    it('should throw error for other errors', async () => {
      mockKy.get.mockRejectedValueOnce(
        new HTTPError(
          { status: 500, text: () => Promise.resolve('Server Error') },
          { url: 'auth/user/' },
          {}
        )
      );

      await expect(authService.getCurrentUser()).rejects.toThrow();
    });
  });

  describe('login', () => {
    const credentials: LoginCredentials = {
      email: 'test@example.com',
      password: 'password',
    };

    it('should login successfully', async () => {
      const mockResponse = {
        user: mockUser,
        access: 'access_token',
        refresh: 'refresh_token',
      };

      mockKy.post.mockResolvedValueOnce({
        json: () => Promise.resolve(mockResponse),
      });

      const user = await authService.login(credentials);
      expect(user).toEqual(mockUser);
      expect(mockKy.post).toHaveBeenCalledWith('auth/login/', { json: credentials });
      
      // Check if tokens were stored in cookies
      expect(document.cookie).toContain('access_token');
      expect(document.cookie).toContain('refresh_token');
    });

    it('should handle login error', async () => {
      mockKy.post.mockRejectedValueOnce(
        new HTTPError(
          { status: 401, text: () => Promise.resolve('Invalid credentials') },
          { url: 'auth/login/' },
          {}
        )
      );

      await expect(authService.login(credentials)).rejects.toThrow();
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      mockKy.post.mockResolvedValueOnce({});

      await authService.logout();
      expect(mockKy.post).toHaveBeenCalledWith('auth/logout/');
      
      // Check if tokens were removed from cookies
      expect(document.cookie).not.toContain('access_token');
      expect(document.cookie).not.toContain('refresh_token');
    });

    it('should clear tokens even if logout request fails', async () => {
      mockKy.post.mockRejectedValueOnce(
        new HTTPError(
          { status: 500, text: () => Promise.resolve('Server Error') },
          { url: 'auth/logout/' },
          {}
        )
      );

      await authService.logout();
      expect(document.cookie).not.toContain('access_token');
      expect(document.cookie).not.toContain('refresh_token');
    });
  });

  describe('updateProfile', () => {
    const updateData = { name: 'Updated Name' };

    it('should update profile successfully', async () => {
      const updatedUser = { ...mockUser, ...updateData };
      mockKy.patch.mockResolvedValueOnce({
        json: () => Promise.resolve(updatedUser),
      });

      const result = await authService.updateProfile(updateData);
      expect(result).toEqual(updatedUser);
      expect(mockKy.patch).toHaveBeenCalledWith('auth/user/', { json: updateData });
    });

    it('should handle update error', async () => {
      mockKy.patch.mockRejectedValueOnce(
        new HTTPError(
          { status: 400, text: () => Promise.resolve('Invalid data') },
          { url: 'auth/user/' },
          {}
        )
      );

      await expect(authService.updateProfile(updateData)).rejects.toThrow();
    });
  });
}); 