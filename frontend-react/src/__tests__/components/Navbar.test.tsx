import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Navbar from '../../components/Navbar';
import { useTheme } from '../../hooks/useTheme';
import { useIsAuthenticated, useLogout } from '../../lib/auth/authHooks';
import { useTranslation } from '../../hooks/useTranslationWrapper';
import { useScreenSize } from '../../utils/responsive';

// Mock the components and hooks
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => <img {...props} />,
}));

jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

jest.mock('../../components/LanguageSelector', () => ({
  __esModule: true,
  default: () => <div data-testid="language-selector-mock" />,
}));

// Mock useTheme with both named and default export
jest.mock('../../hooks/useTheme', () => {
  const mockUseTheme = jest.fn();
  mockUseTheme.mockReturnValue({
    theme: 'dark',
    toggleTheme: jest.fn()
  });
  return {
    __esModule: true,
    useTheme: mockUseTheme,
    default: mockUseTheme
  };
});

jest.mock('../../lib/auth/authHooks', () => ({
  useAuth: jest.fn(),
  useIsAuthenticated: jest.fn(),
  useLogout: jest.fn()
}));

// Create translation mapping to simulate actual translations
const translations = {
  'navigation.home': 'Home',
  'navigation.products': 'Products',
  'navigation.sales': 'Sales',
  'navigation.production': 'Production',
  'navigation.inventory': 'Inventory',
  'navigation.settings': 'Settings',
  'user.logout': 'Logout',
  'theme.lightMode': 'Light Mode',
  'theme.darkMode': 'Dark Mode',
  'navigation.ui_components': 'UI Components'
};

jest.mock('../../hooks/useTranslationWrapper', () => {
  const mockTranslation = jest.fn();
  mockTranslation.mockReturnValue({
    t: jest.fn(key => translations[key] || key),
    i18n: { language: 'en' }
  });
  return {
    __esModule: true,
    useTranslation: mockTranslation,
    default: mockTranslation
  };
});

jest.mock('../../utils/responsive', () => ({
  useScreenSize: jest.fn(),
}));

// Mock the MobileMenu component
const mockMobileMenuFn = jest.fn();
jest.mock('../../components/MobileMenu', () => ({
  __esModule: true,
  MobileMenu: props => {
    mockMobileMenuFn(props);
    return <div data-testid="mobile-menu-mock" />;
  }
}));

// Proper mock for window.getComputedStyle
const originalGetComputedStyle = window.getComputedStyle;
window.getComputedStyle = jest.fn().mockImplementation((element) => {
  const computedStyle = {
    display: 'block',
    visibility: 'visible',
    getPropertyValue: (prop: string) => {
      if (prop === 'display') return 'block';
      if (prop === 'visibility') return 'visible';
      return '';
    }
  };
  return computedStyle;
});

// Restore original after tests
afterAll(() => {
  window.getComputedStyle = originalGetComputedStyle;
});

describe('Navbar', () => {
  // Default mock implementations
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup mock return values using imported mocks
    (useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      toggleTheme: jest.fn(),
    });
    
    (useIsAuthenticated as jest.Mock).mockReturnValue({
      user: { username: 'testuser', isAdmin: false },
    });
    
    (useLogout as jest.Mock).mockReturnValue({
      mutate: jest.fn(),
    });
    
    (useTranslation as jest.Mock).mockReturnValue({
      t: (key: string) => translations[key] || key,
      i18n: { language: 'en' },
    });
    
    // Default to desktop size
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: false,
      isTablet: false,
      isDesktop: true,
    });
  });

  it('renders the logo', () => {
    render(<Navbar />);
    const logo = screen.getByAltText('Wilhelm Schweizer Zinnmanufaktur');
    expect(logo).toBeInTheDocument();
  });

  it('renders desktop navigation on large screens', () => {
    render(<Navbar />);
    
    // Navigation links should be visible - now checking for the translated text
    const links = [
      screen.getByText(translations['navigation.home']),
      screen.getByText(translations['navigation.products']),
      screen.getByText(translations['navigation.sales'])
    ];
    
    links.forEach(link => {
      expect(link).toBeInTheDocument();
    });
  });

  it('passes correct navigation items to MobileMenu on small screens', () => {
    // Set screen size to mobile
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    
    render(<Navbar />);
    
    // Check that MobileMenu was called with translated items
    expect(mockMobileMenuFn).toHaveBeenCalledWith(
      expect.objectContaining({
        items: expect.arrayContaining([
          expect.objectContaining({ href: '/dashboard', label: translations['navigation.home'] }),
          expect.objectContaining({ href: '/products', label: translations['navigation.products'] }),
          expect.objectContaining({ href: '/sales', label: translations['navigation.sales'] }),
          expect.objectContaining({ href: '/warehouse', label: translations['navigation.inventory'] }),
          expect.objectContaining({ href: '/picklist', label: 'Picklist' }),
        ]),
      })
    );
  });

  it('shows user menu dropdown when clicked', () => {
    render(<Navbar />);
    
    // User menu button should be visible
    const userMenuButton = screen.getByText('testuser').closest('button');
    expect(userMenuButton).toBeInTheDocument();
    
    // Click the user menu button
    fireEvent.click(userMenuButton!);
    
    // User menu should be visible now - checking for translated text
    const lightModeElements = screen.getAllByText(translations['theme.lightMode']);
    expect(lightModeElements.length).toBeGreaterThan(0);
    expect(screen.getByText(translations['navigation.settings'])).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('shows simplified user button on mobile', () => {
    // Set screen size to mobile
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    
    render(<Navbar />);
    
    // On mobile, find the mobile user dropdown by ID
    const mobileUserDropdown = document.getElementById('mobile-user-dropdown');
    expect(mobileUserDropdown).toBeInTheDocument();
    
    // Find the button inside the mobile user dropdown
    const mobileUserButton = mobileUserDropdown!.querySelector('button');
    expect(mobileUserButton).toBeInTheDocument();
    
    // Check for the SVG icon inside the button
    const userIcon = mobileUserButton!.querySelector('svg');
    expect(userIcon).toBeInTheDocument();
  });

  it('shows mobile user dropdown when clicked', () => {
    // Set screen size to mobile
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    
    render(<Navbar />);
    
    // Find the mobile user dropdown and button
    const mobileUserDropdown = document.getElementById('mobile-user-dropdown');
    const mobileUserButton = mobileUserDropdown!.querySelector('button');
    
    // Click the mobile user button
    fireEvent.click(mobileUserButton!);
    
    // Check for dropdown items using getAllByText for elements that might appear multiple times
    const lightModeElements = screen.getAllByText(translations['theme.lightMode']);
    expect(lightModeElements.length).toBeGreaterThan(0);
    
    // Check for Settings and Logout
    const settingsElements = screen.getAllByText(translations['navigation.settings']);
    expect(settingsElements.length).toBeGreaterThan(0);
    
    const logoutElements = screen.getAllByText('Logout');
    expect(logoutElements.length).toBeGreaterThan(0);
  });

  it('shows tablet specific UI when on tablet', () => {
    // Set screen size to tablet
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: false,
      isTablet: true,
      isDesktop: false,
    });
    
    render(<Navbar />);
    
    // Check tablet specific UI elements
    expect(screen.getByTestId('mobile-menu-mock')).toBeInTheDocument();
  });

  it('closes user dropdown when clicking outside', () => {
    // Set up the test
    render(<Navbar />);
    
    // User menu button should be visible
    const userMenuButton = screen.getByText('testuser').closest('button');
    expect(userMenuButton).toBeInTheDocument();
    
    // Click the user menu button to open dropdown
    fireEvent.click(userMenuButton!);
    
    // Verify dropdown is open by checking for a menu item
    const lightModeElements = screen.getAllByText(translations['theme.lightMode']);
    expect(lightModeElements.length).toBeGreaterThan(0);
    
    // Simulate clicking outside by triggering the mousedown event on the document
    fireEvent.mouseDown(document.body);
    
    // Dropdown should be closed now - use queryAllByText which doesn't throw if no elements found
    const closedLightModeElements = screen.queryAllByText(translations['theme.lightMode']);
    expect(closedLightModeElements.length).toBe(0);
  });

  it('shows UI Components in test dropdown menu', () => {
    render(<Navbar />);
    
    // Find and click the test dropdown button
    const testButton = screen.getByText('Test');
    fireEvent.click(testButton);
    
    // Verify UI Components link is in the dropdown
    const uiComponentsLink = screen.getByText('UI Components / Style Guide');
    expect(uiComponentsLink).toBeInTheDocument();
    
    // Verify it's inside the test dropdown
    const testDropdown = document.getElementById('test-dropdown');
    expect(testDropdown).toContainElement(uiComponentsLink);
  });
}); 