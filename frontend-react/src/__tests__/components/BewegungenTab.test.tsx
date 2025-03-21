import React from 'react';
import { render, screen } from '@testing-library/react';
import BewegungenTab from '@/components/bewegungen-tab';

// Mock the icons
jest.mock('lucide-react', () => ({
  Search: () => <div data-testid="search-icon" />,
  Filter: () => <div data-testid="filter-icon" />,
  ArrowUpDown: () => <div data-testid="arrow-updown-icon" />,
  Calendar: () => <div data-testid="calendar-icon" />,
  Download: () => <div data-testid="download-icon" />,
}));

describe('BewegungenTab Component', () => {
  beforeEach(() => {
    render(<BewegungenTab />);
  });

  test('renders the search input', () => {
    const searchInput = screen.getByPlaceholderText('Suchen...');
    expect(searchInput).toBeInTheDocument();
    expect(screen.getByTestId('search-icon')).toBeInTheDocument();
  });

  test('renders filter button', () => {
    const filterButton = screen.getByText('Filter');
    expect(filterButton).toBeInTheDocument();
    expect(screen.getByTestId('filter-icon')).toBeInTheDocument();
  });

  test('renders period and export buttons', () => {
    const periodButton = screen.getByText('Zeitraum');
    const exportButton = screen.getByText('Exportieren');
    
    expect(periodButton).toBeInTheDocument();
    expect(screen.getByTestId('calendar-icon')).toBeInTheDocument();
    
    expect(exportButton).toBeInTheDocument();
    expect(screen.getByTestId('download-icon')).toBeInTheDocument();
  });

  test('renders the card with proper title', () => {
    const cardTitle = screen.getByText('Bewegungen');
    expect(cardTitle).toBeInTheDocument();
  });

  test('renders sort button', () => {
    const sortButton = screen.getByText('Sortieren');
    expect(sortButton).toBeInTheDocument();
    expect(screen.getByTestId('arrow-updown-icon')).toBeInTheDocument();
  });

  test('renders table headers correctly', () => {
    const headers = [
      'Kunden-Nr', 'Kunde', 'Art', 'Beleg-Nr', 'Datum', 'Menge', 'Preis'
    ];
    
    headers.forEach(header => {
      expect(screen.getByText(header)).toBeInTheDocument();
    });
  });

  test('renders table rows with customer data', () => {
    const customerNumbers = ['1891810', '1440011', 'DE20060', '128017'];
    const customerNames = ['ADK', 'Tropp'];
    const documentNumbers = ['202060', '2010292', '210870', '210688', '210689', '210690'];
    
    customerNumbers.forEach(number => {
      expect(screen.getAllByText(number).length).toBeGreaterThanOrEqual(1);
    });
    
    customerNames.forEach(name => {
      expect(screen.getAllByText(name).length).toBeGreaterThanOrEqual(1);
    });
    
    documentNumbers.forEach(docNumber => {
      expect(screen.getByText(docNumber)).toBeInTheDocument();
    });
  });

  test('renders transaction types', () => {
    // These are spans with different background colors
    expect(screen.getByText('L')).toBeInTheDocument();
    expect(screen.getByText('R')).toBeInTheDocument();
    expect(screen.getAllByText('A').length).toBeGreaterThanOrEqual(1);
  });

  test('renders checkbox for filtering', () => {
    const checkbox = screen.getByLabelText('Nur R');
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
  });

  test('renders entries count', () => {
    expect(screen.getByText('Gesamt: 6 Einträge')).toBeInTheDocument();
  });

  test('renders dates and prices correctly', () => {
    const dates = ['22.10.2024', '23.09.2024', '18.09.2024', '06.08.2024'];
    const prices = ['66,70 €', '27,80 €', '24,20 €', '52,30 €'];
    
    dates.forEach(date => {
      expect(screen.getAllByText(date).length).toBeGreaterThanOrEqual(1);
    });
    
    prices.forEach(price => {
      expect(screen.getAllByText(price).length).toBeGreaterThanOrEqual(1);
    });
  });
}); 