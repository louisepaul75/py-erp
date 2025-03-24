# React Testing Improvements Guide

This document provides specific guidance for fixing the React component testing issues identified in our latest test run. These improvements will make our tests more reliable and eliminate warnings.

## Common Issues Found

1. State updates not wrapped in `act()`
2. Asynchronous operations not properly handled
3. Network requests not properly mocked
4. Missing cleanup for event listeners and mocks

## Fixing the Footer Component Tests

The Footer component showed multiple `act()` warnings related to state updates from API calls. Here's how to fix this:

### Before (Problematic):

```tsx
// Footer.test.tsx
import { render, screen } from '@testing-library/react';
import Footer from '../../components/Footer';

test('renders footer correctly', () => {
  render(<Footer />);
  expect(screen.getByText(/Version/i)).toBeInTheDocument();
});
```

### After (Fixed):

```tsx
// Footer.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import Footer from '../../components/Footer';

beforeEach(() => {
  // Mock the fetch calls used in Footer
  jest.spyOn(global, 'fetch').mockImplementation((url) => {
    if (url.includes('/api/health-status')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          status: 'healthy',
          database: { status: 'healthy', message: 'Connected' },
          environment: 'test',
          version: '1.0.0'
        })
      });
    }
    if (url.includes('/api/git-branch')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          branch: 'main',
          commit: 'abc123'
        })
      });
    }
    return Promise.resolve({
      ok: false,
      json: () => Promise.resolve({})
    });
  });
});

afterEach(() => {
  // Clean up mocks
  jest.restoreAllMocks();
});

test('renders footer correctly', async () => {
  // Wrap the initial render in act
  await act(async () => {
    render(<Footer />);
  });

  // Wait for the async operations to complete
  await waitFor(() => {
    expect(screen.getByText(/Version: 1.0.0/i)).toBeInTheDocument();
    expect(screen.getByText(/Status: healthy/i)).toBeInTheDocument();
  });
});

test('handles API failure gracefully', async () => {
  // Override the mock for this specific test
  global.fetch = jest.fn(() => Promise.reject(new Error('API unavailable')));

  await act(async () => {
    render(<Footer />);
  });

  await waitFor(() => {
    expect(screen.getByText(/Status: unhealthy/i)).toBeInTheDocument();
  });
});
```

## Fixing Auth Hook Tests

The auth hook tests also showed `act()` warnings. Here's how to fix them:

### Before (Problematic):

```tsx
// authHooks.test.tsx
import { renderHook } from '@testing-library/react-hooks';
import { useAuth } from '../../lib/auth/authHooks';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';

const queryClient = new QueryClient();
const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

test('useAuth provides auth functions', () => {
  const { result } = renderHook(() => useAuth(), { wrapper });
  expect(result.current.isAuthenticated).toBe(false);
  expect(typeof result.current.login).toBe('function');
});
```

### After (Fixed):

```tsx
// authHooks.test.tsx
import { renderHook, act } from '@testing-library/react-hooks';
import { useAuth } from '../../lib/auth/authHooks';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import * as authService from '../../lib/auth/authService';

// Mock the auth service
jest.mock('../../lib/auth/authService', () => ({
  login: jest.fn(),
  logout: jest.fn(),
  refreshToken: jest.fn(),
  isAuthenticated: jest.fn(),
  getUser: jest.fn()
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0
      }
    }
  });
  
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useAuth hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Default mock implementations
    (authService.isAuthenticated as jest.Mock).mockReturnValue(false);
    (authService.getUser as jest.Mock).mockReturnValue(null);
    (authService.login as jest.Mock).mockResolvedValue({ token: 'fake-token' });
    (authService.logout as jest.Mock).mockImplementation(() => {});
    (authService.refreshToken as jest.Mock).mockResolvedValue('new-token');
  });

  test('provides auth state and functions', async () => {
    const wrapper = createWrapper();
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), { wrapper });
    
    // Initial state
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    
    // Login
    let loginPromise;
    await act(async () => {
      loginPromise = result.current.login('user', 'pass');
    });
    await loginPromise;
    
    // Should have called the service
    expect(authService.login).toHaveBeenCalledWith('user', 'pass');
  });

  test('handles login success', async () => {
    const user = { id: 1, username: 'testuser' };
    (authService.login as jest.Mock).mockResolvedValue({ token: 'token', user });
    (authService.isAuthenticated as jest.Mock).mockReturnValue(true);
    (authService.getUser as jest.Mock).mockReturnValue(user);
    
    const wrapper = createWrapper();
    const { result, waitForNextUpdate } = renderHook(() => useAuth(), { wrapper });
    
    let loginPromise;
    await act(async () => {
      loginPromise = result.current.login('user', 'pass');
    });
    await loginPromise;
    
    // Auth state should update
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(user);
  });
});
```

## General React Testing Best Practices

### 1. Wrapping State Updates

Always wrap state updates in `act()`:

```tsx
// For synchronous updates
act(() => {
  fireEvent.click(button);
});

// For asynchronous updates
await act(async () => {
  await userEvent.click(button);
  // Wait for any promises to resolve
});
```

### 2. Handling Asynchronous Operations

Use `waitFor` to wait for elements to appear or state to update:

```tsx
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});
```

### 3. Mock Network Requests

Mock fetch or axios consistently:

```tsx
// Create a utility for mocking API calls
export const mockApiCall = (url, data, status = 200) => {
  return jest.spyOn(global, 'fetch').mockImplementation((fetchUrl) => {
    if (fetchUrl.includes(url)) {
      return Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        json: () => Promise.resolve(data)
      });
    }
    return Promise.reject(new Error(`No mock for ${fetchUrl}`));
  });
};

// In tests
const mockApi = mockApiCall('/api/users', [{ id: 1, name: 'Test' }]);
```

### 4. Testing Custom Hooks

Use `renderHook` from `@testing-library/react-hooks`:

```tsx
const { result, waitForNextUpdate, rerender } = renderHook(
  (props) => useCustomHook(props),
  {
    initialProps: { initialValue: 5 },
    wrapper: ContextProvider
  }
);

// Test initial state
expect(result.current.value).toBe(5);

// Update props
rerender({ initialValue: 10 });

// Update state within the hook
act(() => {
  result.current.setValue(20);
});

// Check state after update
expect(result.current.value).toBe(20);
```

### 5. Clean Up

Always clean up after tests:

```tsx
afterEach(() => {
  jest.restoreAllMocks();
  cleanup(); // from @testing-library/react
});
```

## Creating a Testing Utility Library

To standardize these patterns, create a testing utility file at `src/__tests__/utils/test-helpers.tsx`:

```tsx
import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a custom render function that includes providers
export function renderWithProviders(
  ui,
  {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0
        }
      }
    }),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  }
  return { queryClient, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

// Mock API calls
export function mockFetch(mocks = {}) {
  return jest.spyOn(global, 'fetch').mockImplementation((url) => {
    // Convert the URL to a string if it's a Request object
    const urlString = url instanceof Request ? url.url : url.toString();
    
    // Find a matching mock
    for (const [path, response] of Object.entries(mocks)) {
      if (urlString.includes(path)) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(response),
          text: () => Promise.resolve(JSON.stringify(response))
        });
      }
    }
    
    // No match found
    return Promise.reject(new Error(`No mock for ${urlString}`));
  });
}
```

## Next Steps

1. Fix the Footer component tests first, as they have the most warnings
2. Update auth hook tests to use proper act() wrapping
3. Create the test utilities file for consistent patterns
4. Apply these patterns to all new tests
5. Gradually update existing tests using this guide

By implementing these changes, we'll eliminate the act() warnings and make our React tests more robust and reliable. 