import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchResultsDropdown } from '@/components/ui/search-results-dropdown';
import { SearchResult } from '@/hooks/useGlobalSearch';
import '@testing-library/jest-dom';

// Mock console.error and console.log to keep the test output clean
// and to capture logging for assertions
const originalError = console.error;
const originalLog = console.log;
let consoleErrors: string[] = [];
let consoleLogs: string[] = [];

beforeEach(() => {
  consoleErrors = [];
  consoleLogs = [];
  console.error = jest.fn((...args) => {
    consoleErrors.push(args.map(arg => String(arg)).join(' '));
  });
  console.log = jest.fn((...args) => {
    consoleLogs.push(args.map(arg => String(arg)).join(' '));
  });
});

afterEach(() => {
  console.error = originalError;
  console.log = originalLog;
});

// Mock sample data
const mockResults: SearchResult[] = [
  {
    id: 1,
    type: 'customer',
    name: 'Test Customer',
    customer_number: 'C001'
  },
  {
    id: 2,
    type: 'sales_record',
    record_number: 'S001',
    record_type: 'Invoice',
    customer: 'Test Customer'
  },
  {
    id: 3,
    type: 'variant_product',
    name: 'Test Product',
    sku: 'P001',
    legacy_sku: 'LP001'
  }
];

// Mock callbacks
const mockOnSelect = jest.fn();

describe('SearchResultsDropdown Component', () => {
  beforeEach(() => {
    mockOnSelect.mockClear();
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
    
    expect(screen.getByTestId('loading-state')).toHaveTextContent('Suchen...');
  });
  
  it('renders no results state correctly', () => {
    render(
      <SearchResultsDropdown
        results={[]}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    expect(screen.getByTestId('no-results')).toHaveTextContent('Keine Ergebnisse gefunden');
  });
  
  it('renders search results correctly', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Check first result (customer)
    expect(screen.getByTestId('result-name-1')).toHaveTextContent('Test Customer');
    expect(screen.getByTestId('result-subtitle-1')).toHaveTextContent('Kunde #C001');
    
    // Check second result (sales record)
    expect(screen.getByTestId('result-name-2')).toHaveTextContent('Test Customer');
    expect(screen.getByTestId('result-subtitle-2')).toHaveTextContent('Verkauf #S001');
    
    // Check third result (product)
    expect(screen.getByTestId('result-name-3')).toHaveTextContent('Test Product');
    expect(screen.getByTestId('result-subtitle-3')).toHaveTextContent('Artikel #P001 (LP001)');
  });
  
  it('handles click on search result correctly', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Click the first result
    fireEvent.click(screen.getByTestId('result-1'));
    
    expect(mockOnSelect).toHaveBeenCalledWith(mockResults[0]);
  });
  
  it('does not render anything when open is false', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={false}
        onSelect={mockOnSelect}
      />
    );
    
    expect(screen.getByTestId('search-dropdown-hidden')).toBeInTheDocument();
    expect(screen.queryByTestId('search-dropdown')).not.toBeInTheDocument();
  });
  
  it('handles null or invalid results gracefully', () => {
    // @ts-expect-error - deliberately passing invalid data to test error handling
    const invalidResults: SearchResult[] = [
      null,
      undefined,
      { id: 'string-id', type: 'customer' }, // Invalid id type
      { id: 4, type: 123 }, // Invalid type type
      { id: 5 }, // Missing type
      { type: 'customer' } // Missing id
    ];
    
    render(
      <SearchResultsDropdown
        results={invalidResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    expect(screen.getByTestId('no-results')).toBeInTheDocument();
  });
  
  it('handles results with null properties gracefully', () => {
    const resultsWithNulls: SearchResult[] = [
      {
        id: 6,
        type: 'customer',
        name: null as unknown as string,
        customer_number: undefined as unknown as string
      }
    ];
    
    render(
      <SearchResultsDropdown
        results={resultsWithNulls}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    expect(screen.getByTestId('result-name-6')).toHaveTextContent('Unbekannt');
    expect(screen.getByTestId('result-subtitle-6')).toHaveTextContent('Kunde #');
  });
  
  it('handles StrictMode double-rendering without textContent errors', () => {
    const StrictModeWrapper: React.FC<{children: React.ReactNode}> = ({children}) => (
      <React.StrictMode>{children}</React.StrictMode>
    );
    
    const { unmount } = render(
      <StrictModeWrapper>
        <SearchResultsDropdown
          results={mockResults}
          isLoading={false}
          open={true}
          onSelect={mockOnSelect}
        />
      </StrictModeWrapper>
    );
    
    // Click the first result
    fireEvent.click(screen.getByTestId('result-1'));
    
    // Unmount quickly
    unmount();
    
    // No assertions needed - test passes if no errors are thrown
  });
}); 