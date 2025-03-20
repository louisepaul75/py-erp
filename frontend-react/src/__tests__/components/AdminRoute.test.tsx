import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AdminRoute } from '@/components/auth/AdminRoute';
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
    asPath: '/admin-page',
  }),
}));

describe('AdminRoute Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children when user is admin', () => {
    // Mock the auth hook to return authenticated admin user
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { isAdmin: true },
    });

    render(
      <AdminRoute>
        <div data-testid="admin-content">Admin Content</div>
      </AdminRoute>
    );

    // Check if admin content is rendered
    expect(screen.getByTestId('admin-content')).toBeInTheDocument();
    // Loading spinner should not be present
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
  });

  it('renders loading spinner when authentication status is loading', () => {
    // Mock the auth hook to return loading state
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: true,
      user: null,
    });

    render(
      <AdminRoute>
        <div data-testid="admin-content">Admin Content</div>
      </AdminRoute>
    );

    // Check if loading spinner is rendered
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    // Admin content should not be present
    expect(screen.queryByTestId('admin-content')).not.toBeInTheDocument();
  });

  it('does not render children when user is authenticated but not admin', () => {
    // Mock the auth hook to return authenticated non-admin user
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { isAdmin: false },
    });

    const { container } = render(
      <AdminRoute>
        <div data-testid="admin-content">Admin Content</div>
      </AdminRoute>
    );

    // Check if admin content is not rendered
    expect(screen.queryByTestId('admin-content')).not.toBeInTheDocument();
    // Loading spinner should not be present
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    // Container should be empty
    expect(container.innerHTML).toBe('');
  });

  it('does not render children when user is not authenticated', () => {
    // Mock the auth hook to return unauthenticated user
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      isLoading: false,
      user: null,
    });

    const { container } = render(
      <AdminRoute>
        <div data-testid="admin-content">Admin Content</div>
      </AdminRoute>
    );

    // Check if admin content is not rendered
    expect(screen.queryByTestId('admin-content')).not.toBeInTheDocument();
    // Loading spinner should not be present
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    // Container should be empty
    expect(container.innerHTML).toBe('');
  });

  it('redirects to unauthorized page when user is not admin', () => {
    // Mock the auth hook to return authenticated non-admin user
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { isAdmin: false },
    });

    render(
      <AdminRoute>
        <div>Admin Content</div>
      </AdminRoute>
    );

    // Verify that router.push was called with correct arguments
    expect(mockPush).toHaveBeenCalledWith('/unauthorized');
  });
}); 