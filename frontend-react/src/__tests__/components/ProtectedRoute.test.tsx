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

describe('ProtectedRoute Component', () => {
  const mockUseIsAuthenticated = useIsAuthenticated as jest.Mock;

  beforeEach(() => {
    mockUseIsAuthenticated.mockClear();
    // Reset the router mock state before each test
    // require('next-router-mock').memoryRouter.setCurrentUrl("/"); // No longer needed for this test
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
}); 