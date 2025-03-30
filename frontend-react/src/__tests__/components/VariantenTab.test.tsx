import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import VariantenTab from '@/components/varianten-tab';

// Mock the Lucide icons
jest.mock('lucide-react', () => ({
  Plus: () => <div data-testid="plus-icon" />,
  Minus: () => <div data-testid="minus-icon" />
}));

// Mock the content components since they might be problematic in tests
const LagerorteTabMock = () => <div data-testid="lagerorte-content">Lagerorte Content</div>;
LagerorteTabMock.displayName = 'LagerorteTabMock';

const GewogenTabMock = () => <div data-testid="gewogen-content">Gewogen Content</div>;
GewogenTabMock.displayName = 'GewogenTabMock';

const UmsatzeTabMock = () => <div data-testid="umsatze-content">Umsätze Content</div>;
UmsatzeTabMock.displayName = 'UmsatzeTabMock';

const BewegungenTabMock = () => <div data-testid="bewegungen-content">Bewegungen Content</div>;
BewegungenTabMock.displayName = 'BewegungenTabMock';

jest.mock('@/components/lagerorte-tab', () => LagerorteTabMock);
jest.mock('@/components/gewogen-tab', () => GewogenTabMock);
jest.mock('@/components/umsatze-tab', () => UmsatzeTabMock);
jest.mock('@/components/bewegungen-tab', () => BewegungenTabMock);

describe('VariantenTab', () => {
  it('renders correctly with default props', () => {
    render(<VariantenTab />);
    
    // Check if the main heading is rendered
    expect(screen.getByText('Varianten')).toBeInTheDocument();
    
    // Check if the table headers are rendered
    expect(screen.getByText('Nummer')).toBeInTheDocument();
    expect(screen.getByText('Bezeichnung')).toBeInTheDocument();
    expect(screen.getByText('Ausprägung')).toBeInTheDocument();
    expect(screen.getByText('Prod.')).toBeInTheDocument();
    expect(screen.getByText('Vertr.')).toBeInTheDocument();
    expect(screen.getByText('VK Artikel')).toBeInTheDocument();
    expect(screen.getByText('Releas')).toBeInTheDocument();
    
    // Check if the variant data is rendered
    expect(screen.getByText('501506')).toBeInTheDocument();
    expect(screen.getByText('100870')).toBeInTheDocument();
    expect(screen.getByText('904743')).toBeInTheDocument();
    expect(screen.getAllByText('"Adler"-Lock').length).toBe(2);
    expect(screen.getByText('"Adler"-Lock OX')).toBeInTheDocument();
    expect(screen.getByText('Blank')).toBeInTheDocument();
    expect(screen.getByText('Bemalt')).toBeInTheDocument();
  });

  it('renders the correct tabs', () => {
    render(<VariantenTab />);
    
    // Check if all tabs are rendered
    expect(screen.getByRole('tab', { name: 'Details' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Teile' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Bilder' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Gewogen' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Lagerorte' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Umsätze' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Bewegungen' })).toBeInTheDocument();
  });
  
  it('has the Details tab with categories section', () => {
    render(<VariantenTab />);
    
    // Check that the details tab content is visible
    expect(screen.getByText('Kategorien')).toBeInTheDocument();
    
    // Check the categories table headers, using getAllByText for Home
    // since it appears multiple times in the component
    expect(screen.getAllByText('Home').length).toBeGreaterThan(0);
    expect(screen.getByText('Sortiment')).toBeInTheDocument();
    expect(screen.getByText('Tradition')).toBeInTheDocument();
    expect(screen.getByText('Maschinerie')).toBeInTheDocument();
    
    // Check the categories table data
    expect(screen.getByText('All Products')).toBeInTheDocument();
  });
  
  it('renders plus/minus buttons for variants', () => {
    render(<VariantenTab />);
    
    // Check for the Plus and Minus icons near the 'Varianten' heading
    const plusIcons = screen.getAllByTestId('plus-icon');
    const minusIcons = screen.getAllByTestId('minus-icon');
    
    expect(plusIcons.length).toBeGreaterThan(0);
    expect(minusIcons.length).toBeGreaterThan(0);
  });
  
  it('renders checkboxes with correct state', () => {
    render(<VariantenTab />);
    
    // Get all checkboxes
    const checkboxes = screen.getAllByRole('checkbox');
    
    // Expect at least 9 checkboxes (3 variants × 3 checkbox columns)
    expect(checkboxes.length).toBeGreaterThanOrEqual(9);
    
    // Expect at least one checkbox to be checked (at least one is true in the data)
    const checkedBoxes = screen.getAllByRole('checkbox', { checked: true });
    expect(checkedBoxes.length).toBeGreaterThan(0);
  });
}); 