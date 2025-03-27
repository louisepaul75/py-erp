import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import i18n from '../__mocks__/i18nMock';
import { useUser, useLogin, useLogout, useIsAuthenticated } from '@/lib/auth/authHooks';
import { authService } from '@/lib/auth/authService';

// Mock the auth service
jest.mock('@/lib/auth/authService', () => ({
  authService: {
    getCurrentUser: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
  }
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0
      }
    }
  });
  
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        {children}
      </I18nextProvider>
    </QueryClientProvider>
  );
};

describe('Auth Hooks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useUser', () => {
    it('should fetch current user', async () => {
      const mockUser = { id: 1, username: 'testuser' };
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

      const wrapper = createWrapper();
      const { result, waitFor } = renderHook(() => useUser(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toEqual(mockUser);
      });
    });

    it('should handle null user (not authenticated)', async () => {
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(null);

      const wrapper = createWrapper();
      const { result, waitFor } = renderHook(() => useUser(), { wrapper });

      await waitFor(() => {
        expect(result.current.data).toBeNull();
      });
    });
  });

  describe('useLogin', () => {
    it('should call login service and set user data on success', async () => {
      const mockUser = { id: 1, username: 'testuser' };
      (authService.login as jest.Mock).mockResolvedValue(mockUser);

      const wrapper = createWrapper();
      const { result, waitFor } = renderHook(() => useLogin(), { wrapper });

      await act(async () => {
        result.current.mutate({ username: 'testuser', password: 'password' });
      });

      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith({
          username: 'testuser',
          password: 'password'
        });
      });
    });

    it('should handle login error', async () => {
      const mockError = new Error('Invalid credentials');
      (authService.login as jest.Mock).mockRejectedValue(mockError);

      const wrapper = createWrapper();
      const { result, waitFor } = renderHook(() => useLogin(), { wrapper });

      await act(async () => {
        result.current.mutate({ username: 'testuser', password: 'wrong' });
      });

      await waitFor(() => {
        expect(result.current.error).toBeTruthy();
      });
    });
  });

  describe('useLogout', () => {
    it('should call logout service', async () => {
      (authService.logout as jest.Mock).mockResolvedValue(undefined);

      const wrapper = createWrapper();
      const { result, waitFor } = renderHook(() => useLogout(), { wrapper });

      await act(async () => {
        result.current.mutate();
      });

      await waitFor(() => {
        expect(authService.logout).toHaveBeenCalled();
      });
    });
  });

  describe('useIsAuthenticated', () => {
    it('should return authenticated=true when user exists', async () => {
      const mockUser = { id: 1, username: 'testuser' };
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

      const wrapper = createWrapper();
      const { result, waitFor } = renderHook(() => useIsAuthenticated(), { wrapper });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
        expect(result.current.user).toEqual(mockUser);
      });
    });

    it('should return authenticated=false when user is null', async () => {
      (authService.getCurrentUser as jest.Mock).mockResolvedValue(null);

      const wrapper = createWrapper();
      const { result, waitFor } = renderHook(() => useIsAuthenticated(), { wrapper });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(false);
        expect(result.current.user).toBeNull();
      });
    });
  });
}); 