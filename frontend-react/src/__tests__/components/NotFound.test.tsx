import React from 'react';
import { render, screen } from '@testing-library/react';
import NotFound from '../../app/not-found';

describe('NotFound', () => {
  it('renders the 404 message', () => {
    render(<NotFound />);
    
    // Check for the main elements
    expect(screen.getByText('404 - Seite nicht gefunden')).toBeInTheDocument();
    expect(screen.getByText('Die angeforderte Seite existiert nicht.')).toBeInTheDocument();
    
    // Check for the home link
    const homeLink = screen.getByRole('link', { name: /zurück zur startseite/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute('href', '/');
  });
}); 