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

// Mock the LastVisited context - keep the mock for useLastVisited
const mockAddLastVisited = jest.fn();
jest.mock('@/context/LastVisitedContext', () => ({
  useLastVisited: jest.fn(() => ({ // Provide the mock implementation here
    addVisitedItem: mockAddLastVisited,
    lastVisitedItems: [],
  })),
  // Keep the actual Provider for wrapping
  LastVisitedProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
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
  const mockGetProducts = productApi.getProducts as jest.Mock;
  const mockedUseLastVisited = useLastVisited as jest.Mock;

  beforeEach(() => {
    // Reset mocks before each test
    mockGetProducts.mockReset();
    mockedUseLastVisited.mockClear(); // Clear calls on the imported mock function
    mockAddLastVisited.mockClear(); // Clear calls on the inner function mock
    
    // Reset the return value for the mock hook if necessary (though defined in jest.mock now)
    mockedUseLastVisited.mockReturnValue({
      addVisitedItem: mockAddLastVisited,
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
      <React.StrictMode>
        <MemoryRouterProvider>
          <LastVisitedProvider>
            <InventoryManagement />
          </LastVisitedProvider>
        </MemoryRouterProvider>
      </React.StrictMode>
    );
    
    // Wait for products to load
    await waitFor(() => {
      // Use a more specific query for the main heading
      expect(screen.getByRole('heading', { name: 'Produkte', level: 2 })).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Search by exact SKU or legacy-SKU...')).toBeInTheDocument();
    });
  });
}); 