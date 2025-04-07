import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useIsAuthenticated } from '@/lib/auth/authHooks';
import { useRouter, usePathname } from 'next/navigation';
import { MemoryRouterProvider } from 'next-router-mock/MemoryRouterProvider';
import { useAuth } from '@/hooks/useAuth';

// Mock the auth hooks
jest.mock('@/lib/auth/authHooks', () => ({
  useIsAuthenticated: jest.fn(),
}));

// Mock Next.js navigation hooks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn().mockImplementation(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
  })),
  usePathname: jest.fn().mockReturnValue('/protected-page'),
}));

// Mock the LoadingSpinner component
jest.mock('@/components/ui/LoadingSpinner', () => ({
  LoadingSpinner: () => <div data-testid="loading-spinner">Loading...</div>,
}));

describe('ProtectedRoute Component', () => {
  const mockUseIsAuthenticated = useIsAuthenticated as jest.Mock;
  const mockUseRouter = useRouter as jest.Mock;
  const mockUsePathname = usePathname as jest.Mock;

  beforeEach(() => {
    mockUseIsAuthenticated.mockClear();
    mockUseRouter.mockClear();
    mockUsePathname.mockClear();
    
    // Set default path
    mockUsePathname.mockReturnValue('/protected-page');
    
    // Set default router implementation
    mockUseRouter.mockImplementation(() => ({
      push: jest.fn(),
      replace: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
    }));
  });

  it('renders children when user is authenticated', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: true, isLoading: false });

    render(
      <ProtectedRoute>
        <div data-testid="child-component">Protected Content</div>
      </ProtectedRoute>
    );

    expect(screen.getByTestId('child-component')).toBeInTheDocument();
  });

  it('does not render children when user is not authenticated', () => {
    mockUseIsAuthenticated.mockReturnValue({ isAuthenticated: false, isLoading: false });
    
    const { queryByTestId } = render(
      <ProtectedRoute>
        <div data-testid="child-component">Protected Content</div>
      </ProtectedRoute>
    );

    // Children should not be rendered
    expect(queryByTestId('child-component')).not.toBeInTheDocument();
    
    // Verify router.push was called with the correct redirect URL
    const mockRouter = mockUseRouter.mock.results[0].value;
    expect(mockRouter.push).toHaveBeenCalledWith('/login?from=%2Fprotected-page');
  });
}); 