import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useIsAuthenticated } from '@/lib/auth/authHooks';
import { useRouter } from 'next/navigation';
import { MemoryRouterProvider } from 'next-router-mock/MemoryRouterProvider';

// Mock the auth hooks
jest.mock('@/lib/auth/authHooks', () => ({
  useIsAuthenticated: jest.fn(),
}));

// Mock next/navigation - Keep this global mock as well
jest.mock('next/navigation', () => require('next-router-mock'));

// Mock the LoadingSpinner component
jest.mock('@/components/ui/LoadingSpinner', () => ({
  LoadingSpinner: () => <div data-testid="loading-spinner">Loading...</div>,
}));

describe('ProtectedRoute Component', () => {
  const mockUseIsAuthenticated = useIsAuthenticated as jest.Mock;
  const mockUseRouter = useRouter as jest.Mock;

  beforeEach(() => {
    mockUseIsAuthenticated.mockClear();
  });

  it('renders children when user is authenticated', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: true, isLoading: false });

    render(
      <MemoryRouterProvider>
        <ProtectedRoute>
          <div data-testid="child-component">Protected Content</div>
        </ProtectedRoute>
      </MemoryRouterProvider>
    );

    expect(screen.getByTestId('child-component')).toBeInTheDocument();
  });

  it('renders loading spinner when authentication status is loading', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: false, isLoading: true });

    render(
      <MemoryRouterProvider>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouterProvider>
    );

    // Assuming you have a specific test ID or role for the loading spinner
    expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument(); 
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('does not render children when user is not authenticated', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: false, isLoading: false });
    
    // Set up a mock implementation for useRouter needed for redirection check
    const mockRouterInstance = { push: jest.fn() };
    mockUseRouter.mockReturnValue(mockRouterInstance);

    const { queryByTestId } = render(
      <MemoryRouterProvider url="/protected-page">
        <ProtectedRoute>
          <div data-testid="child-component">Protected Content</div>
        </ProtectedRoute>
      </MemoryRouterProvider>
    );

    // Children should not be rendered
    expect(queryByTestId('child-component')).not.toBeInTheDocument();
  });

  it('redirects to login page when user is not authenticated', async () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: false, isLoading: false });
    
    // It's crucial to mock the router instance returned by the hook
    const mockRouterInstance = { push: jest.fn() };
    mockUseRouter.mockReturnValue(mockRouterInstance);

    render(
      // Wrap with MemoryRouterProvider to provide routing context
      <MemoryRouterProvider url="/protected-page">
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouterProvider>
    );

    // Use await act if the redirection happens asynchronously within useEffect
    await act(async () => {
      // Allow time for useEffect to potentially run
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // Check if router.push was called with the correct login path and query param
    expect(mockRouterInstance.push).toHaveBeenCalledWith('/login?redirect=/protected-page');
  });
}); 