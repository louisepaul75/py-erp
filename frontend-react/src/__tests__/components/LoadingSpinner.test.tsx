import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('renders with default (medium) size', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('h-8', 'w-8');
  });

  it('renders with small size', () => {
    const { container } = render(<LoadingSpinner size="sm" />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('h-4', 'w-4');
  });

  it('renders with large size', () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('h-12', 'w-12');
  });

  it('has correct border styling', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toHaveClass('border-t-2', 'border-b-2', 'border-primary');
  });

  it('is wrapped in a flex container with centered content', () => {
    const { container } = render(<LoadingSpinner />);
    
    const wrapperElement = container.firstChild;
    expect(wrapperElement).toHaveClass('flex', 'justify-center', 'items-center');
  });
}); 