import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('renders without crashing', () => {
    render(<LoadingSpinner data-testid="spinner" />);
    
    const spinner = screen.getByTestId('spinner');
    expect(spinner).toBeInTheDocument();
  });

  it('renders with the default medium size when no size is specified', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('h-8');
    expect(spinnerElement).toHaveClass('w-8');
  });

  it('renders with small size when size="sm" is specified', () => {
    const { container } = render(<LoadingSpinner size="sm" />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('h-4');
    expect(spinnerElement).toHaveClass('w-4');
  });

  it('renders with medium size when size="md" is specified', () => {
    const { container } = render(<LoadingSpinner size="md" />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('h-8');
    expect(spinnerElement).toHaveClass('w-8');
  });

  it('renders with large size when size="lg" is specified', () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('h-12');
    expect(spinnerElement).toHaveClass('w-12');
  });

  it('applies the animation class for the spinner animation', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('animate-spin');
  });

  it('applies the border classes for the spinner appearance', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('border-t-2');
    expect(spinnerElement).toHaveClass('border-b-2');
    expect(spinnerElement).toHaveClass('border-primary');
  });

  it('renders with a container that has flex centering classes', () => {
    const { container } = render(<LoadingSpinner />);
    
    const containerElement = container.firstChild;
    expect(containerElement).toHaveClass('flex');
    expect(containerElement).toHaveClass('justify-center');
    expect(containerElement).toHaveClass('items-center');
  });

  it('accepts and forwards a data-testid prop', () => {
    const testId = 'loading-spinner';
    render(<LoadingSpinner data-testid={testId} />);
    
    const spinner = screen.getByTestId(testId);
    expect(spinner).toBeInTheDocument();
  });
}); 