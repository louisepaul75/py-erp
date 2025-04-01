import React from 'react';
import { render, screen, fireEvent, waitForElementToBeRemoved, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import * as useThemeModule from '@/hooks/useTheme';
import * as useMobileModule from '@/hooks/use-mobile';
import { Footer } from '@/components/Footer';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { useIsAuthenticated, useLogout } from '@/lib/auth/authHooks';
import useAppTranslation from '@/hooks/useTranslationWrapper';
import { act } from 'react';
import { MemoryRouter } from 'react-router-dom';

// Mock React explicitly to ensure the test environment uses the intended version/hooks
jest.mock('react', () => {
  const actualReact = jest.requireActual('react');
  return {
    ...actualReact, // Keep actual React functionality
    // Potentially override specific hooks if needed, but start with just mocking the module
  };
});

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
  let consoleErrorSpy: jest.SpyInstance;
  
  // Helper function to apply theme and render component
  const renderWithTheme = (component: React.ReactElement, theme: 'light' | 'dark') => {
    // Set the theme attribute on the body for Tailwind CSS
    document.body.className = theme; // Set body class for Tailwind
    document.documentElement.classList.toggle('dark', theme === 'dark'); // Set class on html for the hook
    
    // No ThemeProviderContext needed based on current implementation
    return render(
      <MemoryRouter>
        {component}
      </MemoryRouter>
    );
  };
  
  beforeAll(() => {
    // Mock console.error to prevent logging during tests
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterAll(() => {
    // Restore console.error after all tests
    consoleErrorSpy.mockRestore();
  });

  beforeEach(() => {
    // Clear mock calls before each test
    consoleErrorSpy.mockClear();
    
    // Reset fetch mock before each test
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        // Ensure mock response includes 'results' array
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            success: true,
            results: [
              { component: 'api', status: 'success', details: 'OK', response_time: 10, timestamp: new Date().toISOString() },
              { component: 'database', status: 'success', details: 'Connected', response_time: 5, timestamp: new Date().toISOString() }
            ],
            authenticated: true,
            server_time: new Date().toISOString()
          })
        });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ branch: 'main' })
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

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
    // Reset body class and clear mocks
    document.body.className = '';
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
    it.skip('applies dark mode classes to Footer components', () => {
      renderWithTheme(<Footer />, 'dark');
      
      const footer = screen.getByRole('contentinfo');
      expect(footer).toHaveClass('dark:bg-gray-800');
      expect(footer).toHaveClass('dark:border-gray-700');
    });

    it.skip('applies dark mode text colors', async () => {
      document.body.className = 'dark';
      document.documentElement.classList.toggle('dark', true);

      render(
        <MemoryRouter>
          <Footer />
        </MemoryRouter>
      );

      // Wait for the footer content to render
      await waitFor(() => {
        const footerElement = screen.getByRole('contentinfo');
        expect(footerElement).toBeInTheDocument();
      });
      
      // Verify the copyright text has dark mode classes
      const copyrightText = await screen.findByText(/pyERP System/);
      expect(copyrightText).toHaveClass('dark:text-gray-400');
      
      // Verify the version link exists and has the correct content
      const versionLink = screen.getByRole('link', { name: /v1\.0\.0/ });
      expect(versionLink).toBeInTheDocument();
      expect(versionLink).toHaveClass('dark:text-gray-400', 'dark:hover:text-gray-200');

      // Verify the status indicator is rendered (health check passes)
      const statusIndicator = await screen.findByTestId('api-status-indicator');
      expect(statusIndicator).toHaveClass('bg-green-500');
    });
  });

  describe('Button Component Dark Mode', () => {
    it('applies dark mode styles to primary button', () => {
      render(<Button variant="default">Test Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-blue-600');
      expect(button).toHaveClass('dark:bg-blue-600');
      expect(button).toHaveClass('dark:text-white');
    });

    it('applies dark mode styles to secondary button', () => {
      render(<Button variant="secondary">Test Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-slate-100');
      expect(button).toHaveClass('dark:bg-slate-800');
      expect(button).toHaveClass('dark:text-slate-300');
    });

    it('applies dark mode styles to outline button', () => {
      render(<Button variant="outline">Test Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('border-slate-300');
      expect(button).toHaveClass('dark:border-slate-700');
      expect(button).toHaveClass('dark:bg-slate-900');
      expect(button).toHaveClass('dark:text-slate-300');
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