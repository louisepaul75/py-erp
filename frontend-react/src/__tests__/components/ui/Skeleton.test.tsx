import React from 'react';
import { render, screen } from '@testing-library/react';
import { Skeleton } from '@/components/ui/skeleton';

describe('Skeleton Component', () => {
  it('renders without crashing', () => {
    render(<Skeleton data-testid="skeleton" />);
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toBeInTheDocument();
  });

  it('applies default classes', () => {
    render(<Skeleton data-testid="skeleton" />);
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveClass('animate-pulse');
    expect(skeleton).toHaveClass('rounded-md');
    expect(skeleton).toHaveClass('bg-primary/10');
  });

  it('applies custom classes', () => {
    render(<Skeleton className="custom-class h-20 w-40" data-testid="skeleton" />);
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveClass('custom-class');
    expect(skeleton).toHaveClass('h-20');
    expect(skeleton).toHaveClass('w-40');
    
    // Default classes should still be applied
    expect(skeleton).toHaveClass('animate-pulse');
    expect(skeleton).toHaveClass('rounded-md');
    expect(skeleton).toHaveClass('bg-primary/10');
  });

  it('passes through custom props', () => {
    render(
      <Skeleton 
        data-testid="skeleton" 
        aria-label="Loading content"
        role="progressbar"
      />
    );
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveAttribute('aria-label', 'Loading content');
    expect(skeleton).toHaveAttribute('role', 'progressbar');
  });

  it('renders with children', () => {
    render(
      <Skeleton data-testid="skeleton">
        <div data-testid="skeleton-child">Child content</div>
      </Skeleton>
    );
    
    const skeleton = screen.getByTestId('skeleton');
    const child = screen.getByTestId('skeleton-child');
    
    expect(skeleton).toBeInTheDocument();
    expect(child).toBeInTheDocument();
    expect(child).toHaveTextContent('Child content');
  });

  it('works as a text placeholder', () => {
    render(
      <div>
        <h2>Title</h2>
        <Skeleton className="h-4 w-[250px]" data-testid="skeleton-line-1" />
        <Skeleton className="h-4 w-[200px] mt-2" data-testid="skeleton-line-2" />
        <Skeleton className="h-4 w-[150px] mt-2" data-testid="skeleton-line-3" />
      </div>
    );
    
    expect(screen.getByTestId('skeleton-line-1')).toBeInTheDocument();
    expect(screen.getByTestId('skeleton-line-2')).toBeInTheDocument();
    expect(screen.getByTestId('skeleton-line-3')).toBeInTheDocument();
  });

  it('works as an image placeholder', () => {
    const { container } = render(
      <div>
        <Skeleton className="h-[200px] w-[200px] rounded-xl" data-testid="skeleton-image" />
      </div>
    );
    
    const skeleton = screen.getByTestId('skeleton-image');
    expect(skeleton).toBeInTheDocument();
    expect(skeleton).toHaveClass('h-[200px]');
    expect(skeleton).toHaveClass('w-[200px]');
    expect(skeleton).toHaveClass('rounded-xl');
  });
}); 