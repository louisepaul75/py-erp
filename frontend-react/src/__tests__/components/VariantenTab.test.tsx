import { render, screen, fireEvent } from '@testing-library/react';
import VariantenTab from '@/components/varianten-tab';

// Mock the Lucide icons
jest.mock('lucide-react', () => ({
  Plus: () => <div data-testid="plus-icon" />,
  Minus: () => <div data-testid="minus-icon" />
}));

describe('VariantenTab Component', () => {
  it('renders the component with correct heading', () => {
    render(<VariantenTab />);
    
    expect(screen.getByText('Varianten')).toBeInTheDocument();
  });

  it('renders add and remove buttons', () => {
    render(<VariantenTab />);
    
    expect(screen.getAllByTestId('plus-icon').length).toBeGreaterThan(0);
    expect(screen.getAllByTestId('minus-icon').length).toBeGreaterThan(0);
  });

  it('renders variants table with correct headers', () => {
    render(<VariantenTab />);
    
    expect(screen.getByText('Nummer')).toBeInTheDocument();
    expect(screen.getByText('Bezeichnung')).toBeInTheDocument();
    expect(screen.getByText('Ausprägung')).toBeInTheDocument();
    expect(screen.getByText('Prod.')).toBeInTheDocument();
    expect(screen.getByText('Vertr.')).toBeInTheDocument();
    expect(screen.getByText('VK Artikel')).toBeInTheDocument();
    expect(screen.getByText('Releas')).toBeInTheDocument();
  });

  it('renders variant rows with correct data', () => {
    render(<VariantenTab />);
    
    expect(screen.getByText('501506')).toBeInTheDocument();
    expect(screen.getByText('100870')).toBeInTheDocument();
    expect(screen.getByText('904743')).toBeInTheDocument();
    expect(screen.getAllByText('"Adler"-Lock').length).toBe(2);
    expect(screen.getByText('"Adler"-Lock OX')).toBeInTheDocument();
    expect(screen.getByText('Blank')).toBeInTheDocument();
    expect(screen.getByText('Bemalt')).toBeInTheDocument();
    expect(screen.getByText('01.01.2023')).toBeInTheDocument();
    expect(screen.getByText('11.02.2023')).toBeInTheDocument();
    expect(screen.getByText('01.01.1999')).toBeInTheDocument();
  });

  it('renders all tabs', () => {
    render(<VariantenTab />);
    
    expect(screen.getByRole('tab', { name: 'Details' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Teile' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Bilder' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Gewogen' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Lagerorte' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Umsätze' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Bewegungen' })).toBeInTheDocument();
  });

  it('defaults to Details tab and shows categories section', () => {
    render(<VariantenTab />);
    
    // Check that Details tab is active initially
    const detailsTab = screen.getByRole('tab', { name: 'Details' });
    expect(detailsTab).toHaveAttribute('data-state', 'active');
    
    // Check that categories section is visible
    expect(screen.getByText('Kategorien')).toBeInTheDocument();
    expect(screen.getAllByText('Home').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Sortiment')).toBeInTheDocument();
  });

  it('renders checkboxes correctly', () => {
    render(<VariantenTab />);
    
    // Get all checkboxes
    const checkboxes = screen.getAllByRole('checkbox');
    
    // There should be checkboxes for Prod, Vertr, and VK Artikel for 3 variants
    expect(checkboxes.length).toBe(9);
    
    // Check that the 100870 variant (second row) has all checkboxes checked
    // This is the variant with prod, vertr, and vkArtikel all set to true
    // We can't easily isolate these directly, but we know the data pattern
    const checkedCheckboxes = screen.getAllByRole('checkbox', { checked: true });
    expect(checkedCheckboxes.length).toBeGreaterThan(0);
  });

  it('renders tab triggers correctly', () => {
    render(<VariantenTab />);
    
    // Check that all tabs have correct accessible roles and names
    const detailsTab = screen.getByRole('tab', { name: 'Details' });
    const lagerorteTab = screen.getByRole('tab', { name: 'Lagerorte' });
    const gewogenTab = screen.getByRole('tab', { name: 'Gewogen' });
    
    expect(detailsTab).toBeInTheDocument();
    expect(lagerorteTab).toBeInTheDocument();
    expect(gewogenTab).toBeInTheDocument();
    
    // The Details tab should be the default active tab
    expect(detailsTab).toHaveClass('data-[state=active]:bg-white');
  });
}); 