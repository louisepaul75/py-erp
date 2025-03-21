import React from 'react';
import { render, RenderOptions, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

/**
 * Creates a wrapper with a new QueryClient for testing React Query hooks and components
 */
export function createQueryClientWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
        staleTime: 0,
        refetchOnWindowFocus: false,
      },
    },
    logger: {
      log: console.log,
      warn: console.warn,
      error: () => {}, // Silence errors during tests
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

/**
 * Custom render function with QueryClient provider
 */
export function renderWithQueryClient(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) {
  const wrapper = createQueryClientWrapper();
  return render(ui, { wrapper, ...options });
}

/**
 * Mock fetch API for a specific URL and response
 */
export function mockFetch(mocks: Record<string, any> = {}) {
  return jest.spyOn(global, 'fetch').mockImplementation((url) => {
    const urlString = url instanceof Request ? url.url : String(url);
    
    // Find matching mock
    for (const [path, response] of Object.entries(mocks)) {
      if (urlString.includes(path)) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(response),
          text: () => Promise.resolve(JSON.stringify(response)),
        });
      }
    }
    
    // Default response if no match (API unavailable)
    return Promise.resolve({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ error: "Not found" }),
      text: () => Promise.resolve("Not found"),
    });
  });
}

/**
 * Helper to mock a failed fetch with proper error
 */
export function mockFetchError(errorMessage: string = "Network error") {
  return jest.spyOn(global, 'fetch').mockImplementation(() => {
    return Promise.reject(new Error(errorMessage));
  });
}

/**
 * Helper to wait for asynchronous operations in tests
 * Useful for waiting for state updates caused by useEffect
 */
export async function waitForAsync(callback: () => boolean, timeout = 1000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (callback()) {
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  throw new Error(`Timed out waiting for condition after ${timeout}ms`);
}

/**
 * Helper for testing components with React Query
 * Provides common mocks and utilities
 */
export function setupReactQueryTest() {
  // Create a clean QueryClient for each test
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
    },
  });
  
  // Silence React Query error logging
  const originalConsoleError = console.error;
  beforeAll(() => {
    console.error = (...args: any[]) => {
      if (
        typeof args[0] === 'string' &&
        args[0].includes('React Query') &&
        args[0].includes('Error')
      ) {
        return;
      }
      originalConsoleError(...args);
    };
  });
  
  afterAll(() => {
    console.error = originalConsoleError;
  });
  
  beforeEach(() => {
    queryClient.clear();
  });
  
  return {
    queryClient,
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    ),
  };
}

/**
 * Helper to mock window.fetch specifically for API endpoints
 */
export function mockApiEndpoint(endpoint: string, responseData: any, status = 200) {
  const mockResponse = {
    ok: status >= 200 && status < 300,
    status,
    json: jest.fn().mockResolvedValue(responseData),
  };
  
  return jest.spyOn(global, 'fetch').mockImplementation((url) => {
    const urlString = url instanceof Request ? url.url : String(url);
    if (urlString.includes(endpoint)) {
      return Promise.resolve(mockResponse as unknown as Response);
    }
    return Promise.reject(new Error(`No mock for ${urlString}`));
  });
} 