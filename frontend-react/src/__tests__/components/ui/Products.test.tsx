import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import InventoryManagement from '@/components/ui/products';
import { productApi } from '@/lib/products/api';
import { LastVisitedProvider, useLastVisited } from '@/context/LastVisitedContext';
import { MemoryRouterProvider } from 'next-router-mock/MemoryRouterProvider';

// Mock the product API
jest.mock('@/lib/products/api', () => ({
  productApi: {
    getProducts: jest.fn()
  }
}));

// Mock the LastVisited context
jest.mock('@/context/LastVisitedContext', () => ({
  useLastVisited: jest.fn(),
}));

// Mock next/navigation - Keep this global mock as well
jest.mock('next/navigation', () => require('next-router-mock'));

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
  const mockGetProducts = productApi.getProducts as jest.Mock;
  const mockUseLastVisited = useLastVisited as jest.Mock;
  const mockAddLastVisited = jest.fn();

  beforeEach(() => {
    // Reset mocks before each test
    mockGetProducts.mockReset();
    mockUseLastVisited.mockReset();
    mockAddLastVisited.mockClear();
    
    // Provide default mock implementation for useLastVisited
    mockUseLastVisited.mockReturnValue({
      addLastVisited: mockAddLastVisited,
      lastVisitedItems: [],
    });
    
    // Default successful API response
    mockGetProducts.mockResolvedValue({ products: mockProducts, total: mockProducts.length, skip: 0, limit: 30 });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the Products component correctly', async () => {
    render(
      <MemoryRouterProvider>
        <InventoryManagement />
      </MemoryRouterProvider>
    );
    
    // Wait for products to load
    await waitFor(() => {
      // Use a more specific query for the main heading
      expect(screen.getByRole('heading', { name: 'Produkte', level: 3 })).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Suche nach Produkt...')).toBeInTheDocument();
    });
  });

  it('handles search functionality', async () => {
    render(
      <MemoryRouterProvider>
        <InventoryManagement />
      </MemoryRouterProvider>
    );
    
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
    render(
      <MemoryRouterProvider>
        <InventoryManagement />
      </MemoryRouterProvider>
    );
    
    // Wait for products to load and check for specific elements
    await waitFor(() => {
      const productElements = screen.getAllByText('Product A');
      expect(productElements.length).toBeGreaterThan(0);
      expect(screen.getByText('SKU001')).toBeInTheDocument();
    });
  });

  it('can select a product from the list', async () => {
    render(
      <MemoryRouterProvider>
        <InventoryManagement />
      </MemoryRouterProvider>
    );
    
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

    // Check if addLastVisited was called with the correct product
    await waitFor(() => {
      expect(mockAddLastVisited).toHaveBeenCalledWith(mockProducts[0]);
    });

    // Optional: Check if navigation occurred if selection triggers navigation
    // You'll need to inspect the mocked router state from next-router-mock
    // e.g., expect(require('next/router').pathname).toBe('/products/1');
  });
}); 