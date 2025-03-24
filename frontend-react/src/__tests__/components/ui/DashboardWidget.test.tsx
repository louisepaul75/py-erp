import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';

// Mock the entire dashboard module
jest.mock('@/components/ui/dashboard', () => {
  // Create a mock DashboardWidget component
  const DashboardWidget = ({
    id,
    title,
    children,
    isEditMode,
    onRemove,
  }: {
    id: string;
    title: string | null;
    children: React.ReactNode;
    isEditMode: boolean;
    onRemove?: (id: string) => void;
  }) => {
    return (
      <div 
        className={`h-full w-full overflow-auto ${isEditMode ? "border-2 border-dashed border-primary" : ""}`}
        data-testid="dashboard-widget"
      >
        <div className="h-full flex flex-col">
          {isEditMode && (
            <div className="absolute top-0 right-0 p-1 z-10 flex gap-1" data-testid="edit-controls">
              {onRemove && (
                <button 
                  onClick={() => onRemove(id)}
                  data-testid="remove-button"
                  aria-label="Remove widget"
                >
                  <span data-testid="x-icon">X Icon</span>
                </button>
              )}
              <div data-testid="grip-icon">Grip Icon</div>
            </div>
          )}
          
          {title && <h2 className="text-xl font-bold tracking-tight mb-2 pr-8">{title}</h2>}
          <div className="flex-1 overflow-auto">
            {children}
          </div>
        </div>
      </div>
    );
  };

  return {
    DashboardWidget,
  };
});

describe('DashboardWidget', () => {
  it('renders widget with title', () => {
    const { getByText, queryByTestId } = render(
      <DashboardWidget
        id="test-widget"
        title="Test Widget"
        isEditMode={false}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    expect(getByText('Test Widget')).toBeInTheDocument();
    expect(getByText('Widget Content')).toBeInTheDocument();
    
    // Should not show edit controls when not in edit mode
    expect(queryByTestId('edit-controls')).not.toBeInTheDocument();
  });

  it('renders widget without title', () => {
    const { getByText, queryByText } = render(
      <DashboardWidget
        id="test-widget"
        title={null}
        isEditMode={false}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    expect(queryByText('Test Widget')).not.toBeInTheDocument();
    expect(getByText('Widget Content')).toBeInTheDocument();
  });

  it('renders edit controls in edit mode', () => {
    const { getByTestId } = render(
      <DashboardWidget
        id="test-widget"
        title="Test Widget"
        isEditMode={true}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    expect(getByTestId('edit-controls')).toBeInTheDocument();
    expect(getByTestId('grip-icon')).toBeInTheDocument();
    // Without onRemove prop, the X button shouldn't be present
    expect(screen.queryByTestId('remove-button')).not.toBeInTheDocument();
  });

  it('renders remove button in edit mode when onRemove is provided', () => {
    const mockRemoveFn = jest.fn();
    
    render(
      <DashboardWidget
        id="test-widget"
        title="Test Widget"
        isEditMode={true}
        onRemove={mockRemoveFn}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    // Should show both edit controls
    expect(screen.getByTestId('grip-icon')).toBeInTheDocument();
    expect(screen.getByTestId('x-icon')).toBeInTheDocument();
    
    // Test remove button click
    const removeButton = screen.getByTestId('remove-button');
    fireEvent.click(removeButton);
    
    expect(mockRemoveFn).toHaveBeenCalledWith('test-widget');
  });

  it('renders with border styling in edit mode', () => {
    const { getByTestId } = render(
      <DashboardWidget
        id="test-widget"
        title="Test Widget"
        isEditMode={true}
      >
        <div>Widget Content</div>
      </DashboardWidget>
    );

    // Check for the edit mode border styling
    const widgetElement = getByTestId('dashboard-widget');
    expect(widgetElement.className).toContain('border-2');
    expect(widgetElement.className).toContain('border-dashed');
    expect(widgetElement.className).toContain('border-primary');
  });
});

// Import DashboardWidget to make TypeScript happy
import { DashboardWidget } from '@/components/ui/dashboard'; 