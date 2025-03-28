import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResponsiveCard } from '@/components/ResponsiveCard';
import { useScreenSize } from '@/utils/responsive';
import { TouchFeedback } from '@/components/TouchFeedback';

// Mock dependencies
jest.mock('@/utils/responsive', () => ({
  useScreenSize: jest.fn(),
}));

jest.mock('@/components/TouchFeedback', () => ({
  TouchFeedback: jest.fn(({ children, className, onClick }) => (
    <div 
      data-testid="touchfeedback-mock" 
      className={className} 
      onClick={onClick}
    >
      {children}
    </div>
  )),
}));

describe('ResponsiveCard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Default to mobile view
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: false,
      isTablet: false,
      isDesktop: true,
    });
  });

  it('renders title correctly', () => {
    render(<ResponsiveCard title="Test Card" />);
    expect(screen.getByText('Test Card')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(
      <ResponsiveCard 
        title="Test Card" 
        description="This is a test description"
      />
    );
    
    expect(screen.getByText('This is a test description')).toBeInTheDocument();
  });

  it('renders icon when provided', () => {
    const testIcon = <div data-testid="test-icon">Icon</div>;
    
    render(
      <ResponsiveCard 
        title="Test Card" 
        icon={testIcon}
      />
    );
    
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  it('renders children content when provided', () => {
    render(
      <ResponsiveCard title="Test Card">
        <div data-testid="child-content">Child Content</div>
      </ResponsiveCard>
    );
    
    expect(screen.getByTestId('child-content')).toBeInTheDocument();
  });

  it('renders footer when provided', () => {
    const footer = <div data-testid="footer-content">Footer Content</div>;
    
    render(
      <ResponsiveCard 
        title="Test Card" 
        footer={footer}
      />
    );
    
    expect(screen.getByTestId('footer-content')).toBeInTheDocument();
  });

  it('uses TouchFeedback when onClick is provided', () => {
    const handleClick = jest.fn();
    
    render(
      <ResponsiveCard 
        title="Clickable Card" 
        onClick={handleClick}
      />
    );
    
    expect(screen.getByTestId('touchfeedback-mock')).toBeInTheDocument();
    
    // Simplified expectation to avoid React 19 object structure issues
    expect(TouchFeedback).toHaveBeenCalled();
    
    // Verify that props were passed correctly by checking the onClick handler directly
    const mockCalls = (TouchFeedback as jest.Mock).mock.calls;
    expect(mockCalls.length).toBeGreaterThan(0);
    
    // Extract and check the onClick prop from the first argument of the first call
    const firstCallFirstArg = mockCalls[0][0];
    expect(firstCallFirstArg.onClick).toBe(handleClick);
  });

  it('does not use TouchFeedback when onClick is not provided', () => {
    render(<ResponsiveCard title="Non-clickable Card" />);
    
    expect(screen.queryByTestId('touchfeedback-mock')).not.toBeInTheDocument();
    expect(TouchFeedback).not.toHaveBeenCalled();
  });

  it('applies custom className', () => {
    const { container } = render(
      <ResponsiveCard 
        title="Styled Card" 
        className="custom-class"
      />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('applies mobile-specific styles when on mobile', () => {
    // Mock mobile view
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
    
    const { container } = render(
      <ResponsiveCard title="Mobile Card" />
    );
    
    // Check for mobile-specific padding
    expect(container.firstChild).toHaveClass('p-4');
  });

  it('applies desktop-specific styles when not on mobile', () => {
    // Mock desktop view
    (useScreenSize as jest.Mock).mockReturnValue({
      isMobile: false,
      isTablet: false,
      isDesktop: true,
    });
    
    const { container } = render(
      <ResponsiveCard title="Desktop Card" />
    );
    
    // Check for desktop-specific padding
    expect(container.firstChild).toHaveClass('p-6');
  });

  it('handles click events when onClick is provided', () => {
    const handleClick = jest.fn();
    
    render(
      <ResponsiveCard 
        title="Clickable Card" 
        onClick={handleClick}
      />
    );
    
    fireEvent.click(screen.getByTestId('touchfeedback-mock'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
}); 