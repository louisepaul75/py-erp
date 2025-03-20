import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TouchFeedback } from '@/components/TouchFeedback';

describe('TouchFeedback', () => {
  it('renders children correctly', () => {
    render(
      <TouchFeedback>
        <div data-testid="child">Test Content</div>
      </TouchFeedback>
    );
    
    expect(screen.getByTestId('child')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <TouchFeedback className="custom-class">
        Test Content
      </TouchFeedback>
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('calls onClick when clicked', () => {
    const mockOnClick = jest.fn();
    
    render(
      <TouchFeedback onClick={mockOnClick}>
        Clickable Content
      </TouchFeedback>
    );
    
    fireEvent.click(screen.getByText('Clickable Content'));
    
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const mockOnClick = jest.fn();
    
    render(
      <TouchFeedback onClick={mockOnClick} disabled={true}>
        Disabled Content
      </TouchFeedback>
    );
    
    fireEvent.click(screen.getByText('Disabled Content'));
    
    expect(mockOnClick).not.toHaveBeenCalled();
  });

  it('applies disabled styles when disabled', () => {
    const { container } = render(
      <TouchFeedback disabled={true}>
        Disabled Content
      </TouchFeedback>
    );
    
    expect(container.firstChild).toHaveClass('opacity-50');
    expect(container.firstChild).toHaveClass('cursor-not-allowed');
  });

  it('handles touch events correctly', () => {
    const { container } = render(
      <TouchFeedback activeClassName="active-state">
        Touch Content
      </TouchFeedback>
    );
    
    // Simulate touch start
    fireEvent.touchStart(container.firstChild as Element);
    expect(container.firstChild).toHaveClass('active-state');
    
    // Simulate touch end
    fireEvent.touchEnd(container.firstChild as Element);
    expect(container.firstChild).not.toHaveClass('active-state');
  });

  it('handles touch cancel events correctly', () => {
    const { container } = render(
      <TouchFeedback activeClassName="active-state">
        Touch Content
      </TouchFeedback>
    );
    
    // Simulate touch start
    fireEvent.touchStart(container.firstChild as Element);
    expect(container.firstChild).toHaveClass('active-state');
    
    // Simulate touch cancel
    fireEvent.touchCancel(container.firstChild as Element);
    expect(container.firstChild).not.toHaveClass('active-state');
  });

  it('adds correct accessibility attributes when clickable', () => {
    const { container } = render(
      <TouchFeedback onClick={() => {}}>
        Accessible Content
      </TouchFeedback>
    );
    
    expect(container.firstChild).toHaveAttribute('role', 'button');
    expect(container.firstChild).toHaveAttribute('tabIndex', '0');
  });

  it('does not add accessibility attributes when not clickable', () => {
    const { container } = render(
      <TouchFeedback>
        Non-clickable Content
      </TouchFeedback>
    );
    
    expect(container.firstChild).not.toHaveAttribute('role');
    expect(container.firstChild).not.toHaveAttribute('tabIndex');
  });
}); 