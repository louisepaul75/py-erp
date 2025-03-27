import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUser, useLogin, useLogout, useUpdateProfile, useIsAuthenticated } from '@/lib/auth/authHooks';
import { authService } from '@/lib/auth/authService';
import { User, LoginCredentials } from '@/lib/auth/authTypes';
import { I18nextProvider } from 'react-i18next';
import mockI18n from '../../__mocks__/i18nMock';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock auth service
jest.mock('@/lib/auth/authService', () => ({
  authService: {
    getCurrentUser: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
    updateProfile: jest.fn(),
  },
}));

describe('Auth Hooks', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    });
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  const createWrapper = () => {
    return ({ children }: { children: React.ReactNode }) => (
      <I18nextProvider i18n={mockI18n}>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </I18nextProvider>
    );
  };

  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    name: 'Test User',
  };

  describe('useUser', () => {
    it('should fetch current user', async () => {
      // Mock authService response
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
      
      const wrapper = createWrapper();
      const { result } = renderHook(() => useUser(), { wrapper });

      // Initial state should be loading
      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();

      // Wait for the query to resolve
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      // Verify data is loaded
      expect(result.current.isLoading).toBe(false);
      expect(result.current.data).toEqual(mockUser);
    });

    it('should handle null user (not authenticated)', async () => {
      // Mock authService response for not authenticated
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(null);
      
      const wrapper = createWrapper();
      const { result } = renderHook(() => useUser(), { wrapper });

      // Wait for the query to resolve
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      // Verify null user is handled
      expect(result.current.data).toBeNull();
    });
  });

  describe('useLogin', () => {
    it('should call login service and set user data on success', async () => {
      // Mock authService login response
      (authService.login as jest.Mock).mockResolvedValue(mockUser);
      
      const wrapper = createWrapper();
      const { result } = renderHook(() => useLogin(), { wrapper });

      // Initial state
      expect(result.current.isPending).toBe(false);

      // Call login mutation
      await act(async () => {
        await result.current.mutate({ email: 'test@example.com', password: 'password' });
      });

      // Verify successful login
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      });
      expect(result.current.isPending).toBe(false);
    });

    it('should handle login error', async () => {
      // Mock authService login error
      const mockError = new Error('Invalid credentials');
      (authService.login as jest.Mock).mockRejectedValue(mockError);
      
      const wrapper = createWrapper();
      const { result } = renderHook(() => useLogin(), { wrapper });

      // Call login mutation
      let error: Error | null = null;
      await act(async () => {
        try {
          await result.current.mutate({ email: 'test@example.com', password: 'wrong' });
        } catch (e) {
          error = e as Error;
        }
      });

      // Verify error handling
      expect(error?.message).toBe('Invalid credentials');
      expect(result.current.isPending).toBe(false);
    });
  });

  describe('useLogout', () => {
    it('should call logout service', async () => {
      // Mock authService logout response
      (authService.logout as jest.Mock).mockResolvedValue(undefined);
      
      const wrapper = createWrapper();
      const { result } = renderHook(() => useLogout(), { wrapper });

      // Call logout mutation
      await act(async () => {
        await result.current.mutate();
      });
      
      // Verify logout was called
      expect(authService.logout).toHaveBeenCalledTimes(1);
      
      // Verify mutation is no longer pending
      expect(result.current.isPending).toBe(false);
    });
  });

  describe('useUpdateProfile', () => {
    it('should update profile successfully', async () => {
      const updatedUser = { ...mockUser, name: 'Updated Name' };
      
      // Mock authService updateProfile response
      (authService.updateProfile as jest.Mock).mockResolvedValue(updatedUser);
      
      const wrapper = createWrapper();
      const { result } = renderHook(() => useUpdateProfile(), { wrapper });

      // Call update profile mutation
      await act(async () => {
        await result.current.mutate({ name: 'Updated Name' });
      });

      // Verify update was called with correct data
      expect(authService.updateProfile).toHaveBeenCalledWith({ name: 'Updated Name' });
      expect(result.current.isPending).toBe(false);
    });
  });

  describe('useIsAuthenticated', () => {
    it('returns loading state initially', () => {
      (authService.getCurrentUser as jest.Mock).mockReturnValue(undefined);
      const wrapper = createWrapper();
      const { result } = renderHook(() => useIsAuthenticated(), { wrapper });
      expect(result.current.isLoading).toBe(true);
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBe(undefined);
    });

    it('returns authenticated state when user exists', async () => {
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

      const wrapper = createWrapper();
      const { result } = renderHook(() => useIsAuthenticated(), { wrapper });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockUser);
    });

    it('returns unauthenticated state when no user exists', async () => {
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(null);

      const wrapper = createWrapper();
      const { result } = renderHook(() => useIsAuthenticated(), { wrapper });

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
    });
  });
}); 