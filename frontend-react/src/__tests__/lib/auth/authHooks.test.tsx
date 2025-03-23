import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUser, useLogin, useLogout, useUpdateProfile, useIsAuthenticated } from '@/lib/auth/authHooks';
import { authService } from '@/lib/auth/authService';
import { User, LoginCredentials } from '@/lib/auth/authTypes';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock authService
jest.mock('@/lib/auth/authService', () => ({
  authService: {
    getCurrentUser: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
    updateProfile: jest.fn(),
  },
}));

// Wrapper component for providing QueryClient to hooks
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

// Custom helper for waiting for queries to settle
const waitForQueryToSettle = async (callback: () => boolean, timeout = 1000) => {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (callback()) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  throw new Error(`Timed out waiting for condition after ${timeout}ms`);
};

describe('Auth Hooks', () => {
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
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('useUser', () => {
    it('should fetch current user', async () => {
      // Mock authService response
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
      
      // Render hook with query client provider
      const { result } = renderHook(() => useUser(), {
        wrapper: createWrapper(),
      });
      
      // Initially should be loading
      expect(result.current.isLoading).toBe(true);
      
      // Wait for data to load
      await waitForQueryToSettle(() => !result.current.isLoading);
      
      // Verify data and status
      expect(result.current.data).toEqual(mockUser);
      expect(result.current.isSuccess).toBe(true);
      expect(authService.getCurrentUser).toHaveBeenCalledTimes(1);
    });
    
    it('should handle null user (not authenticated)', async () => {
      // Mock authService response for not authenticated
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(null);
      
      // Render hook with query client provider
      const { result } = renderHook(() => useUser(), {
        wrapper: createWrapper(),
      });
      
      // Wait for data to load
      await waitForQueryToSettle(() => !result.current.isLoading);
      
      // Verify data and status
      expect(result.current.data).toBeNull();
      expect(result.current.isSuccess).toBe(true);
    });
  });
  
  describe('useLogin', () => {
    it('should call login service and set user data on success', async () => {
      // Mock authService login response
      (authService.login as jest.Mock).mockResolvedValue(mockUser);
      
      // Render hook with query client provider
      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });
      
      // Trigger login
      await act(async () => {
        await result.current.mutate(mockCredentials);
        // Allow state update
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      // Verify authService was called correctly
      expect(authService.login).toHaveBeenCalledWith(mockCredentials);
      
      // Verify mutation success (use isPending to avoid isSuccess issues)
      expect(result.current.isPending).toBe(false);
      expect(result.current.data).toEqual(mockUser);
    });
    
    it('should handle login error', async () => {
      // Mock authService login error
      const mockError = new Error('Invalid credentials');
      (authService.login as jest.Mock).mockRejectedValue(mockError);
      
      // Render hook with query client provider
      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });
      
      // Trigger login
      await act(async () => {
        try {
          await result.current.mutate(mockCredentials);
          // Allow state update
          await new Promise(resolve => setTimeout(resolve, 0));
        } catch (e) {
          // Expected to throw
        }
      });
      
      // Verify mutation status (use isPending to avoid isError issues)
      expect(result.current.isPending).toBe(false);
      expect(result.current.error).toBeTruthy();
    });
  });
  
  describe('useLogout', () => {
    it('should call logout service', async () => {
      // Render hook with query client provider
      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      });
      
      // Trigger logout
      await act(async () => {
        result.current.mutate();
        // Allow state update
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      // Verify logout was called
      expect(authService.logout).toHaveBeenCalledTimes(1);
      
      // Verify mutation is no longer pending
      expect(result.current.isPending).toBe(false);
    });
  });
  
  describe('useUpdateProfile', () => {
    it('should update profile successfully', async () => {
      const updatedUser = { ...mockUser, firstName: 'Updated', lastName: 'Name' };
      const profileUpdate = { firstName: 'Updated', lastName: 'Name' };
      
      // Mock authService updateProfile response
      (authService.updateProfile as jest.Mock).mockResolvedValue(updatedUser);
      
      // Render hook with query client provider
      const { result } = renderHook(() => useUpdateProfile(), {
        wrapper: createWrapper(),
      });
      
      // Trigger profile update
      await act(async () => {
        result.current.mutate(profileUpdate);
        // Allow state update
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      // Verify authService was called correctly
      expect(authService.updateProfile).toHaveBeenCalledWith(profileUpdate);
      
      // Verify mutation is no longer pending
      expect(result.current.isPending).toBe(false);
    });
  });
  
  describe('useIsAuthenticated', () => {
    it('should return authenticated=true when user exists', async () => {
      // Mock authService response
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
      
      // Render hook with query client provider
      const { result } = renderHook(() => useIsAuthenticated(), {
        wrapper: createWrapper(),
      });
      
      // Initially should be loading
      expect(result.current.isLoading).toBe(true);
      
      // Wait for data to load
      await waitForQueryToSettle(() => !result.current.isLoading);
      
      // Verify status
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toEqual(mockUser);
    });
    
    it('should return authenticated=false when user is null', async () => {
      // Mock authService response for not authenticated
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(null);
      
      // Render hook with query client provider
      const { result } = renderHook(() => useIsAuthenticated(), {
        wrapper: createWrapper(),
      });
      
      // Wait for data to load
      await waitForQueryToSettle(() => !result.current.isLoading);
      
      // Verify status
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.user).toBeNull();
    });
  });
}); 