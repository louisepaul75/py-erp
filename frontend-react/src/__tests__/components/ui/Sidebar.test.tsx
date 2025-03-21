import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SidebarProvider, Sidebar, SidebarTrigger, SidebarHeader, SidebarContent, SidebarFooter } from '@/components/ui/sidebar';

// Mock useIsMobile hook to control mobile state in tests
jest.mock('@/hooks/use-is-mobile', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(false), // Default to desktop
}));

// Import after mock is defined
import useIsMobile from '@/hooks/use-is-mobile';

describe('Sidebar Component', () => {
  const mockUseIsMobile = useIsMobile as jest.Mock;

  beforeEach(() => {
    mockUseIsMobile.mockReturnValue(false); // Reset to desktop for each test
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly in expanded state', () => {
    render(
      <SidebarProvider defaultOpen={true}>
        <Sidebar data-testid="sidebar">
          <SidebarHeader>Header</SidebarHeader>
          <SidebarContent>Content</SidebarContent>
          <SidebarFooter>Footer</SidebarFooter>
        </Sidebar>
      </SidebarProvider>
    );

    const sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toBeInTheDocument();
    expect(screen.getByText('Header')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument(); 
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('renders correctly in collapsed state', () => {
    render(
      <SidebarProvider defaultOpen={false}>
        <Sidebar data-testid="sidebar">
          <SidebarHeader>Header</SidebarHeader>
          <SidebarContent>Content</SidebarContent>
          <SidebarFooter>Footer</SidebarFooter>
        </Sidebar>
      </SidebarProvider>
    );

    const sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toBeInTheDocument();
    expect(sidebar).toHaveAttribute('data-state', 'collapsed');
  });

  it('toggles sidebar state when trigger is clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <SidebarProvider defaultOpen={true}>
        <SidebarTrigger data-testid="sidebar-trigger" />
        <Sidebar data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );

    const trigger = screen.getByTestId('sidebar-trigger');
    const sidebar = screen.getByTestId('sidebar');
    
    // Initially expanded
    expect(sidebar).toHaveAttribute('data-state', 'expanded');
    
    // Click to collapse
    await user.click(trigger);
    
    // Should now be collapsed
    expect(sidebar).toHaveAttribute('data-state', 'collapsed');
    
    // Click to expand again
    await user.click(trigger);
    
    // Should be expanded again
    expect(sidebar).toHaveAttribute('data-state', 'expanded');
  });

  it('toggles sidebar with keyboard shortcut', () => {
    render(
      <SidebarProvider defaultOpen={true}>
        <Sidebar data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );

    const sidebar = screen.getByTestId('sidebar');
    
    // Initially expanded
    expect(sidebar).toHaveAttribute('data-state', 'expanded');
    
    // Simulate keyboard shortcut Ctrl+B
    fireEvent.keyDown(window, { key: 'b', ctrlKey: true });
    
    // Should now be collapsed
    expect(sidebar).toHaveAttribute('data-state', 'collapsed');
    
    // Press shortcut again
    fireEvent.keyDown(window, { key: 'b', ctrlKey: true });
    
    // Should be expanded again
    expect(sidebar).toHaveAttribute('data-state', 'expanded');
  });

  it('renders mobile view when on mobile', () => {
    // Mock mobile device
    mockUseIsMobile.mockReturnValue(true);
    
    render(
      <SidebarProvider>
        <SidebarTrigger data-testid="sidebar-trigger" />
        <Sidebar data-testid="sidebar">
          <SidebarContent>Mobile Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );

    const trigger = screen.getByTestId('sidebar-trigger');
    expect(trigger).toBeInTheDocument();
    
    // Mobile sidebar initially not visible
    expect(screen.queryByText('Mobile Content')).not.toBeInTheDocument();
  });

  it('renders with different variants', () => {
    const { rerender } = render(
      <SidebarProvider defaultOpen={true}>
        <Sidebar variant="sidebar" data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    // Check "sidebar" variant (default)
    let sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toHaveAttribute('data-variant', 'sidebar');
    
    // Rerender with "floating" variant
    rerender(
      <SidebarProvider defaultOpen={true}>
        <Sidebar variant="floating" data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toHaveAttribute('data-variant', 'floating');
    
    // Rerender with "inset" variant
    rerender(
      <SidebarProvider defaultOpen={true}>
        <Sidebar variant="inset" data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toHaveAttribute('data-variant', 'inset');
  });

  it('renders controlled sidebar state', () => {
    const onOpenChange = jest.fn();
    
    const { rerender } = render(
      <SidebarProvider open={true} onOpenChange={onOpenChange}>
        <SidebarTrigger data-testid="sidebar-trigger" />
        <Sidebar data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    const sidebar = screen.getByTestId('sidebar');
    const trigger = screen.getByTestId('sidebar-trigger');
    
    // Initial state is open
    expect(sidebar).toHaveAttribute('data-state', 'expanded');
    
    // Click trigger
    fireEvent.click(trigger);
    
    // onOpenChange should be called with false
    expect(onOpenChange).toHaveBeenCalledWith(false);
    
    // Update the controlled prop
    rerender(
      <SidebarProvider open={false} onOpenChange={onOpenChange}>
        <SidebarTrigger data-testid="sidebar-trigger" />
        <Sidebar data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    // Now sidebar should be collapsed
    expect(sidebar).toHaveAttribute('data-state', 'collapsed');
  });

  it('sets cookie when sidebar state changes', () => {
    // Mock document.cookie
    const originalCookie = Object.getOwnPropertyDescriptor(document, 'cookie');
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
    });
    
    render(
      <SidebarProvider defaultOpen={true}>
        <SidebarTrigger data-testid="sidebar-trigger" />
        <Sidebar data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    const trigger = screen.getByTestId('sidebar-trigger');
    
    // Initial state should be expanded
    fireEvent.click(trigger);
    
    // Cookie should be set
    expect(document.cookie).toContain('sidebar:state=false');
    
    // Restore original cookie property
    if (originalCookie) {
      Object.defineProperty(document, 'cookie', originalCookie);
    }
  });
}); 