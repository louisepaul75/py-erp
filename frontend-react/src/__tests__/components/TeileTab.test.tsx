import { render, screen } from '@testing-library/react';
import TeileTab from '@/components/teile-tab';

// Mock the Lucide icons
jest.mock('lucide-react', () => ({
  Plus: () => <div data-testid="plus-icon" />,
  Minus: () => <div data-testid="minus-icon" />,
  ChevronLeft: () => <div data-testid="chevron-left-icon" />,
  ChevronRight: () => <div data-testid="chevron-right-icon" />,
  ArrowUpDown: () => <div data-testid="arrow-up-down-icon" />,
  Filter: () => <div data-testid="filter-icon" />,
}));

describe('TeileTab Component', () => {
  it('renders the component with correct headings', () => {
    render(<TeileTab />);
    
    // Check if the headings are rendered
    // Using getAllByText as there are multiple elements with the same text
    const bestehtAusElements = screen.getAllByText('Besteht aus');
    expect(bestehtAusElements.length).toBeGreaterThanOrEqual(1);
    
    expect(screen.getByText('Ist Teil von')).toBeInTheDocument();
  });

  it('renders action buttons', () => {
    render(<TeileTab />);
    
    // Check if the buttons are rendered
    expect(screen.getByText('Hinzufügen')).toBeInTheDocument();
    expect(screen.getByText('Entfernen')).toBeInTheDocument();
    expect(screen.getByText('Filter')).toBeInTheDocument();
    expect(screen.getByText('Sortieren')).toBeInTheDocument();
  });

  it('renders the table headers correctly', () => {
    render(<TeileTab />);
    
    // Check table headers in first table
    const tableHeaders = screen.getAllByText('Besteht aus');
    expect(tableHeaders.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Anz')).toBeInTheDocument();
    
    // Check table headers in second table
    expect(screen.getByText('Ist Teil von Variante')).toBeInTheDocument();
    expect(screen.getByText('Ist Teil von Artikel')).toBeInTheDocument();
  });

  it('renders pagination elements', () => {
    render(<TeileTab />);
    
    // Check pagination text
    expect(screen.getByText('Seite 1 von 1')).toBeInTheDocument();
    
    // Check pagination buttons (through mocked icons)
    const leftChevron = screen.getByTestId('chevron-left-icon');
    expect(leftChevron).toBeInTheDocument();
    
    const rightChevron = screen.getByTestId('chevron-right-icon');
    expect(rightChevron).toBeInTheDocument();
  });

  it('renders tables with correct number of rows', () => {
    render(<TeileTab />);
    
    // Each row contains empty td cells, so we can count them
    // First table has 5 rows (5 rows * 4 cells = 20 cells)
    // Second table has 7 rows (7 rows * 2 cells = 14 cells)
    // Total of 34 td cells
    const tableCells = document.querySelectorAll('td');
    expect(tableCells.length).toBe(34);
  });

  it('has the correct icons', () => {
    render(<TeileTab />);
    
    // Check if the icons are rendered
    expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
    expect(screen.getByTestId('minus-icon')).toBeInTheDocument();
    expect(screen.getByTestId('filter-icon')).toBeInTheDocument();
    expect(screen.getByTestId('arrow-up-down-icon')).toBeInTheDocument();
  });
  
  it('has the correct structure', () => {
    const { container } = render(<TeileTab />);
    
    // Check if main container has correct padding
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv).toHaveClass('p-6');
    
    // Check if there are two cards
    const cards = document.querySelectorAll('.border.border-slate-200');
    expect(cards.length).toBe(2);
  });
}); 