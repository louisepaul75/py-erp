import React from 'react';
import { render, screen } from '@testing-library/react';
import NotFound from '../../app/not-found';

describe('NotFound', () => {
  it('renders the 404 message', () => {
    render(<NotFound />);
    
    // Check for the main elements
    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('This page could not be found.')).toBeInTheDocument();
    
    // Check for the home link
    const homeLink = screen.getByRole('link', { name: /return home/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute('href', '/');
  });
}); 