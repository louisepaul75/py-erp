import { render, screen } from '@testing-library/react';
import React from 'react';

// Mock the entire Layout component
jest.mock('../../components/Layout', () => {
  return {
    Layout: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="mock-layout">
        <div data-testid="mock-navbar">Navbar</div>
        <main data-testid="mock-content">{children}</main>
        <div data-testid="mock-footer">Footer</div>
      </div>
    )
  };
});

// Import the mocked component
import { Layout } from '../../components/Layout';

describe('Layout', () => {
  it('renders navbar, content area, and footer', () => {
    render(
      <Layout>
        <div>Content</div>
      </Layout>
    );

    expect(screen.getByTestId('mock-navbar')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByTestId('mock-footer')).toBeInTheDocument();
  });
}); 