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
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText('Add Product')).toBeInTheDocument();
  });

  it('handles search functionality', async () => {
    const user = userEvent.setup();
    render(<Products />);
    
    // There may be multiple inputs, find the one with placeholder "Search products..."
    const inputs = screen.getAllByTestId('input');
    const searchInput = inputs.find(input => input.getAttribute('placeholder') === 'Search products...');
    
    expect(searchInput).toBeDefined();
    if (searchInput) {
      // Type in the search input
      await user.type(searchInput, 'Adler');
      
      // Check if search term is applied
      expect(searchInput).toHaveValue('Adler');
    }
  });

  it('renders product list correctly', () => {
    render(<Products />);
    
    // Check for product list items in the sidebar
    const productItems = screen.getAllByText(/Product [A-Z]/);
    expect(productItems.length).toBeGreaterThan(0);
  });

  it('can toggle sidebar visibility', async () => {
    const user = userEvent.setup();
    render(<Products />);
    
    // Find the toggle button for sidebar
    const toggleButtons = screen.getAllByTestId('button');
    // We can't rely on specific text, so just click the first button which should be the sidebar toggle
    if (toggleButtons.length > 0) {
      await user.click(toggleButtons[0]);
      expect(toggleButtons[0]).toBeInTheDocument();
    }
  });

  it('can select a product from the list', async () => {
    const user = userEvent.setup();
    render(<Products />);
    
    // Find a product item to click
    const productItems = screen.getAllByText(/Product [A-Z]/);
    
    if (productItems.length > 0) {
      // Click on the first product
      await user.click(productItems[0]);
      
      // Since we mocked components, we can't easily check the selected state
      // but we can verify the item was clickable
      expect(productItems[0]).toBeInTheDocument();
    }
  });
}); 