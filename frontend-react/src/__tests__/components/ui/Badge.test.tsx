import React from 'react';
import { render, screen } from '@testing-library/react';
import { Badge, badgeVariants } from '@/components/ui/badge';

describe('Badge component', () => {
  it('renders correctly with default props', () => {
    render(<Badge>Test Badge</Badge>);
    const badge = screen.getByText('Test Badge');
    
    expect(badge).toBeInTheDocument();
    // Check that default variant class is applied
    expect(badge).toHaveClass('bg-primary');
  });
  
  it('renders with secondary variant', () => {
    render(<Badge variant="secondary">Secondary Badge</Badge>);
    const badge = screen.getByText('Secondary Badge');
    
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-secondary');
  });
  
  it('renders with destructive variant', () => {
    render(<Badge variant="destructive">Destructive Badge</Badge>);
    const badge = screen.getByText('Destructive Badge');
    
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-destructive');
  });
  
  it('renders with outline variant', () => {
    render(<Badge variant="outline">Outline Badge</Badge>);
    const badge = screen.getByText('Outline Badge');
    
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('text-foreground');
    // Outline doesn't have a bg class
    expect(badge).not.toHaveClass('bg-primary');
  });
  
  it('renders with amber variant', () => {
    render(<Badge variant="amber">Amber Badge</Badge>);
    const badge = screen.getByText('Amber Badge');
    
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-amber-500');
  });
  
  it('applies additional className prop correctly', () => {
    render(<Badge className="custom-class">Custom Badge</Badge>);
    const badge = screen.getByText('Custom Badge');
    
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('custom-class');
    // Should still have the default variant classes
    expect(badge).toHaveClass('bg-primary');
  });
  
  it('passes additional props to the div element', () => {
    render(<Badge data-testid="test-badge" id="unique-id">Props Badge</Badge>);
    const badge = screen.getByTestId('test-badge');
    
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveAttribute('id', 'unique-id');
  });
  
  it('badgeVariants function returns expected classes', () => {
    // Test the utility function directly
    expect(badgeVariants({ variant: 'default' })).toContain('bg-primary');
    expect(badgeVariants({ variant: 'secondary' })).toContain('bg-secondary');
    expect(badgeVariants({ variant: 'destructive' })).toContain('bg-destructive');
    expect(badgeVariants({ variant: 'outline' })).toContain('text-foreground');
    expect(badgeVariants({ variant: 'amber' })).toContain('bg-amber-500');
  });
}); 