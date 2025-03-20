import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Switch } from '@/components/ui/switch';
import userEvent from '@testing-library/user-event';

// Mock Radix UI components
jest.mock('@radix-ui/react-switch', () => ({
  Root: ({ className, checked, onCheckedChange, disabled, children, ...props }: any) => (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      className={className}
      onClick={() => !disabled && onCheckedChange && onCheckedChange(!checked)}
      data-state={checked ? 'checked' : 'unchecked'}
      {...props}
    >
      {children}
    </button>
  ),
  Thumb: ({ className }: any) => <span className={className} data-testid="switch-thumb" />,
}));

describe('Switch', () => {
  it('renders correctly', () => {
    render(<Switch />);
    
    // Check if the switch is rendered
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toBeInTheDocument();
    
    // Check if the thumb is rendered
    const thumb = screen.getByTestId('switch-thumb');
    expect(thumb).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const customClass = 'custom-switch-class';
    render(<Switch className={customClass} />);
    
    const switchElement = screen.getByRole('switch');
    expect(switchElement).toHaveClass(customClass);
  });

  it('can be checked and unchecked', async () => {
    const handleChange = jest.fn();
    
    // Render unchecked switch with its own container
    const uncheckedRender = render(<Switch checked={false} onCheckedChange={handleChange} />);
    
    const switchElement = uncheckedRender.getByRole('switch');
    
    // Initial state is unchecked
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    expect(switchElement).toHaveAttribute('aria-checked', 'false');
    
    // Click to check
    fireEvent.click(switchElement);
    expect(handleChange).toHaveBeenCalledWith(true);
    
    // Clean up to avoid test interference
    uncheckedRender.unmount();
    
    // Render checked state in a separate render
    const checkedRender = render(<Switch checked={true} onCheckedChange={handleChange} />);
    
    // Now it should be checked
    const updatedSwitch = checkedRender.getByRole('switch');
    expect(updatedSwitch).toHaveAttribute('data-state', 'checked');
    expect(updatedSwitch).toHaveAttribute('aria-checked', 'true');
  });

  it('respects the disabled state', async () => {
    const handleChange = jest.fn();
    render(<Switch disabled checked={false} onCheckedChange={handleChange} />);
    
    const switchElement = screen.getByRole('switch');
    
    // Verify it has disabled attribute
    expect(switchElement).toBeDisabled();
    
    // Click should not trigger onChange
    fireEvent.click(switchElement);
    expect(handleChange).not.toHaveBeenCalled();
  });

  it('passes additional props to the underlying component', () => {
    const testId = 'test-switch';
    render(<Switch data-testid={testId} />);
    
    const switchElement = screen.getByTestId(testId);
    expect(switchElement).toBeInTheDocument();
  });

  it('has the correct styles based on state', () => {
    // Test unchecked state
    const uncheckedRender = render(<Switch checked={false} />);
    let switchElement = uncheckedRender.getByRole('switch');
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    expect(switchElement.className).toContain('data-[state=unchecked]:bg-input');
    
    // Clean up to avoid test interference
    uncheckedRender.unmount();
    
    // Test checked state
    const checkedRender = render(<Switch checked={true} />);
    switchElement = checkedRender.getByRole('switch');
    expect(switchElement).toHaveAttribute('data-state', 'checked');
    expect(switchElement.className).toContain('data-[state=checked]:bg-primary');
  });
}); 