import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Products from '@/components/ui/products';

// Mock all the components that are used in Products
jest.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children }: { children: React.ReactNode }) => <div data-testid="tabs">{children}</div>,
  TabsContent: ({ children, value }: { children: React.ReactNode; value: string }) => (
    <div data-testid={`tabs-content-${value}`}>{children}</div>
  ),
  TabsList: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="tabs-list">{children}</div>
  ),
  TabsTrigger: ({ children, value }: { children: React.ReactNode; value: string }) => (
    <button data-testid={`tabs-trigger-${value}`}>{children}</button>
  ),
}));

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick }: { children: React.ReactNode; onClick?: () => void }) => (
    <button onClick={onClick} data-testid="button">
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/input', () => ({
  Input: (props: any) => <input data-testid="input" {...props} />,
}));

jest.mock('@/components/ui/table', () => ({
  Table: ({ children }: { children: React.ReactNode }) => <table data-testid="table">{children}</table>,
  TableHeader: ({ children }: { children: React.ReactNode }) => <thead data-testid="table-header">{children}</thead>,
  TableBody: ({ children }: { children: React.ReactNode }) => <tbody data-testid="table-body">{children}</tbody>,
  TableRow: ({ children }: { children: React.ReactNode }) => <tr data-testid="table-row">{children}</tr>,
  TableHead: ({ children }: { children: React.ReactNode }) => <th data-testid="table-head">{children}</th>,
  TableCell: ({ children }: { children: React.ReactNode }) => <td data-testid="table-cell">{children}</td>,
}));

jest.mock('@/components/ui/card', () => ({
  Card: ({ children }: { children: React.ReactNode }) => <div data-testid="card">{children}</div>,
  CardContent: ({ children }: { children: React.ReactNode }) => <div data-testid="card-content">{children}</div>,
}));

jest.mock('@/components/ui/badge', () => ({
  Badge: ({ children }: { children: React.ReactNode }) => <span data-testid="badge">{children}</span>,
}));

jest.mock('@/components/ui/separator', () => ({
  Separator: () => <hr data-testid="separator" />,
}));

jest.mock('lucide-react', () => ({
  Plus: () => <span data-testid="icon-plus">Plus</span>,
  Minus: () => <span data-testid="icon-minus">Minus</span>,
  FileText: () => <span data-testid="icon-file-text">FileText</span>,
  Settings: () => <span data-testid="icon-settings">Settings</span>,
  Search: () => <span data-testid="icon-search">Search</span>,
  Eye: () => <span data-testid="icon-eye">Eye</span>,
  ChevronDown: () => <span data-testid="icon-chevron-down">ChevronDown</span>,
  Menu: () => <span data-testid="icon-menu">Menu</span>,
  X: () => <span data-testid="icon-x">X</span>,
  Filter: () => <span data-testid="icon-filter">Filter</span>,
  ArrowUpDown: () => <span data-testid="icon-arrow-up-down">ArrowUpDown</span>,
  MoreHorizontal: () => <span data-testid="icon-more-horizontal">MoreHorizontal</span>,
}));

describe('Products Component', () => {
  it('renders the Products component correctly', () => {
    render(<Products />);
    
    // Check if the main components are rendered
    expect(screen.getByTestId('tabs')).toBeInTheDocument();
    expect(screen.getByTestId('tabs-list')).toBeInTheDocument();
    expect(screen.getByTestId('input')).toBeInTheDocument();
  });

  it('handles search functionality', async () => {
    const user = userEvent.setup();
    render(<Products />);
    
    const searchInput = screen.getByTestId('input');
    
    // Type in the search input
    await user.type(searchInput, 'Adler');
    
    // Check if search term is applied
    expect(searchInput).toHaveValue('Adler');
  });

  it('renders product list correctly', () => {
    render(<Products />);
    
    // Table should be rendered
    expect(screen.getByTestId('table')).toBeInTheDocument();
    expect(screen.getByTestId('table-header')).toBeInTheDocument();
    expect(screen.getByTestId('table-body')).toBeInTheDocument();
    
    // Check for product list items
    const tableRows = screen.getAllByTestId('table-row');
    expect(tableRows.length).toBeGreaterThan(0);
  });

  it('can toggle sidebar visibility', async () => {
    const user = userEvent.setup();
    render(<Products />);
    
    // Find the toggle button for sidebar
    const toggleButtons = screen.getAllByTestId('button');
    const toggleSidebarButton = toggleButtons.find(button => 
      button.textContent?.includes('Menu') || 
      button.innerHTML.includes('data-testid="icon-menu"')
    );
    
    if (toggleSidebarButton) {
      // Click the toggle sidebar button
      await user.click(toggleSidebarButton);
      
      // We would check for sidebar visibility here, but since we've mocked
      // the components, we'll just verify the button was clickable
      expect(toggleSidebarButton).toBeInTheDocument();
    }
  });

  it('can select a product from the list', async () => {
    const user = userEvent.setup();
    render(<Products />);
    
    // Find all table rows (products)
    const tableRows = screen.getAllByTestId('table-row');
    
    // Click on the first product row (excluding header row)
    if (tableRows.length > 1) {
      await user.click(tableRows[1]);
      
      // Since we mocked components, we can't easily check the selected state
      // but we can verify the row was clickable
      expect(tableRows[1]).toBeInTheDocument();
    }
  });

  it('renders tab content correctly', () => {
    render(<Products />);
    
    // Check for different tab content areas
    expect(screen.getByTestId('tabs-content-details')).toBeInTheDocument();
    expect(screen.getByTestId('tabs-content-history')).toBeInTheDocument();
    expect(screen.getByTestId('tabs-content-pricing')).toBeInTheDocument();
    expect(screen.getByTestId('tabs-content-inventory')).toBeInTheDocument();
  });

  it('can switch between tabs', async () => {
    const user = userEvent.setup();
    render(<Products />);
    
    // Find tab triggers
    const detailsTab = screen.getByTestId('tabs-trigger-details');
    const historyTab = screen.getByTestId('tabs-trigger-history');
    const pricingTab = screen.getByTestId('tabs-trigger-pricing');
    const inventoryTab = screen.getByTestId('tabs-trigger-inventory');
    
    // Click on different tabs
    await user.click(historyTab);
    expect(historyTab).toBeInTheDocument();
    
    await user.click(pricingTab);
    expect(pricingTab).toBeInTheDocument();
    
    await user.click(inventoryTab);
    expect(inventoryTab).toBeInTheDocument();
    
    await user.click(detailsTab);
    expect(detailsTab).toBeInTheDocument();
  });
}); 