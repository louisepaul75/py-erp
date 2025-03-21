import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from '@/components/ui/tooltip';

// Mock React Portal to make tooltips easier to test
jest.mock('react-dom', () => {
  const original = jest.requireActual('react-dom');
  return {
    ...original,
    createPortal: (node) => node,
  };
});

describe('Tooltip Component', () => {
  it('renders with trigger element', () => {
    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent>Tooltip content</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );

    // Verify trigger is rendered
    const trigger = screen.getByTestId('tooltip-trigger');
    expect(trigger).toBeInTheDocument();
    expect(trigger).toHaveTextContent('Hover me');
    
    // Content should not be immediately visible
    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument();
  });

  it('shows tooltip content when defaultOpen is true', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent>Tooltip content</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    
    // Tooltip content should be visible with defaultOpen
    const tooltipElements = screen.getAllByText('Tooltip content');
    expect(tooltipElements.length).toBeGreaterThan(0);
    expect(tooltipElements[0]).toBeInTheDocument();
  });

  it('renders with custom className when open', () => {
    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent className="custom-tooltip">Tooltip with custom class</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    
    // Check if custom class is applied - get the first element with the tooltip text
    const tooltipElements = screen.getAllByText('Tooltip with custom class');
    expect(tooltipElements[0]).toHaveClass('custom-tooltip');
  });

  it('handles side offset prop correctly', () => {
    const customOffset = 10;

    render(
      <TooltipProvider>
        <Tooltip defaultOpen>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent sideOffset={customOffset}>Tooltip with custom offset</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
    
    // Verify the tooltip is rendered
    const tooltipElements = screen.getAllByText('Tooltip with custom offset');
    expect(tooltipElements.length).toBeGreaterThan(0);
    expect(tooltipElements[0]).toBeInTheDocument();
  });

  it('supports controlled tooltip state', async () => {
    // Using a controlled component pattern
    function ControlledTooltip() {
      const [open, setOpen] = React.useState(false);
      
      return (
        <TooltipProvider>
          <Tooltip open={open}>
            <TooltipTrigger 
              data-testid="tooltip-trigger"
              onClick={() => setOpen(!open)}
            >
              Click me
            </TooltipTrigger>
            <TooltipContent>Controlled tooltip</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    const user = userEvent.setup();
    render(<ControlledTooltip />);
    
    // Initially tooltip shouldn't be visible
    expect(screen.queryByText('Controlled tooltip')).not.toBeInTheDocument();
    
    // Click to show tooltip
    await user.click(screen.getByTestId('tooltip-trigger'));
    
    // Wait for the tooltip to appear
    await waitFor(() => {
      const tooltipElements = screen.getAllByText('Controlled tooltip');
      expect(tooltipElements.length).toBeGreaterThan(0);
      expect(tooltipElements[0]).toBeInTheDocument();
    });
  });
}); 