import React from 'react';
import { render, screen } from '@testing-library/react';
import Home from '../../app/page';
import { authService } from '@/lib/auth/authService';

// Mock the auth service
jest.mock('@/lib/auth/authService', () => ({
  authService: {
    getCurrentUser: jest.fn()
  }
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn()
  })
}));

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render loading state initially', () => {
    render(<Home />);
    // The loading spinner should be present
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('should redirect to dashboard when authenticated', async () => {
    const mockRouter = { push: jest.fn() };
    (require('next/navigation') as any).useRouter = () => mockRouter;
    
    // Mock user is authenticated
    (authService.getCurrentUser as jest.Mock).mockResolvedValueOnce({ id: '1', name: 'Test User' });
    
    render(<Home />);
    
    // Wait for the redirect
    await screen.findByRole('status');
    expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
  });

  it('should redirect to login when not authenticated', async () => {
    const mockRouter = { push: jest.fn() };
    (require('next/navigation') as any).useRouter = () => mockRouter;
    
    // Mock user is not authenticated
    (authService.getCurrentUser as jest.Mock).mockResolvedValueOnce(null);
    
    render(<Home />);
    
    // Wait for the redirect
    await screen.findByRole('status');
    expect(mockRouter.push).toHaveBeenCalledWith('/login');
  });
}); 