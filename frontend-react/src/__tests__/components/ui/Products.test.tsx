import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import InventoryManagement from '@/components/ui/products';
import { productApi } from '@/lib/products/api';

// Mock the product API
jest.mock('@/lib/products/api', () => ({
  productApi: {
    getProducts: jest.fn()
  }
}));

const mockProducts = [
  {
    id: 1,
    name: 'Product A',
    sku: 'SKU001',
    description: 'Description A',
    is_active: true,
    is_discontinued: false,
    is_new: true,
    release_date: null,
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
    weight: 1.5,
    length_mm: 100,
    width_mm: 50,
    height_mm: 25,
    name_en: 'Product A EN',
    short_description: 'Short desc A',
    short_description_en: 'Short desc A EN',
    description_en: 'Description A EN',
    keywords: 'keywords',
    legacy_id: 'L001',
    legacy_base_sku: 'LSKU001',
    is_hanging: false,
    is_one_sided: true,
    images: [],
    primary_image: null,
    category: null,
    tags: [],
    variants_count: 2
  },
  // Add more mock products as needed
];

describe('Products Component', () => {
  beforeEach(() => {
    (productApi.getProducts as jest.Mock).mockResolvedValue({
      results: mockProducts,
      total: mockProducts.length
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the Products component correctly', async () => {
    render(<InventoryManagement />);
    
    // Wait for products to load
    await waitFor(() => {
      // Use a more specific query for the main heading
      expect(screen.getByRole('heading', { name: 'Produkte', level: 3 })).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Suche nach Produkt...')).toBeInTheDocument();
    });
  });

  it('handles search functionality', async () => {
    render(<InventoryManagement />);
    
    // Wait for products to load and use getAllByText to handle multiple instances
    await waitFor(() => {
      const productElements = screen.getAllByText('Product A');
      expect(productElements.length).toBeGreaterThan(0);
    });

    // Find search input and type
    const searchInput = screen.getByPlaceholderText('Suche nach Produkt...');
    await userEvent.type(searchInput, 'SKU001');

    // Check if product is filtered - use getAllByText since there might be multiple instances
    const productElements = screen.getAllByText('Product A');
    expect(productElements.length).toBeGreaterThan(0);
  });

  it('renders product list correctly', async () => {
    render(<InventoryManagement />);
    
    // Wait for products to load and check for specific elements
    await waitFor(() => {
      const productElements = screen.getAllByText('Product A');
      expect(productElements.length).toBeGreaterThan(0);
      expect(screen.getByText('SKU001')).toBeInTheDocument();
    });
  });

  it('can select a product from the list', async () => {
    render(<InventoryManagement />);
    
    // Wait for products to load
    await waitFor(() => {
      const productElements = screen.getAllByText('Product A');
      expect(productElements.length).toBeGreaterThan(0);
    });

    // Click on the first product instance
    const productElements = screen.getAllByText('Product A');
    fireEvent.click(productElements[0]);

    // Check if product details are displayed
    expect(screen.getByText('SKU001')).toBeInTheDocument();
  });
}); 