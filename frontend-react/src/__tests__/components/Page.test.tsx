import React from 'react';
import { render } from '@testing-library/react';
import Home from '../../app/page';

// Mock the redirect function from next/navigation
jest.mock('next/navigation', () => ({
  redirect: jest.fn(),
}));

describe('Home Page', () => {
  it('should redirect to the dashboard page', () => {
    const { redirect } = require('next/navigation');
    
    // Render the component
    render(<Home />);
    
    // Check if redirect was called with the correct path
    expect(redirect).toHaveBeenCalledWith('/dashboard');
  });
}); 