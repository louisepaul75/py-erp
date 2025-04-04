import React from 'react';
import { render, screen } from '@testing-library/react';
import Footer from './Footer';

describe('Footer', () => {
  it('renders footer text and link', () => {
    render(<Footer />);
    expect(screen.getByText(/© \\d{4} pyERP/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /v\S+ (?:success|warning|error)/ })).toBeInTheDocument();
  });

  it('shows loading spinner initially', () => {
    // ... existing code ...
  });
}); 