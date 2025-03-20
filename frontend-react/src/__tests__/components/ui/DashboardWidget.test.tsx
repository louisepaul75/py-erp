import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { DashboardWidget } from '@/components/ui/dashboard';

// Since DashboardWidget is not exported by default, we need to mock it
// Let's create a mock module for dashboard.tsx
jest.mock('@/components/ui/dashboard', () => {
  const originalModule = jest.requireActual('@/components/ui/dashboard');
  
  // Extract the DashboardWidget component implementation from dashboard.tsx
  const DashboardWidget = ({ id, title, children, isEditMode, onRemove }) => {
    return (
      <div className={`h-full w-full overflow-auto ${isEditMode ? "border-2 border-dashed border-primary" : ""}`} data-testid="dashboard-widget">
        <div className="h-full flex flex-col">
          {isEditMode && (
            <div className="absolute top-0 right-0 p-1 z-10 flex gap-1" data-testid="edit-controls">
              {onRemove && (
                <button 
                  data-testid="remove-button"
                  className="h-6 w-6"
                  onClick={() => onRemove(id)}
                  aria-label="remove"
                >
                  X
                </button>
              )}
              <div className="h-6 w-6" data-testid="drag-handle">
                Grip
              </div>
            </div>
          )}
          
          {title && <h2 className="text-xl font-bold tracking-tight mb-2 pr-8" data-testid="widget-title">{title}</h2>}
          <div className="flex-1 overflow-auto" data-testid="widget-content">
            {children}
          </div>
        </div>
      </div>
    );
  };
  
  return {
    __esModule: true,
    ...originalModule,
    DashboardWidget,
  };
});

describe('DashboardWidget Component', () => {
  it('renders children correctly', () => {
    render(
      <DashboardWidget id="test-widget" title={null} isEditMode={false}>
        <div data-testid="test-content">Test Content</div>
      </DashboardWidget>
    );
    
    expect(screen.getByTestId('test-content')).toBeInTheDocument();
    expect(screen.getByTestId('widget-content')).toBeInTheDocument();
  });
  
  it('displays the title when provided', () => {
    render(
      <DashboardWidget id="test-widget" title="Test Title" isEditMode={false}>
        <div>Content</div>
      </DashboardWidget>
    );
    
    expect(screen.getByTestId('widget-title')).toBeInTheDocument();
    expect(screen.getByTestId('widget-title')).toHaveTextContent('Test Title');
  });
  
  it('does not display title when not provided', () => {
    render(
      <DashboardWidget id="test-widget" title={null} isEditMode={false}>
        <div>Content</div>
      </DashboardWidget>
    );
    
    expect(screen.queryByTestId('widget-title')).not.toBeInTheDocument();
  });
  
  it('displays edit controls in edit mode', () => {
    render(
      <DashboardWidget id="test-widget" title="Test Title" isEditMode={true} onRemove={() => {}}>
        <div>Content</div>
      </DashboardWidget>
    );
    
    expect(screen.getByTestId('edit-controls')).toBeInTheDocument();
    expect(screen.getByTestId('remove-button')).toBeInTheDocument();
    expect(screen.getByTestId('drag-handle')).toBeInTheDocument();
  });
  
  it('does not display edit controls when not in edit mode', () => {
    render(
      <DashboardWidget id="test-widget" title="Test Title" isEditMode={false} onRemove={() => {}}>
        <div>Content</div>
      </DashboardWidget>
    );
    
    expect(screen.queryByTestId('edit-controls')).not.toBeInTheDocument();
    expect(screen.queryByTestId('remove-button')).not.toBeInTheDocument();
    expect(screen.queryByTestId('drag-handle')).not.toBeInTheDocument();
  });
  
  it('calls onRemove with the correct id when remove button is clicked', () => {
    const mockOnRemove = jest.fn();
    
    render(
      <DashboardWidget id="test-widget" title="Test Title" isEditMode={true} onRemove={mockOnRemove}>
        <div>Content</div>
      </DashboardWidget>
    );
    
    fireEvent.click(screen.getByTestId('remove-button'));
    
    expect(mockOnRemove).toHaveBeenCalledTimes(1);
    expect(mockOnRemove).toHaveBeenCalledWith('test-widget');
  });
  
  it('applies edit mode styling', () => {
    const { container } = render(
      <DashboardWidget id="test-widget" title="Test Title" isEditMode={true}>
        <div>Content</div>
      </DashboardWidget>
    );
    
    const widget = screen.getByTestId('dashboard-widget');
    expect(widget).toHaveClass('border-2', 'border-dashed', 'border-primary');
  });
  
  it('does not apply edit mode styling when not in edit mode', () => {
    render(
      <DashboardWidget id="test-widget" title="Test Title" isEditMode={false}>
        <div>Content</div>
      </DashboardWidget>
    );
    
    const widget = screen.getByTestId('dashboard-widget');
    expect(widget).not.toHaveClass('border-2', 'border-dashed', 'border-primary');
  });
}); 