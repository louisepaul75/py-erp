import React from 'react';
import { render, screen } from '@testing-library/react';
import Dashboard from '@/components/ui/dashboard';

// Mock useRouter hook
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    pathname: '/dashboard',
    events: {
      on: jest.fn(),
      off: jest.fn(),
      emit: jest.fn(),
    },
  })),
  usePathname: jest.fn().mockReturnValue('/dashboard'),
  useSearchParams: jest.fn().mockReturnValue(new URLSearchParams())
}));

// Mock react-grid-layout since it uses complicated DOM manipulations
jest.mock('react-grid-layout', () => ({
  Responsive: jest.fn(({ children }) => <div data-testid="responsive-grid">{children}</div>),
  __esModule: true,
}));

// Mock Next.js Link component
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href} data-testid="next-link">
      {children}
    </a>
  );
});

// Mock API calls
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ 
      layouts: {
        lg: [],
        md: [],
        sm: []
      },
      menuTiles: []
    }),
  })
) as jest.Mock;

// Mock the auth service
jest.mock('@/lib/auth/authService', () => ({
  authService: {
    getToken: jest.fn().mockReturnValue('test-token'),
  },
}));

describe('Dashboard Component', () => {
  it('renders without crashing', () => {
    render(<Dashboard />);
    // Simply verify the component renders without throwing an error
    expect(document.body).toBeTruthy();
  });
}); 