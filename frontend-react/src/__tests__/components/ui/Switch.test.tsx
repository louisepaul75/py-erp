import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Switch } from '@/components/ui/switch';
import { act } from 'react-dom/test-utils';

// Mock the cn function from utils
jest.mock('@/lib/utils', () => ({
  cn: (...inputs: any[]) => inputs.filter(Boolean).join(' '),
}));

describe('Switch Component', () => {
  it('renders correctly with default props', () => {
    render(<Switch data-testid="test-switch" />);
    
    const switchElement = screen.getByTestId('test-switch');
    expect(switchElement).toBeInTheDocument();
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    expect(switchElement).toHaveClass('peer inline-flex h-6 w-11');
  });

  it('renders with custom className', () => {
    render(<Switch data-testid="test-switch" className="custom-class" />);
    
    const switchElement = screen.getByTestId('test-switch');
    expect(switchElement).toHaveClass('custom-class');
  });

  it('can be checked and unchecked', async () => {
    const user = userEvent.setup();
    render(<Switch data-testid="test-switch" />);
    
    const switchElement = screen.getByTestId('test-switch');
    
    // Initial state should be unchecked
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    
    // Click to check
    await user.click(switchElement);
    expect(switchElement).toHaveAttribute('data-state', 'checked');
    
    // Click to uncheck
    await user.click(switchElement);
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
  });

  it('can be disabled', () => {
    render(<Switch data-testid="test-switch" disabled />);
    
    const switchElement = screen.getByTestId('test-switch');
    expect(switchElement).toBeDisabled();
    expect(switchElement).toHaveClass('disabled:cursor-not-allowed disabled:opacity-50');
  });

  it('responds to keyboard interaction', async () => {
    const user = userEvent.setup();
    render(<Switch data-testid="test-switch" />);
    
    const switchElement = screen.getByTestId('test-switch');
    
    // Focus the element
    switchElement.focus();
    
    // Initial state should be unchecked
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    
    // Press space to check
    await user.keyboard(' ');
    expect(switchElement).toHaveAttribute('data-state', 'checked');
    
    // Press space to uncheck
    await user.keyboard(' ');
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
  });

  it('calls onChange when clicked', async () => {
    const handleChange = jest.fn();
    const user = userEvent.setup();
    
    render(<Switch data-testid="test-switch" onCheckedChange={handleChange} />);
    
    const switchElement = screen.getByTestId('test-switch');
    
    // Click to toggle
    await user.click(switchElement);
    
    // onChange should be called with true (checked)
    expect(handleChange).toHaveBeenCalledWith(true);
    
    // Click again to toggle
    await user.click(switchElement);
    
    // onChange should be called with false (unchecked)
    expect(handleChange).toHaveBeenCalledWith(false);
  });

  it('can be controlled with checked prop', async () => {
    const user = userEvent.setup();
    const { rerender } = render(<Switch data-testid="test-switch" checked={false} />);
    
    const switchElement = screen.getByTestId('test-switch');
    
    // Initial state should match checked prop
    expect(switchElement).toHaveAttribute('data-state', 'unchecked');
    
    // Rerender with checked=true
    rerender(<Switch data-testid="test-switch" checked={true} />);
    
    // State should update to checked
    expect(switchElement).toHaveAttribute('data-state', 'checked');
    
    // Clicking should not change the state in controlled mode without onChange
    await user.click(switchElement);
    expect(switchElement).toHaveAttribute('data-state', 'checked');
  });

  it('renders with appropriate ARIA attributes', () => {
    render(<Switch data-testid="test-switch" aria-label="Toggle feature" />);
    
    const switchElement = screen.getByTestId('test-switch');
    expect(switchElement).toHaveAttribute('role', 'switch');
    expect(switchElement).toHaveAttribute('aria-label', 'Toggle feature');
    expect(switchElement).toHaveAttribute('aria-checked', 'false');
  });

  it('can be focused programmatically', () => {
    render(<Switch data-testid="test-switch" />);
    
    const switchElement = screen.getByTestId('test-switch');
    
    // Should not be focused initially
    expect(switchElement).not.toHaveFocus();
    
    // Focus the element
    act(() => {
      switchElement.focus();
    });
    
    // Should now be focused
    expect(switchElement).toHaveFocus();
  });

  it('renders thumb with correct positioning classes', () => {
    const { container, rerender } = render(<Switch data-testid="test-switch" checked={false} />);
    
    // Find the thumb element (child of the root)
    const thumb = container.querySelector('[class*="data-[state=unchecked]:translate-x-0"]');
    expect(thumb).toBeInTheDocument();
    
    // Rerender with checked=true
    rerender(<Switch data-testid="test-switch" checked={true} />);
    
    // Thumb should have the checked position class
    const checkedThumb = container.querySelector('[class*="data-[state=checked]:translate-x-5"]');
    expect(checkedThumb).toBeInTheDocument();
  });
}); 