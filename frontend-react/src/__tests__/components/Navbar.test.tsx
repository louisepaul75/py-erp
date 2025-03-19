import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Navbar } from '@/components/Navbar';
import * as useThemeModule from '@/hooks/useTheme';
import * as authHooksModule from '@/lib/auth/authHooks';
import * as translationModule from '@/hooks/useTranslationWrapper';

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={props.alt} />;
  },
}));

// Mock next/link
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>;
  },
}));

// Mock LanguageSelector to avoid i18next issues
jest.mock('@/components/LanguageSelector', () => ({
  __esModule: true,
  default: () => <div data-testid="language-selector">Language Selector</div>
}));

// Mock the hooks
jest.mock('@/hooks/useTheme', () => ({
  __esModule: true,
  default: jest.fn(),
}));

jest.mock('@/lib/auth/authHooks', () => ({
  __esModule: true,
  useIsAuthenticated: jest.fn(),
  useLogout: jest.fn(),
}));

jest.mock('@/hooks/useTranslationWrapper', () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe('Navbar', () => {
  // Set up our mocks
  beforeEach(() => {
    // Mock useTheme
    const mockUseTheme = jest.fn().mockReturnValue({
      theme: 'light',
      toggleTheme: jest.fn(),
    });
    jest.spyOn(useThemeModule, 'default').mockImplementation(mockUseTheme);

    // Mock useIsAuthenticated
    const mockUseIsAuthenticated = jest.fn().mockReturnValue({
      user: { username: 'testuser', isAdmin: false },
      isAuthenticated: true,
      isLoading: false,
    });
    jest.spyOn(authHooksModule, 'useIsAuthenticated').mockImplementation(mockUseIsAuthenticated);

    // Mock useLogout
    const mockUseLogout = jest.fn().mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    });
    jest.spyOn(authHooksModule, 'useLogout').mockImplementation(mockUseLogout);

    // Mock useTranslation
    const mockUseTranslation = jest.fn().mockReturnValue({
      t: (key: string) => {
        const translations: Record<string, string> = {
          'navigation.home': 'Home',
          'navigation.products': 'Products',
          'navigation.sales': 'Sales',
          'navigation.production': 'Production',
          'navigation.inventory': 'Inventory',
          'navigation.settings': 'Settings',
          'navigation.admin_settings': 'Admin Settings',
        };
        return translations[key] || key;
      },
      i18n: {
        changeLanguage: jest.fn(),
      },
    });
    jest.spyOn(translationModule, 'default').mockImplementation(mockUseTranslation);

    // Mock document.addEventListener
    document.addEventListener = jest.fn();
    document.removeEventListener = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<Navbar />);
    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('displays the correct navigation links', () => {
    render(<Navbar />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Products')).toBeInTheDocument();
    expect(screen.getByText('Sales')).toBeInTheDocument();
    expect(screen.getByText('Production')).toBeInTheDocument();
    expect(screen.getByText('Inventory')).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('toggles the user dropdown when clicked', () => {
    render(<Navbar />);
    
    // Initially, dropdown should be closed
    expect(screen.queryByText('Dark Mode')).not.toBeInTheDocument();
    
    // Click the user menu button
    const userMenuButton = screen.getByText('testuser').closest('button');
    if (userMenuButton) fireEvent.click(userMenuButton);
    
    // Now dropdown should be open
    expect(screen.getByText('Dark Mode')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('toggles the test menu dropdown when clicked', () => {
    render(<Navbar />);
    
    // Initially, dropdown should be closed
    expect(screen.queryByText('UI Components / Style Guide')).not.toBeInTheDocument();
    
    // Click the test menu button
    const testMenuButton = screen.getByText('Test');
    fireEvent.click(testMenuButton);
    
    // Now dropdown should be open
    expect(screen.getByText('UI Components / Style Guide')).toBeInTheDocument();
    expect(screen.getByText('Feature 1')).toBeInTheDocument();
    expect(screen.getByText('Feature 2')).toBeInTheDocument();
  });

  it('toggles the mobile menu when clicked', () => {
    render(<Navbar />);
    
    // Initially, mobile menu should be closed
    expect(screen.queryByRole('button', { name: /open main menu/i })).toBeInTheDocument();
    
    // Click the mobile menu button
    const mobileMenuButton = screen.getByRole('button', { name: /open main menu/i });
    fireEvent.click(mobileMenuButton);
    
    // Mobile menu should be open
    expect(screen.getAllByText('Home')).toHaveLength(2); // One in desktop, one in mobile
    expect(screen.getAllByText('Products')).toHaveLength(2);
  });

  it('calls logout when logout button is clicked', () => {
    const mockLogout = { mutate: jest.fn() };
    jest.spyOn(authHooksModule, 'useLogout').mockReturnValue(mockLogout as any);
    
    render(<Navbar />);
    
    // Open the dropdown
    const userMenuButton = screen.getByText('testuser').closest('button');
    if (userMenuButton) fireEvent.click(userMenuButton);
    
    // Click the logout button - select the button element directly
    const logoutButton = screen.getByText('Logout').closest('button');
    if (logoutButton) fireEvent.click(logoutButton);
    
    // Check if logout was called
    expect(mockLogout.mutate).toHaveBeenCalled();
  });

  it('displays different settings text for admin users', () => {
    // Mock admin user
    jest.spyOn(authHooksModule, 'useIsAuthenticated').mockReturnValue({
      user: { username: 'admin', isAdmin: true },
      isAuthenticated: true,
      isLoading: false,
    });
    
    render(<Navbar />);
    
    // Open the dropdown
    const userMenuButton = screen.getByText('admin').closest('button');
    if (userMenuButton) fireEvent.click(userMenuButton);
    
    // Check for admin settings text
    expect(screen.getByText('Admin Settings')).toBeInTheDocument();
  });

  it('toggles theme when theme toggle is clicked', () => {
    const mockToggleTheme = jest.fn();
    jest.spyOn(useThemeModule, 'default').mockReturnValue({
      theme: 'light',
      toggleTheme: mockToggleTheme,
    });
    
    render(<Navbar />);
    
    // Open the dropdown
    const userMenuButton = screen.getByText('testuser').closest('button');
    if (userMenuButton) fireEvent.click(userMenuButton);
    
    // Check if language selector is rendered
    expect(screen.getByTestId('language-selector')).toBeInTheDocument();
    
    // Click the theme toggle
    const darkModeButton = screen.getByText('Dark Mode');
    fireEvent.click(darkModeButton);
    
    // Check if toggleTheme was called
    expect(mockToggleTheme).toHaveBeenCalled();
  });
}); 