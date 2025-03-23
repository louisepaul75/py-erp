import React from 'react';
import { render } from '@testing-library/react';
import RootLayout from '../../app/layout';

// Mock the components used in the layout
jest.mock('@/components/Navbar', () => ({
  Navbar: () => <div data-testid="navbar-mock">Navbar Mock</div>
}));

jest.mock('@/components/Footer', () => ({
  Footer: () => <div data-testid="footer-mock">Footer Mock</div>
}));

jest.mock('../../app/providers', () => ({
  Providers: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="providers-mock">{children}</div>
  )
}));

// Mock document.documentElement.lang since jsdom doesn't support it properly
Object.defineProperty(document.documentElement, 'lang', {
  get: jest.fn(() => 'de'),
  set: jest.fn()
});

describe('RootLayout', () => {
  it('renders the layout structure with navbar, content area, and footer', () => {
    const { getByTestId, getByText } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    );

    // Check that the mocked components are rendered
    expect(getByTestId('navbar-mock')).toBeInTheDocument();
    expect(getByTestId('footer-mock')).toBeInTheDocument();
    expect(getByTestId('providers-mock')).toBeInTheDocument();
    
    // Check that the children are rendered
    expect(getByText('Test Content')).toBeInTheDocument();
    
    // Verify that the lang attribute is set to 'de'
    expect(document.documentElement.lang).toBe('de');
  });
}); 