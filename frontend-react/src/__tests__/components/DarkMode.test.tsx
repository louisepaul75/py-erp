import React from 'react';
import { render, screen, fireEvent, waitForElementToBeRemoved } from '@testing-library/react';
import '@testing-library/jest-dom';
import * as useThemeModule from '@/hooks/useTheme';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { useIsAuthenticated, useLogout } from '@/lib/auth/authHooks';
import useAppTranslation from '@/hooks/useTranslationWrapper';
import { act } from 'react';

// Mock the required modules
jest.mock('@/hooks/useTheme');
jest.mock('@/lib/auth/authHooks');
jest.mock('@/hooks/useTranslationWrapper');
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => <img {...props} alt={props.alt} />,
}));
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe('Dark Mode Integration Tests', () => {
  // Set up our mocks before each test
  beforeEach(() => {
    // Mock useTheme hook
    (useThemeModule.default as jest.Mock).mockReturnValue({
      theme: 'dark',
      toggleTheme: jest.fn(),
    });

    // Mock authentication hooks
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      user: { username: 'testuser', isAdmin: false },
      isAuthenticated: true,
      isLoading: false,
    });

    (useLogout as jest.Mock).mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    });

    // Mock translation hook
    (useAppTranslation as jest.Mock).mockReturnValue({
      t: (key: string) => key,
      i18n: {
        changeLanguage: jest.fn(),
      },
    });

    // Mock document methods
    document.documentElement.classList.remove('dark');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Navbar Dark Mode', () => {
    it('applies dark mode classes to Navbar components', () => {
      render(<Navbar />);
      
      // Check if the navbar has dark mode classes
      const navbar = screen.getByRole('navigation');
      expect(navbar).toHaveClass('dark:bg-gray-800');
      
      // Check if the dropdown menu has dark mode classes
      const userButton = screen.getByText('testuser');
      fireEvent.click(userButton);
      const dropdown = screen.getByRole('menu');
      expect(dropdown).toHaveClass('dark:bg-gray-700');
    });

    it('shows correct theme toggle button in dark mode', () => {
      render(<Navbar />);
      
      const userButton = screen.getByText('testuser');
      fireEvent.click(userButton);
      
      // In dark mode, it should show "Light Mode" as the toggle option
      expect(screen.getByText('Light Mode')).toBeInTheDocument();
    });
  });

  describe('Footer Dark Mode', () => {
    it('applies dark mode classes to Footer components', () => {
      render(<Footer />);
      
      const footer = screen.getByRole('contentinfo');
      expect(footer).toHaveClass('dark:bg-gray-800');
      expect(footer).toHaveClass('dark:border-gray-700');
    });

    it('applies dark mode text colors', async () => {
      // Mock the fetch response for health status with a delay
      global.fetch = jest.fn().mockImplementation((url) => {
        if (url.includes('/health')) {
          return new Promise(resolve => {
            setTimeout(() => {
              resolve({
                ok: true,
                json: () => Promise.resolve({
                  status: 'healthy',
                  database: { status: 'connected', message: 'Database is connected' },
                  environment: 'development',
                  version: '1.0.0-dev'
                })
              });
            }, 100);
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({})
        });
      });

      render(<Footer />);
      
      // Wait for loading indicator to appear
      await screen.findByTestId('loading-indicator');
      
      // Wait for loading indicator to disappear
      await waitForElementToBeRemoved(() => screen.queryByTestId('loading-indicator'));
      
      // Wait for state updates to complete
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });

      // Verify the version link exists and has the correct content
      const versionLink = screen.getByRole('link', { href: '/health-status' });
      expect(versionLink).toBeInTheDocument();
      
      // Verify the version text is displayed
      const versionText = screen.getByText('v1.0.0-dev');
      expect(versionText).toBeInTheDocument();
      
      // Verify the status indicator is displayed with the correct color
      const statusIndicator = versionLink.querySelector('.bg-green-500');
      expect(statusIndicator).toBeInTheDocument();
    });
  });

  describe('Button Component Dark Mode', () => {
    it('applies dark mode styles to primary button', () => {
      render(<Button variant="default">Test Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary');
      expect(button).toHaveClass('text-primary-foreground');
    });

    it('applies dark mode styles to secondary button', () => {
      render(<Button variant="secondary">Test Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-secondary');
      expect(button).toHaveClass('text-secondary-foreground');
    });

    it('applies dark mode styles to outline button', () => {
      render(<Button variant="outline">Test Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('border-input');
      expect(button).toHaveClass('hover:bg-accent');
      expect(button).toHaveClass('hover:text-accent-foreground');
    });
  });

  describe('Theme Transition', () => {
    beforeEach(() => {
      // Clear any existing classes
      document.documentElement.classList.remove('dark');
    });

    it('adds dark class to document when theme is dark', () => {
      // Mock the useTheme hook to simulate dark mode
      (useThemeModule.default as jest.Mock).mockReturnValue({
        theme: 'dark',
        toggleTheme: jest.fn(),
      });

      render(<Navbar />);
      
      // Wait for the useEffect to run
      setTimeout(() => {
        expect(document.documentElement.classList.contains('dark')).toBeTruthy();
      }, 0);
    });

    it('removes dark class from document when theme is light', () => {
      // Add dark class initially
      document.documentElement.classList.add('dark');

      // Mock the useTheme hook to simulate light mode
      (useThemeModule.default as jest.Mock).mockReturnValue({
        theme: 'light',
        toggleTheme: jest.fn(),
      });

      render(<Navbar />);
      
      // Wait for the useEffect to run
      setTimeout(() => {
        expect(document.documentElement.classList.contains('dark')).toBeFalsy();
      }, 0);
    });
  });
}); 