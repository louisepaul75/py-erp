import { renderHook, act, waitFor } from '@testing-library/react';
import { useGlobalSearch } from '@/hooks/useGlobalSearch';
import { API_URL } from '@/lib/config';

// Mock the api object from authService
jest.mock('@/lib/auth/authService', () => ({
  api: {
    get: jest.fn()
  }
}));

// Import after mocking
import { api } from '@/lib/auth/authService';

describe('useGlobalSearch', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset timers
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => useGlobalSearch());
    
    expect(result.current.query).toBe('');
    expect(result.current.results).toBeNull();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should update query when setQuery is called', () => {
    const { result } = renderHook(() => useGlobalSearch());
    
    act(() => {
      result.current.setQuery('test');
    });
    
    expect(result.current.query).toBe('test');
  });

  it('should fetch data after debounce period', async () => {
    const mockResponse = {
      query: 'test',
      total_count: 2,
      counts: {
        customers: 1,
        sales_records: 1,
        parent_products: 0,
        variant_products: 0,
        box_slots: 0,
        storage_locations: 0,
      },
      results: {
        customers: [{ id: 1, type: 'customer', name: 'Test Customer' }],
        sales_records: [{ id: 2, type: 'sales_record', record_number: '123' }],
        parent_products: [],
        variant_products: [],
        box_slots: [],
        storage_locations: [],
      }
    };
    
    // Mock the api.get to return the mockResponse
    (api.get as jest.Mock).mockReturnValueOnce({
      json: () => Promise.resolve(mockResponse)
    });
    
    const { result } = renderHook(() => useGlobalSearch());
    
    act(() => {
      result.current.setQuery('test');
    });
    
    // Fast-forward debounce timer
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // Wait for the async update
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
      expect(result.current.results).toEqual(mockResponse);
    });
    
    expect(api.get).toHaveBeenCalledWith(`search/search/?q=test`);
  });

  it('should not fetch when query is empty', async () => {
    const { result } = renderHook(() => useGlobalSearch());
    
    act(() => {
      result.current.setQuery('');
    });
    
    // Fast-forward debounce timer
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    expect(api.get).not.toHaveBeenCalled();
  });

  it('should handle error correctly', async () => {
    // Mock the api.get to throw an error
    (api.get as jest.Mock).mockImplementationOnce(() => {
      throw new Error('API error');
    });
    
    const { result } = renderHook(() => useGlobalSearch());
    
    act(() => {
      result.current.setQuery('test');
    });
    
    // Fast-forward debounce timer
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // Wait for the async update
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe('API error');
    });
  });

  it('should reset state when reset is called', () => {
    const { result } = renderHook(() => useGlobalSearch());
    
    act(() => {
      result.current.setQuery('test');
    });
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.query).toBe('');
    expect(result.current.results).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should return flattened results with getAllResults', async () => {
    const mockResponse = {
      query: 'test',
      total_count: 2,
      counts: {
        customers: 1,
        sales_records: 1,
        parent_products: 0,
        variant_products: 0,
        box_slots: 0,
        storage_locations: 0,
      },
      results: {
        customers: [{ id: 1, type: 'customer', name: 'Test Customer' }],
        sales_records: [{ id: 2, type: 'sales_record', record_number: '123' }],
        parent_products: [],
        variant_products: [],
        box_slots: [],
        storage_locations: [],
      }
    };
    
    // Mock the api.get to return the mockResponse
    (api.get as jest.Mock).mockReturnValueOnce({
      json: () => Promise.resolve(mockResponse)
    });
    
    const { result } = renderHook(() => useGlobalSearch());
    
    act(() => {
      result.current.setQuery('test');
    });
    
    // Fast-forward debounce timer
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    // Wait for the async update
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
      expect(result.current.results).toEqual(mockResponse);
    });
    
    expect(result.current.getAllResults()).toEqual([
      { id: 1, type: 'customer', name: 'Test Customer' },
      { id: 2, type: 'sales_record', record_number: '123' }
    ]);
  });
}); 