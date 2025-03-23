import { render, screen } from '@testing-library/react';
import LagerorteTab from '@/components/lagerorte-tab';

// Mock the Lucide icons
jest.mock('lucide-react', () => ({
  ChevronUp: () => <div data-testid="chevron-up-icon" />,
  ArrowUpDown: () => <div data-testid="arrow-up-down-icon" />,
  Warehouse: () => <div data-testid="warehouse-icon" />,
  Filter: () => <div data-testid="filter-icon" />,
  Plus: () => <div data-testid="plus-icon" />
}));

describe('LagerorteTab Component', () => {
  it('renders the component with correct heading', () => {
    render(<LagerorteTab />);
    
    expect(screen.getAllByText('Lagerorte').length).toBeGreaterThanOrEqual(1);
  });

  it('renders filter and sort buttons', () => {
    render(<LagerorteTab />);
    
    expect(screen.getByText('Filter')).toBeInTheDocument();
    expect(screen.getByText('Sortieren')).toBeInTheDocument();
  });

  it('renders table with correct headers', () => {
    render(<LagerorteTab />);
    
    expect(screen.getByText('Lager')).toBeInTheDocument();
    expect(screen.getByText('Regal')).toBeInTheDocument();
    expect(screen.getByText('Fach')).toBeInTheDocument();
    expect(screen.getByText('Boden')).toBeInTheDocument();
    expect(screen.getByText('Schütte')).toBeInTheDocument();
    expect(screen.getByText('Slot(s)')).toBeInTheDocument();
    expect(screen.getByText('Abverkauf')).toBeInTheDocument();
    expect(screen.getByText('Sonder')).toBeInTheDocument();
    expect(screen.getByText('Bestand')).toBeInTheDocument();
  });

  it('renders table rows with correct data', () => {
    render(<LagerorteTab />);
    
    const cellContent = screen.getAllByText('18187 / Stammlager-Dies...');
    expect(cellContent.length).toBe(2);
    
    // Check for checkboxes
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes.length).toBe(4); // 2 per row, 2 rows
  });

  it('renders action buttons at the bottom', () => {
    render(<LagerorteTab />);
    
    expect(screen.getByText('Bestand ändern')).toBeInTheDocument();
    expect(screen.getByText('Umbuchen')).toBeInTheDocument();
    expect(screen.getByText('Neuer Lagerort')).toBeInTheDocument();
  });

  it('renders the correct icons', () => {
    render(<LagerorteTab />);
    
    expect(screen.getByTestId('warehouse-icon')).toBeInTheDocument();
    expect(screen.getByTestId('filter-icon')).toBeInTheDocument();
    expect(screen.getByTestId('arrow-up-down-icon')).toBeInTheDocument();
    expect(screen.getByTestId('chevron-up-icon')).toBeInTheDocument();
    expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
  });

  it('renders empty rows for pagination space', () => {
    render(<LagerorteTab />);
    
    // The component renders 15 empty rows
    const tableRows = screen.getAllByRole('row');
    expect(tableRows.length).toBeGreaterThan(17); // Header row + 2 data rows + 15 empty rows + footer row
  });

  it('has a summary row at the bottom of the table', () => {
    render(<LagerorteTab />);
    
    // Get all rows
    const tableRows = screen.getAllByRole('row');
    // Last row should contain '0' as the summary for 'Bestand'
    const lastRowCells = tableRows[tableRows.length - 1].querySelectorAll('td');
    expect(lastRowCells[lastRowCells.length - 1].textContent).toBe('0');
  });
}); 