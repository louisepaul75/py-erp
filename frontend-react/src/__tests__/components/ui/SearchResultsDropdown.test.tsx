import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchResultsDropdown } from '@/components/ui/search-results-dropdown';
import { SearchResult } from '@/hooks/useGlobalSearch';

// Mock the cn function from utils
jest.mock('@/lib/utils', () => ({
  cn: (...inputs: any[]) => inputs.filter(Boolean).join(' '),
}));

describe('SearchResultsDropdown Component', () => {
  const mockOnSelect = jest.fn();
  
  const mockResults: SearchResult[] = [
    {
      id: '1',
      type: 'customer',
      name: 'John Doe',
      customer_number: 'C12345',
    },
    {
      id: '2',
      type: 'sales_record',
      record_number: 'S67890',
      record_type: 'Invoice',
      customer: 'Jane Smith',
    },
    {
      id: '3',
      type: 'parent_product',
      sku: 'P101',
    },
    {
      id: '4',
      type: 'variant_product',
      sku: 'V202',
      legacy_sku: 'L202',
    },
    {
      id: '5',
      type: 'box_slot',
      box_code: 'BOX1',
      slot_code: 'SLOT1',
    },
    {
      id: '6',
      type: 'storage_location',
      legacy_id: 'L303',
      location_code: 'STORE1',
    },
  ];

  it('renders nothing when open is false', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={false}
        onSelect={mockOnSelect}
      />
    );
    
    // Should not render any content when closed
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
  });

  it('renders loading state correctly', () => {
    render(
      <SearchResultsDropdown
        results={[]}
        isLoading={true}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    expect(screen.getByText('Suchen...')).toBeInTheDocument();
  });

  it('renders "no results" message when results array is empty', () => {
    render(
      <SearchResultsDropdown
        results={[]}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    expect(screen.getByText('Keine Ergebnisse gefunden')).toBeInTheDocument();
  });

  it('renders results list correctly', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Check if all results are rendered
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Kunde #C12345')).toBeInTheDocument();
    expect(screen.getByText('Kunde')).toBeInTheDocument();
    
    expect(screen.getByText('Invoice #S67890 - Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Verkaufsbeleg')).toBeInTheDocument();
    
    expect(screen.getByText('Gruppe #P101')).toBeInTheDocument();
    expect(screen.getByText('Produktgruppe')).toBeInTheDocument();
    
    expect(screen.getByText('Artikel #V202 (L202)')).toBeInTheDocument();
    expect(screen.getByText('Produkt')).toBeInTheDocument();
    
    expect(screen.getByText('BOX1 - SLOT1')).toBeInTheDocument();
    expect(screen.getByText('Box')).toBeInTheDocument();
    
    expect(screen.getByText('Lager #L303 - STORE1')).toBeInTheDocument();
    expect(screen.getByText('Lager')).toBeInTheDocument();
  });

  it('calls onSelect when a result item is clicked', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Click on the first result
    fireEvent.click(screen.getByText('John Doe'));
    
    // Check if onSelect was called with the correct result
    expect(mockOnSelect).toHaveBeenCalledWith(mockResults[0]);
  });

  it('renders with custom className', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
        className="custom-class"
      />
    );
    
    // Check if the Card component has the custom class
    const card = document.querySelector('.absolute.custom-class');
    expect(card).toBeInTheDocument();
  });

  it('handles unknown result types gracefully', () => {
    const unknownTypeResult: SearchResult[] = [
      {
        id: '7',
        type: 'unknown_type' as any,
        name: 'Unknown Item',
      },
    ];
    
    render(
      <SearchResultsDropdown
        results={unknownTypeResult}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Should display the name and the type as is
    expect(screen.getByText('Unknown Item')).toBeInTheDocument();
    expect(screen.getByText('unknown_type')).toBeInTheDocument();
  });

  it('handles missing name/identifier in results gracefully', () => {
    const missingNameResult: SearchResult[] = [
      {
        id: '8',
        type: 'customer',
        // No name or identifiers provided
      },
    ];
    
    render(
      <SearchResultsDropdown
        results={missingNameResult}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Should display "Unbekannt" as fallback
    expect(screen.getByText('Unbekannt')).toBeInTheDocument();
  });
}); 