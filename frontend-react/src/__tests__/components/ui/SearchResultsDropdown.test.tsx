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
  
  it('renders no results state correctly', () => {
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
  
  it('renders search results correctly', () => {
    render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    expect(screen.getByText('Test Customer')).toBeInTheDocument();
    expect(screen.getByText('Kunde #C001')).toBeInTheDocument();
    expect(screen.getByText('Test Product')).toBeInTheDocument();
    expect(screen.getByText('Artikel #P001 (LP001)')).toBeInTheDocument();
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
    
    fireEvent.click(screen.getByText('Test Customer'));
    
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
    
    expect(screen.queryByText('Test Customer')).not.toBeInTheDocument();
    expect(screen.getByTestId('search-dropdown-hidden')).toBeInTheDocument();
  });
  
  it('handles null or invalid results gracefully', () => {
    // @ts-ignore - deliberately passing invalid data to test error handling
    const invalidResults: any[] = [
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
    
    // Should show no results message since all are filtered out
    expect(screen.getByText('Keine Ergebnisse gefunden')).toBeInTheDocument();
  });
  
  it('handles results with null properties gracefully', () => {
    const resultsWithNulls: SearchResult[] = [
      {
        id: 6,
        type: 'customer',
        name: null as any, // Deliberately use null
        customer_number: undefined as any // Deliberately use undefined
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
    
    // Should show "Unbekannt" for the name
    expect(screen.getByText('Unbekannt')).toBeInTheDocument();
  });
  
  // Test specifically for the textContent issue
  it('handles DOM manipulation safely without textContent errors', () => {
    const { container, unmount } = render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Get all elements
    const allElements = container.querySelectorAll('*');
    
    // Check textContent safety
    allElements.forEach(el => {
      expect(() => {
        // Just accessing textContent should not throw
        const content = el.textContent;
        // Do something with content to avoid unused variable warning
        return content;
      }).not.toThrow();
    });
    
    // Clean unmount
    unmount();
    
    // No errors should have been logged
    expect(consoleErrors.length).toBe(0);
  });
  
  // Test that specifically triggers the product issue
  it('safely handles rapid mount/unmount without textContent errors', async () => {
    const { unmount } = render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Quickly unmount to simulate what might happen in production
    unmount();
    
    // Immediately render again with different props
    render(
      <SearchResultsDropdown
        results={[mockResults[0]]}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />
    );
    
    // Click a result right after mounting
    fireEvent.click(screen.getByText('Test Customer'));
    
    // No errors should have been logged related to textContent
    const hasTextContentError = consoleErrors.some(
      error => error.includes('textContent') || error.includes('null')
    );
    
    expect(hasTextContentError).toBe(false);
  });
  
  // Test specifically for StrictMode behavior
  it('handles StrictMode double-rendering without textContent errors', async () => {
    // Create a wrapper with React.StrictMode
    const StrictModeWrapper: React.FC<{children: React.ReactNode}> = ({children}) => (
      <React.StrictMode>{children}</React.StrictMode>
    );
    
    // Render with StrictMode to trigger double rendering
    const { unmount } = render(
      <SearchResultsDropdown
        results={mockResults}
        isLoading={false}
        open={true}
        onSelect={mockOnSelect}
      />,
      { wrapper: StrictModeWrapper }
    );
    
    // Interact with component
    fireEvent.click(screen.getByText('Test Customer'));
    
    // Unmount quickly
    unmount();
    
    // Check for textContent errors
    const hasTextContentError = consoleErrors.some(
      error => error.includes('textContent') || error.includes('null')
    );
    
    expect(hasTextContentError).toBe(false);
  });
}); 