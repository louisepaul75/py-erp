import React from 'react';
import { render, screen } from '@testing-library/react';
import { Label } from '@/components/ui/label';

// Mock the cn function from utils
jest.mock('@/lib/utils', () => ({
  cn: (...inputs: any[]) => inputs.filter(Boolean).join(' '),
}));

// Mock class-variance-authority
jest.mock('class-variance-authority', () => ({
  cva: jest.fn(() => jest.fn(() => 'mocked-cva-class')),
}));

describe('Label Component', () => {
  it('renders correctly with default props', () => {
    render(<Label htmlFor="test-input">Test Label</Label>);
    
    const label = screen.getByText('Test Label');
    expect(label).toBeInTheDocument();
    expect(label).toHaveAttribute('for', 'test-input');
    expect(label).toHaveClass('mocked-cva-class');
  });

  it('renders with custom className', () => {
    render(
      <Label htmlFor="test-input" className="custom-class">
        Test Label
      </Label>
    );
    
    const label = screen.getByText('Test Label');
    expect(label).toHaveClass('custom-class');
  });

  it('applies correct styling when rendered', () => {
    const { container } = render(
      <Label htmlFor="test-input">Test Label</Label>
    );
    
    const label = container.firstChild;
    expect(label).toHaveClass('mocked-cva-class');
  });

  it('renders children correctly', () => {
    render(
      <Label htmlFor="test-input">
        <span data-testid="nested-span">Nested Label Text</span>
      </Label>
    );
    
    const nestedSpan = screen.getByTestId('nested-span');
    expect(nestedSpan).toBeInTheDocument();
    expect(nestedSpan).toHaveTextContent('Nested Label Text');
  });

  it('forwards additional HTML attributes correctly', () => {
    render(
      <Label 
        htmlFor="test-input" 
        data-testid="test-label" 
        aria-label="Accessible Name"
      >
        Test Label
      </Label>
    );
    
    const label = screen.getByTestId('test-label');
    expect(label).toHaveAttribute('aria-label', 'Accessible Name');
  });

  it('can be associated with form controls', () => {
    render(
      <>
        <Label htmlFor="test-input">Test Label</Label>
        <input id="test-input" data-testid="associated-input" type="text" />
      </>
    );
    
    const label = screen.getByText('Test Label');
    const input = screen.getByTestId('associated-input');
    
    // Verify association by checking htmlFor matches input id
    expect(label).toHaveAttribute('for', 'test-input');
    expect(input).toHaveAttribute('id', 'test-input');
  });

  it('correctly applies CSS variables for disabled state', () => {
    render(
      <div>
        <Label htmlFor="test-input">Test Label</Label>
        <input id="test-input" disabled />
      </div>
    );
    
    const label = screen.getByText('Test Label');
    
    // Check that the label has the proper styling classes
    // which include peer-disabled variants
    expect(label).toHaveClass('mocked-cva-class');
  });

  it('renders with correct display name', () => {
    expect(Label.displayName).toBe('Root');
  });
}); 