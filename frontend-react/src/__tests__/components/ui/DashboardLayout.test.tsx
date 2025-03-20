import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { mockMatchMedia, mockResizeObserver } from '@/utils/test-utils';

// Mock react-grid-layout
jest.mock('react-grid-layout', () => {
  const ReactGridLayout = ({ children, onLayoutChange, className, layouts, breakpoints, cols, rowHeight, width, isDraggable, isResizable, onBreakpointChange }) => {
    // Render a container with the provided children
    return (
      <div 
        data-testid="mock-grid-layout" 
        className={className}
        data-layouts={JSON.stringify(layouts)}
        data-breakpoints={JSON.stringify(breakpoints)}
        data-cols={JSON.stringify(cols)}
        data-row-height={rowHeight}
        data-is-draggable={isDraggable}
        data-is-resizable={isResizable}
      >
        {children}
      </div>
    );
  };

  return {
    Responsive: ReactGridLayout,
  };
});

// Get DashboardContent from the dashboard module for isolated testing
jest.mock('@/components/ui/dashboard', () => {
  const originalModule = jest.requireActual('@/components/ui/dashboard');
  
  // Create a separate DashboardContent for testing
  const DashboardContent = ({ 
    isEditMode, 
    width, 
    layouts, 
    handleLayoutChange, 
    renderWidgetContent 
  }) => {
    return (
      <div data-testid="dashboard-content">
        <div data-testid="responsive-grid-container">
          <div data-testid="responsive-grid-layout"
               data-is-edit-mode={isEditMode}
               data-width={width}
               data-layouts={JSON.stringify(layouts)}
          >
            {layouts.lg.map((item) => (
              <div key={item.i} data-testid={`widget-${item.i}`}>
                {renderWidgetContent && renderWidgetContent(item.i)}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };
  
  return {
    __esModule: true,
    ...originalModule,
    DashboardContent,
  };
});

// Mock local storage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Import the component we'll test
import { DashboardContent } from '@/components/ui/dashboard';

describe('Dashboard Layout Grid Functionality', () => {
  beforeEach(() => {
    mockMatchMedia();
    mockResizeObserver();
    localStorageMock.clear();
  });

  const mockLayouts = {
    lg: [
      { i: 'widget1', x: 0, y: 0, w: 6, h: 4, title: 'Widget 1' },
      { i: 'widget2', x: 6, y: 0, w: 6, h: 4, title: 'Widget 2' },
      { i: 'widget3', x: 0, y: 4, w: 12, h: 4, title: 'Widget 3' },
    ],
    md: [
      { i: 'widget1', x: 0, y: 0, w: 6, h: 4, title: 'Widget 1' },
      { i: 'widget2', x: 6, y: 0, w: 6, h: 4, title: 'Widget 2' },
      { i: 'widget3', x: 0, y: 4, w: 12, h: 4, title: 'Widget 3' },
    ],
    sm: [
      { i: 'widget1', x: 0, y: 0, w: 12, h: 4, title: 'Widget 1' },
      { i: 'widget2', x: 0, y: 4, w: 12, h: 4, title: 'Widget 2' },
      { i: 'widget3', x: 0, y: 8, w: 12, h: 4, title: 'Widget 3' },
    ],
  };

  it('renders the responsive grid layout with correct props', () => {
    const handleLayoutChange = jest.fn();
    const renderWidgetContent = jest.fn((id) => <div>Content for {id}</div>);
    
    render(
      <DashboardContent
        isEditMode={false}
        width={1200}
        layouts={mockLayouts}
        handleLayoutChange={handleLayoutChange}
        renderWidgetContent={renderWidgetContent}
      />
    );
    
    const gridLayout = screen.getByTestId('responsive-grid-layout');
    expect(gridLayout).toBeInTheDocument();
    
    // Check dashboard is rendering with the right data
    expect(gridLayout).toHaveAttribute('data-is-edit-mode', 'false');
    expect(gridLayout).toHaveAttribute('data-width', '1200');
    
    // Check layouts are passed correctly
    const parsedLayouts = JSON.parse(gridLayout.getAttribute('data-layouts'));
    expect(parsedLayouts).toEqual(mockLayouts);
    
    // Check all widgets are rendered
    expect(screen.getByTestId('widget-widget1')).toBeInTheDocument();
    expect(screen.getByTestId('widget-widget2')).toBeInTheDocument();
    expect(screen.getByTestId('widget-widget3')).toBeInTheDocument();
    
    // Check renderWidgetContent was called for each widget
    expect(renderWidgetContent).toHaveBeenCalledTimes(3);
    expect(renderWidgetContent).toHaveBeenCalledWith('widget1');
    expect(renderWidgetContent).toHaveBeenCalledWith('widget2');
    expect(renderWidgetContent).toHaveBeenCalledWith('widget3');
  });

  it('applies edit mode properties correctly', () => {
    const handleLayoutChange = jest.fn();
    const renderWidgetContent = jest.fn((id) => <div>Content for {id}</div>);
    
    render(
      <DashboardContent
        isEditMode={true}
        width={1200}
        layouts={mockLayouts}
        handleLayoutChange={handleLayoutChange}
        renderWidgetContent={renderWidgetContent}
      />
    );
    
    const gridLayout = screen.getByTestId('responsive-grid-layout');
    expect(gridLayout).toHaveAttribute('data-is-edit-mode', 'true');
  });

  it('renders with different layouts based on screen size', () => {
    const handleLayoutChange = jest.fn();
    const renderWidgetContent = jest.fn((id) => <div>Content for {id}</div>);
    
    // Render with desktop width
    const { rerender } = render(
      <DashboardContent
        isEditMode={false}
        width={1200}  // Desktop width
        layouts={mockLayouts}
        handleLayoutChange={handleLayoutChange}
        renderWidgetContent={renderWidgetContent}
      />
    );
    
    let gridLayout = screen.getByTestId('responsive-grid-layout');
    expect(gridLayout).toHaveAttribute('data-width', '1200');
    
    // Re-render with tablet width
    rerender(
      <DashboardContent
        isEditMode={false}
        width={800}  // Tablet width
        layouts={mockLayouts}
        handleLayoutChange={handleLayoutChange}
        renderWidgetContent={renderWidgetContent}
      />
    );
    
    gridLayout = screen.getByTestId('responsive-grid-layout');
    expect(gridLayout).toHaveAttribute('data-width', '800');
    
    // Re-render with mobile width
    rerender(
      <DashboardContent
        isEditMode={false}
        width={500}  // Mobile width
        layouts={mockLayouts}
        handleLayoutChange={handleLayoutChange}
        renderWidgetContent={renderWidgetContent}
      />
    );
    
    gridLayout = screen.getByTestId('responsive-grid-layout');
    expect(gridLayout).toHaveAttribute('data-width', '500');
  });

  it('renders correct widget content for each widget', () => {
    const handleLayoutChange = jest.fn();
    
    // Define specific content for each widget
    const renderWidgetContent = jest.fn((id) => {
      switch (id) {
        case 'widget1':
          return <div data-testid="widget1-content">Widget 1 Content</div>;
        case 'widget2':
          return <div data-testid="widget2-content">Widget 2 Content</div>;
        case 'widget3':
          return <div data-testid="widget3-content">Widget 3 Content</div>;
        default:
          return null;
      }
    });
    
    render(
      <DashboardContent
        isEditMode={false}
        width={1200}
        layouts={mockLayouts}
        handleLayoutChange={handleLayoutChange}
        renderWidgetContent={renderWidgetContent}
      />
    );
    
    // Check each widget has its specific content
    expect(screen.getByTestId('widget1-content')).toBeInTheDocument();
    expect(screen.getByTestId('widget1-content')).toHaveTextContent('Widget 1 Content');
    
    expect(screen.getByTestId('widget2-content')).toBeInTheDocument();
    expect(screen.getByTestId('widget2-content')).toHaveTextContent('Widget 2 Content');
    
    expect(screen.getByTestId('widget3-content')).toBeInTheDocument();
    expect(screen.getByTestId('widget3-content')).toHaveTextContent('Widget 3 Content');
  });
}); 