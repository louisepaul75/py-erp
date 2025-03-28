import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SidebarProvider, Sidebar, SidebarTrigger, SidebarHeader, SidebarContent, SidebarFooter } from '@/components/ui/sidebar';

// Mock useIsMobile hook to control mobile state in tests
jest.mock('../../../hooks/use-mobile', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(false), // Default to desktop
}));

// Mock document.cookie
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: '',
});

// Mock sheet component used inside the sidebar for mobile view
jest.mock('@/components/ui/sheet', () => ({
  Sheet: ({ children }) => <div data-testid="mock-sheet">{children}</div>,
  SheetContent: ({ children, ...props }) => (
    <div data-testid="mock-sheet-content" {...props}>
      {children}
    </div>
  ),
}));

// Import after mock is defined
import useIsMobile from '../../../hooks/use-mobile';

describe('Sidebar Component', () => {
  const mockUseIsMobile = useIsMobile as jest.Mock;

  beforeEach(() => {
    mockUseIsMobile.mockReturnValue(false); // Reset to desktop for each test
    document.cookie = '';
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

    // Find sidebar wrapper div with the data-state attribute
    const sidebarWrapper = screen.getByTestId('sidebar').closest('[data-state]');
    expect(sidebarWrapper).toBeInTheDocument();
    expect(sidebarWrapper).toHaveAttribute('data-state', 'collapsed');
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
    // Find sidebar wrapper div with the data-state attribute
    const sidebarWrapper = screen.getByTestId('sidebar').closest('[data-state]');
    
    // Initially expanded
    expect(sidebarWrapper).toHaveAttribute('data-state', 'expanded');
    
    // Click to collapse
    await user.click(trigger);
    
    // Should now be collapsed
    expect(sidebarWrapper).toHaveAttribute('data-state', 'collapsed');
    
    // Click to expand again
    await user.click(trigger);
    
    // Should be expanded again
    expect(sidebarWrapper).toHaveAttribute('data-state', 'expanded');
  });

  it('toggles sidebar with keyboard shortcut', () => {
    render(
      <SidebarProvider defaultOpen={true}>
        <Sidebar data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );

    // Find sidebar wrapper div with the data-state attribute
    const sidebarWrapper = screen.getByTestId('sidebar').closest('[data-state]');
    
    // Initially expanded
    expect(sidebarWrapper).toHaveAttribute('data-state', 'expanded');
    
    // Simulate keyboard shortcut Ctrl+B
    fireEvent.keyDown(window, { key: 'b', ctrlKey: true });
    
    // Should now be collapsed
    expect(sidebarWrapper).toHaveAttribute('data-state', 'collapsed');
    
    // Press shortcut again
    fireEvent.keyDown(window, { key: 'b', ctrlKey: true });
    
    // Should be expanded again
    expect(sidebarWrapper).toHaveAttribute('data-state', 'expanded');
  });

  it('renders mobile view when on mobile', () => {
    // Mock the useIsMobile hook to return true for mobile view
    jest.spyOn(React, 'useState').mockImplementationOnce(() => [true, jest.fn()]);
    
    render(
      <SidebarProvider defaultOpen={true}>
        <SidebarTrigger data-testid="sidebar-trigger" />
        <Sidebar data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    const trigger = screen.getByTestId('sidebar-trigger');
    expect(trigger).toBeInTheDocument();
    
    // In mobile view with React 19, the structure has changed
    // Look for the mobile sidebar element inside the Sheet
    const mobileSidebar = screen.getByTestId('mock-sheet-content');
    expect(mobileSidebar).toBeInTheDocument();
    expect(mobileSidebar).toHaveAttribute('data-mobile', 'true');
    
    // The mobile content is rendered but not immediately visible in the Sheet
    // (Sheet content is rendered but not visible until opened in the real component)
  });

  it('renders with different variants', () => {
    const { rerender } = render(
      <SidebarProvider defaultOpen={true}>
        <Sidebar variant="sidebar" data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    // Find sidebar wrapper div with the data-variant attribute
    const sidebarWrapper = screen.getByTestId('sidebar').closest('[data-variant]');
    
    // Check "sidebar" variant (default)
    expect(sidebarWrapper).toHaveAttribute('data-variant', 'sidebar');
    
    // Rerender with "floating" variant
    rerender(
      <SidebarProvider defaultOpen={true}>
        <Sidebar variant="floating" data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    // Find updated sidebar wrapper after rerender
    const floatingSidebar = screen.getByTestId('sidebar').closest('[data-variant]');
    expect(floatingSidebar).toHaveAttribute('data-variant', 'floating');
    
    // Rerender with "inset" variant
    rerender(
      <SidebarProvider defaultOpen={true}>
        <Sidebar variant="inset" data-testid="sidebar">
          <SidebarContent>Content</SidebarContent>
        </Sidebar>
      </SidebarProvider>
    );
    
    // Find updated sidebar wrapper after rerender
    const insetSidebar = screen.getByTestId('sidebar').closest('[data-variant]');
    expect(insetSidebar).toHaveAttribute('data-variant', 'inset');
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
    
    // Find sidebar wrapper div with the data-state attribute
    const sidebarWrapper = screen.getByTestId('sidebar').closest('[data-state]');
    const trigger = screen.getByTestId('sidebar-trigger');
    
    // Initial state is open
    expect(sidebarWrapper).toHaveAttribute('data-state', 'expanded');
    
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
    
    // Find updated sidebar wrapper after rerender
    const updatedSidebarWrapper = screen.getByTestId('sidebar').closest('[data-state]');
    
    // Now sidebar should be collapsed
    expect(updatedSidebarWrapper).toHaveAttribute('data-state', 'collapsed');
  });

  it('sets cookie when sidebar state changes', () => {
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
  });
}); 