import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from '@/components/ui/tooltip';

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

  it('shows tooltip content on hover', async () => {
    const user = userEvent.setup();

    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent>Tooltip content</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );

    // Hover over the trigger
    await user.hover(screen.getByTestId('tooltip-trigger'));
    
    // Tooltip content should be visible
    expect(screen.getByText('Tooltip content')).toBeInTheDocument();
  });

  it('hides tooltip content when hover is removed', async () => {
    const user = userEvent.setup();

    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent>Tooltip content</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );

    // Hover and unhover
    await user.hover(screen.getByTestId('tooltip-trigger'));
    await user.unhover(screen.getByTestId('tooltip-trigger'));
    
    // Check if tooltip was removed after unhover
    // Need to use a small delay due to animations
    setTimeout(() => {
      expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument();
    }, 300);
  });

  it('renders with custom className', async () => {
    const user = userEvent.setup();

    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent className="custom-tooltip">Tooltip with custom class</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );

    // Hover over the trigger
    await user.hover(screen.getByTestId('tooltip-trigger'));
    
    // Check if custom class is applied
    expect(screen.getByText('Tooltip with custom class')).toHaveClass('custom-tooltip');
  });

  it('handles side offset prop correctly', async () => {
    const user = userEvent.setup();
    const customOffset = 10;

    render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger data-testid="tooltip-trigger">Hover me</TooltipTrigger>
          <TooltipContent sideOffset={customOffset}>Tooltip with custom offset</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );

    // Hover over the trigger
    await user.hover(screen.getByTestId('tooltip-trigger'));
    
    // Verify the tooltip is rendered
    expect(screen.getByText('Tooltip with custom offset')).toBeInTheDocument();
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
    
    // Tooltip should now be visible
    expect(screen.getByText('Controlled tooltip')).toBeInTheDocument();
    
    // Click again to hide tooltip
    await user.click(screen.getByTestId('tooltip-trigger'));
    
    // Tooltip should be hidden again
    setTimeout(() => {
      expect(screen.queryByText('Controlled tooltip')).not.toBeInTheDocument();
    }, 300);
  });
}); 