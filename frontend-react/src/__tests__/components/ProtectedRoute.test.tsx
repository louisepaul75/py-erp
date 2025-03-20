import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useIsAuthenticated } from '@/lib/auth/authHooks';

// Mock the auth hooks
jest.mock('@/lib/auth/authHooks', () => ({
  useIsAuthenticated: jest.fn(),
}));

// Mock the LoadingSpinner component
jest.mock('@/components/ui/LoadingSpinner', () => ({
  LoadingSpinner: () => <div data-testid="loading-spinner">Loading...</div>,
}));

// Create a mock for next/router
const mockPush = jest.fn();
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: mockPush,
    asPath: '/protected-page',
  }),
}));

describe('ProtectedRoute Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children when user is authenticated', () => {
    // Mock the auth hook to return authenticated user
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <ProtectedRoute>
        <div data-testid="protected-content">Protected Content</div>
      </ProtectedRoute>
    );

    // Check if protected content is rendered
    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    // Loading spinner should not be present
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
  });

  it('renders loading spinner when authentication status is loading', () => {
    // Mock the auth hook to return loading state
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: true,
    });

    render(
      <ProtectedRoute>
        <div data-testid="protected-content">Protected Content</div>
      </ProtectedRoute>
    );

    // Check if loading spinner is rendered
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    // Protected content should not be present
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  it('does not render children when user is not authenticated', () => {
    // Mock the auth hook to return unauthenticated user
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
    });

    const { container } = render(
      <ProtectedRoute>
        <div data-testid="protected-content">Protected Content</div>
      </ProtectedRoute>
    );

    // Check if protected content is not rendered
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    // Loading spinner should not be present
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    // Container should be empty
    expect(container.innerHTML).toBe('');
  });

  it('redirects to login page when user is not authenticated', () => {
    // Mock the auth hook to return unauthenticated user
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
    });

    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );

    // Verify that router.push was called with correct arguments
    expect(mockPush).toHaveBeenCalledWith({
      pathname: '/login',
      query: { from: '/protected-page' },
    });
  });
}); 