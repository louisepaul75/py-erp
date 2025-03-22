import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import InventoryManagement from '../../../components/ui/article-page';

// Mock the tab components
jest.mock('@/components/bilder-tab', () => {
  return function MockBilderTab() {
    return <div data-testid="bilder-tab">Bilder Tab Content</div>;
  };
});

jest.mock('@/components/gewogen-tab', () => {
  return function MockGewogenTab() {
    return <div data-testid="gewogen-tab">Gewogen Tab Content</div>;
  };
});

jest.mock('@/components/lagerorte-tab', () => {
  return function MockLagerorteTab() {
    return <div data-testid="lagerorte-tab">Lagerorte Tab Content</div>;
  };
});

jest.mock('@/components/umsatze-tab', () => {
  return function MockUmsatzeTab() {
    return <div data-testid="umsatze-tab">Umsatze Tab Content</div>;
  };
});

jest.mock('@/components/bewegungen-tab', () => {
  return function MockBewegungenTab() {
    return <div data-testid="bewegungen-tab">Bewegungen Tab Content</div>;
  };
});

jest.mock('@/components/teile-tab', () => {
  return function MockTeileTab() {
    return <div data-testid="teile-tab">Teile Tab Content</div>;
  };
});

describe('InventoryManagement Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  test('renders the component with initial state', async () => {
    render(<InventoryManagement />);
    
    // Check that the component renders with the expected initial state
    expect(screen.getByText('Artikel')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Suche...')).toBeInTheDocument();
    
    // Verify the mock products are displayed
    await waitFor(() => {
      expect(screen.getByText('Zinnfigur Hirte mit Schaf')).toBeInTheDocument();
      expect(screen.getByText('Zinnfigur Engel')).toBeInTheDocument();
      expect(screen.getByText('Zinnfigur Krippe')).toBeInTheDocument();
    });
  });

  test('allows searching for products', async () => {
    render(<InventoryManagement />);
    
    // Get the search input and type in it
    const searchInput = screen.getByPlaceholderText('Suche...');
    fireEvent.change(searchInput, { target: { value: 'Engel' } });
    
    // Verify filtered results are displayed
    await waitFor(() => {
      expect(screen.getByText('Zinnfigur Engel')).toBeInTheDocument();
      expect(screen.queryByText('Zinnfigur Hirte mit Schaf')).not.toBeInTheDocument();
      expect(screen.queryByText('Zinnfigur Krippe')).not.toBeInTheDocument();
    });
  });

  test('allows selecting a product from the list', async () => {
    render(<InventoryManagement />);
    
    // Wait for products to load
    await waitFor(() => {
      expect(screen.getByText('Zinnfigur Engel')).toBeInTheDocument();
    });
    
    // Click on a product
    fireEvent.click(screen.getByText('Zinnfigur Engel'));
    
    // Verify the product details are shown
    expect(screen.getByText('Artikel 218301: Zinnfigur Engel')).toBeInTheDocument();
  });

  test('allows toggling the sidebar', () => {
    render(<InventoryManagement />);
    
    // Initially, the sidebar should be visible
    expect(screen.getByTestId('sidebar')).toHaveClass('block');
    
    // Click the toggle sidebar button
    fireEvent.click(screen.getByTestId('toggle-sidebar'));
    
    // Sidebar should now be hidden
    expect(screen.getByTestId('sidebar')).toHaveClass('hidden');
    
    // Click again to show
    fireEvent.click(screen.getByTestId('toggle-sidebar'));
    
    // Sidebar should be visible again
    expect(screen.getByTestId('sidebar')).toHaveClass('block');
  });

  test('allows switching between tabs', async () => {
    render(<InventoryManagement />);
    
    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText('Details')).toBeInTheDocument();
    });
    
    // Check that we can switch to different tabs
    fireEvent.click(screen.getByRole('tab', { name: 'Bilder' }));
    expect(screen.getByTestId('bilder-tab')).toBeInTheDocument();
    
    fireEvent.click(screen.getByRole('tab', { name: 'Lagerorte' }));
    expect(screen.getByTestId('lagerorte-tab')).toBeInTheDocument();
    
    fireEvent.click(screen.getByRole('tab', { name: 'Gewogen' }));
    expect(screen.getByTestId('gewogen-tab')).toBeInTheDocument();
  });

  test('handles error state properly', async () => {
    // Mock console.error to avoid test output noise
    const originalError = console.error;
    console.error = jest.fn();
    
    // Force an error state
    jest.spyOn(React, 'useState').mockImplementationOnce(() => [true, jest.fn()]);
    jest.spyOn(React, 'useState').mockImplementationOnce(() => ["Error loading products", jest.fn()]);
    
    render(<InventoryManagement />);
    
    // Verify the error message is displayed
    expect(screen.getByText('Error loading products')).toBeInTheDocument();
    
    // Restore console.error
    console.error = originalError;
  });
}); 