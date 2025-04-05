import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useIsAuthenticated } from '@/lib/auth/authHooks';
import { useRouter } from 'next/navigation';
import { MemoryRouterProvider } from 'next-router-mock/MemoryRouterProvider';
import { useAuth } from '@/hooks/useAuth';

// Mock the auth hooks
jest.mock('@/lib/auth/authHooks', () => ({
  useIsAuthenticated: jest.fn(),
}));

// Mock the LoadingSpinner component
jest.mock('@/components/ui/LoadingSpinner', () => ({
  LoadingSpinner: () => <div data-testid="loading-spinner">Loading...</div>,
}));

describe.skip('ProtectedRoute Component', () => {
  const mockUseIsAuthenticated = useIsAuthenticated as jest.Mock;

  beforeEach(() => {
    mockUseIsAuthenticated.mockClear();
    // Reset the router mock state before each test
    const router = require('next-router-mock');
    router.memoryRouter.setCurrentUrl("/"); // Reset to a default URL
  });

  it('renders children when user is authenticated', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: true, isLoading: false });

    render(
      <React.StrictMode>
        <MemoryRouterProvider>
          <ProtectedRoute>
            <div data-testid="child-component">Protected Content</div>
          </ProtectedRoute>
        </MemoryRouterProvider>
      </React.StrictMode>
    );

    expect(screen.getByTestId('child-component')).toBeInTheDocument();
  });

  it('renders loading spinner when authentication status is loading', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: false, isLoading: true });

    render(
      <React.StrictMode>
        <MemoryRouterProvider>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </MemoryRouterProvider>
      </React.StrictMode>
    );

    // Assuming you have a specific test ID or role for the loading spinner
    expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument(); 
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('does not render children when user is not authenticated', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: false, isLoading: false });
    
    const { queryByTestId } = render(
      <React.StrictMode>
        <MemoryRouterProvider url="/protected-page">
          <ProtectedRoute>
            <div data-testid="child-component">Protected Content</div>
          </ProtectedRoute>
        </MemoryRouterProvider>
      </React.StrictMode>
    );

    // Children should not be rendered
    expect(queryByTestId('child-component')).not.toBeInTheDocument();
  });

  it('redirects to login page when user is not authenticated', async () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: false, isLoading: false });
    
    const router = require('next-router-mock');
    // Spy on the push method of the *memoryRouter instance*
    // Adjust the path ('memoryRouter.push') if the instance is exposed differently
    const pushSpy = jest.spyOn(router.memoryRouter || router, 'push');

    render(
      <React.StrictMode>
        <MemoryRouterProvider url="/protected-page">
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </MemoryRouterProvider>
      </React.StrictMode>
    );

    await waitFor(() => {
      expect(pushSpy).toHaveBeenCalledWith('/login?redirect=/protected-page');
    });

    pushSpy.mockRestore(); // Clean up the spy
  });
}); 