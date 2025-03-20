import React from 'react';
import { render, screen } from '@testing-library/react';
import { Separator } from '@/components/ui/separator';

describe('Separator component', () => {
  it('renders horizontal separator by default', () => {
    render(<Separator data-testid="separator" />);
    const separator = screen.getByTestId('separator');
    
    expect(separator).toBeInTheDocument();
    expect(separator).toHaveClass('h-[1px]', 'w-full');
    expect(separator).not.toHaveClass('h-full', 'w-[1px]');
  });
  
  it('renders vertical separator when specified', () => {
    render(<Separator orientation="vertical" data-testid="separator" />);
    const separator = screen.getByTestId('separator');
    
    expect(separator).toBeInTheDocument();
    expect(separator).toHaveClass('h-full', 'w-[1px]');
    expect(separator).not.toHaveClass('h-[1px]', 'w-full');
  });
  
  it('applies custom className correctly', () => {
    render(<Separator className="custom-class" data-testid="separator" />);
    const separator = screen.getByTestId('separator');
    
    expect(separator).toBeInTheDocument();
    expect(separator).toHaveClass('custom-class');
    // Still has the default classes
    expect(separator).toHaveClass('bg-border');
  });
  
  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLDivElement>();
    render(<Separator ref={ref} data-testid="separator" />);
    
    expect(ref.current).not.toBeNull();
    expect(ref.current).toBe(screen.getByTestId('separator'));
  });
  
  it('sets correct data-orientation attribute', () => {
    render(<Separator orientation="horizontal" data-testid="separator" />);
    const separator = screen.getByTestId('separator');
    
    // Check that orientation is properly passed through to data-orientation
    expect(separator).toHaveAttribute('data-orientation', 'horizontal');
  });
  
  it('handles decorative prop correctly', () => {
    // When decorative is false
    render(<Separator decorative={false} data-testid="separator-non-decorative" />);
    const nonDecorativeSeparator = screen.getByTestId('separator-non-decorative');
    expect(nonDecorativeSeparator).not.toHaveAttribute('role', 'none');
    
    // When decorative is true (default)
    render(<Separator decorative={true} data-testid="separator-decorative" />);
    const decorativeSeparator = screen.getByTestId('separator-decorative');
    expect(decorativeSeparator).toHaveAttribute('role', 'none');
  });
  
  it('passes additional props to the component', () => {
    render(<Separator data-testid="separator" id="custom-id" aria-label="divider" />);
    const separator = screen.getByTestId('separator');
    
    expect(separator).toHaveAttribute('id', 'custom-id');
    expect(separator).toHaveAttribute('aria-label', 'divider');
  });
}); 