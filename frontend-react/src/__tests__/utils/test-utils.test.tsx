import React from 'react';
import { render, screen } from './test-utils';
import '@testing-library/jest-dom';

describe('custom render', () => {
  it('renders components correctly', () => {
    const TestComponent = () => <div data-testid="test-component">Test Content</div>;
    
    render(<TestComponent />);
    
    expect(screen.getByTestId('test-component')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
}); 