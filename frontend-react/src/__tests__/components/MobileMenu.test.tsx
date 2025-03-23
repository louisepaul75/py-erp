import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MobileMenu } from '@/components/MobileMenu';
import { useScreenSize } from '@/utils/responsive';

// Mock the useScreenSize hook
jest.mock('@/utils/responsive', () => ({
  useScreenSize: jest.fn(),
}));

describe('MobileMenu', () => {
  const mockItems = [
    { label: 'Home', href: '/' },
    { label: 'Products', href: '/products' },
    { label: 'About', href: '/about' },
  ];

  beforeEach(() => {
    // Reset all mocks between tests
    jest.clearAllMocks();
  });

  it('renders nothing when not on mobile or tablet', () => {
    // Mock the hook to return desktop screen
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: false,
      isTablet: false,
      isDesktop: true,
    });

    const { container } = render(<MobileMenu items={mockItems} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders menu button on mobile devices', () => {
    // Mock the hook to return mobile screen
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });

    render(<MobileMenu items={mockItems} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('renders menu button on tablet devices', () => {
    // Mock the hook to return tablet screen
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: false,
      isTablet: true,
      isDesktop: false,
    });

    render(<MobileMenu items={mockItems} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('toggles menu open when button is clicked', () => {
    // Mock the hook to return mobile screen
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });

    render(<MobileMenu items={mockItems} />);
    
    // Menu should be closed initially
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
    
    // Click the menu button to open
    fireEvent.click(screen.getByRole('button'));
    
    // Menu should be open
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('displays all navigation items when menu is open', () => {
    // Mock the hook to return mobile screen
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });

    render(<MobileMenu items={mockItems} />);
    
    // Open the menu
    fireEvent.click(screen.getByRole('button'));
    
    // Check if all navigation items are displayed
    mockItems.forEach(item => {
      expect(screen.getByText(item.label)).toBeInTheDocument();
    });
  });

  it('closes menu when a navigation item is clicked', () => {
    // Mock the hook to return mobile screen
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });

    render(<MobileMenu items={mockItems} />);
    
    // Open the menu
    fireEvent.click(screen.getByRole('button'));
    
    // Click on a navigation item
    fireEvent.click(screen.getByText('Products'));
    
    // Menu should be closed
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
  });

  it('changes button icon when menu is opened and closed', () => {
    // Mock the hook to return mobile screen
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });

    render(<MobileMenu items={mockItems} />);
    
    // Menu button should have aria-label for opening initially
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Open menu');
    
    // Open the menu
    fireEvent.click(screen.getByRole('button'));
    
    // Button in the open menu should have aria-label for closing
    expect(screen.getAllByRole('button')[0]).toHaveAttribute('aria-label', 'Close menu');
  });
}); 