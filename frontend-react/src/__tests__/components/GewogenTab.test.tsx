import { render, screen } from '@testing-library/react';
import GewogenTab from '@/components/gewogen-tab';

// Mock the Lucide icons
jest.mock('lucide-react', () => ({
  Scale: () => <div data-testid="scale-icon" />,
  TrendingUp: () => <div data-testid="trending-up-icon" />,
  BarChart: () => <div data-testid="bar-chart-icon" />,
  RefreshCw: () => <div data-testid="refresh-cw-icon" />,
}));

describe('GewogenTab Component', () => {
  it('renders the component with correct card titles', () => {
    render(<GewogenTab />);
    
    // Check if the card titles are rendered
    expect(screen.getByText('Gewicht')).toBeInTheDocument();
    expect(screen.getByText('Gewichtsmessungen')).toBeInTheDocument();
    expect(screen.getByText('Statistik')).toBeInTheDocument();
  });

  it('renders input for weight with default value', () => {
    render(<GewogenTab />);
    
    // Check if the input is rendered with default value
    const input = screen.getByDisplayValue('0');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
  });

  it('renders the gram unit text', () => {
    render(<GewogenTab />);
    
    // Check if the unit text is rendered
    expect(screen.getAllByText('g').length).toBeGreaterThanOrEqual(1);
  });

  it('renders update button', () => {
    render(<GewogenTab />);
    
    // Check if the update button is rendered
    expect(screen.getByText('Aktualisieren')).toBeInTheDocument();
    expect(screen.getByTestId('refresh-cw-icon')).toBeInTheDocument();
  });

  it('renders chart button', () => {
    render(<GewogenTab />);
    
    // Check if the chart button is rendered
    expect(screen.getByText('Diagramm')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart-icon')).toBeInTheDocument();
  });

  it('renders table with correct headers', () => {
    render(<GewogenTab />);
    
    // Check if the table headers are rendered
    expect(screen.getByText('Datum')).toBeInTheDocument();
    expect(screen.getByText('Zeit')).toBeInTheDocument();
    expect(screen.getAllByText('g').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Stück')).toBeInTheDocument();
  });

  it('renders statistics section with correct information', () => {
    render(<GewogenTab />);
    
    // Check if statistics data is rendered
    expect(screen.getByText('Durchschnittsgewicht:')).toBeInTheDocument();
    expect(screen.getByText('0 g')).toBeInTheDocument();
    expect(screen.getByText('Standardabweichung:')).toBeInTheDocument();
    expect(screen.getByText('0,00 g')).toBeInTheDocument();
    expect(screen.getByText('0,00 %')).toBeInTheDocument();
  });

  it('renders average button', () => {
    render(<GewogenTab />);
    
    // Check if the average button is rendered
    expect(screen.getByText('Ø übernehmen')).toBeInTheDocument();
  });

  it('renders icons correctly', () => {
    render(<GewogenTab />);
    
    // Check if icons are rendered
    expect(screen.getByTestId('scale-icon')).toBeInTheDocument();
    expect(screen.getByTestId('trending-up-icon')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart-icon')).toBeInTheDocument();
    expect(screen.getByTestId('refresh-cw-icon')).toBeInTheDocument();
  });

  it('renders the correct grid layout', () => {
    const { container } = render(<GewogenTab />);
    
    // Check if grid layout exists
    const gridDiv = container.querySelector('.grid.grid-cols-1.lg\\:grid-cols-3');
    expect(gridDiv).toBeInTheDocument();
    
    // Check if there are two columns, one larger than the other
    const largeColumn = container.querySelector('.lg\\:col-span-2');
    expect(largeColumn).toBeInTheDocument();
  });
}); 