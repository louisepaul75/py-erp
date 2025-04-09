import React from 'react';
import { screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Footer } from '@/components/Footer';
import { render } from '../utils/test-utils';

// Mock the i18n functionality at component level
jest.mock('react-i18next', () => ({
  // Mock the useTranslation hook
  useTranslation: () => {
    return {
      t: (key: string) => key,
      i18n: {
        changeLanguage: jest.fn(),
        language: 'en'
      }
    };
  }
}));

// Mock auth hooks
jest.mock('@/lib/auth/authHooks', () => ({
  useIsAuthenticated: () => ({ isAuthenticated: true }),
  useUser: () => ({ user: null, isLoading: false, error: null })
}));

jest.mock('@/lib/config', () => ({
  API_URL: 'http://test.com/api',
}));

// Mock useAppTranslation
jest.mock('@/hooks/useTranslationWrapper', () => () => ({
  t: (key: string) => key, // Simple mock that returns the key
}));

// Define mock data structures based on actual component interfaces
const mockHealthyHealthResponse = {
  status: 'healthy',
  database: { status: 'connected', message: 'OK' },
  environment: 'development',
  version: '0.6.0'
};

const mockWarningHealthResponse = {
  status: 'warning',
  database: { status: 'connected', message: 'OK' },
  environment: 'development',
  version: '0.6.1'
};

const mockErrorHealthResponse = {
  status: 'error',
  database: { status: 'disconnected', message: 'Error' },
  environment: 'development',
  version: '0.6.2'
};

const mockHealthChecksResponse = {
  success: true,
  results: [
    { component: 'api', status: 'success', details: 'OK', response_time: 10, timestamp: new Date().toISOString() },
    { component: 'database', status: 'success', details: 'OK', response_time: 5, timestamp: new Date().toISOString() }
  ],
  authenticated: false, server_time: new Date().toISOString()
};

const mockGitBranchResponse = { branch: 'main' };

describe('Footer Component', () => {
  let consoleErrorSpy: jest.SpyInstance;

  // Use fake timers to control async operations
  beforeAll(() => {
    jest.useFakeTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  beforeEach(() => {
    // Spy on console.error without replacing its implementation
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {}); // Mock implementation to silence console
    
    // Mock fetch globally for all tests in this suite
    global.fetch = jest.fn().mockImplementation((url) => {
      // Default healthy mock for /health/
      if (url.includes('/health/')) {
        return Promise.resolve({
          ok: true,
          headers: { get: () => 'application/json' }, // Ensure headers are mocked
          json: () => Promise.resolve(mockHealthyHealthResponse)
        });
      }
      // Default healthy mock for health checks (used for dev bar condition)
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({
          ok: true,
          headers: { get: () => 'application/json' }, // Ensure headers are mocked
          json: () => Promise.resolve(mockHealthChecksResponse)
        });
      }
      // Mock for git branch
      if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          headers: { get: () => 'application/json' }, // Ensure headers are mocked
          json: () => Promise.resolve(mockGitBranchResponse)
        });
      }
      // Default fallback for other requests
      return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve({}) });
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    consoleErrorSpy.mockRestore(); // Restore console.error
    // Clear any pending timers
    jest.clearAllTimers(); 
  });

  it('renders footer with healthy status and correct version', async () => {
    render(<Footer />); 

    // Advance timers minimally to allow initial useEffect fetches and state updates
    act(() => {
      jest.advanceTimersByTime(1);
    });

    // Wait specifically for the version text from the mock response to appear
    const versionText = await screen.findByText(`v${mockHealthyHealthResponse.version}`);
    expect(versionText).toBeInTheDocument();

    // Now check the status indicator class
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toHaveClass('bg-status-success');

    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('renders footer with warning status and correct version', async () => {
    // Override fetch mock for /health/ to return warning status
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.resolve({
          ok: true,
          headers: { get: () => 'application/json' },
          json: () => Promise.resolve(mockWarningHealthResponse)
        });
      }
      // Keep other mocks default/healthy
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve({}) });
    });

    render(<Footer />); 

    // Advance timers minimally
    act(() => {
      jest.advanceTimersByTime(1);
    });

    // Wait specifically for the version text from the mock response to appear
    const versionText = await screen.findByText(`v${mockWarningHealthResponse.version}`);
    expect(versionText).toBeInTheDocument();

    // Now check the status indicator class
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toHaveClass('bg-status-warning');

    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });


  it('handles error status from /health/ endpoint', async () => {
    // Override fetch mock for /health/ to return error status
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.resolve({
          ok: true, 
          headers: { get: () => 'application/json' },
          json: () => Promise.resolve(mockErrorHealthResponse)
        });
      }
      // Keep other mocks default/healthy
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve({}) });
    });

    render(<Footer />); 

    // Advance timers minimally
    act(() => {
      jest.advanceTimersByTime(1);
    });

    // Wait specifically for the version text from the mock response to appear
    const versionText = await screen.findByText(`v${mockErrorHealthResponse.version}`);
    expect(versionText).toBeInTheDocument();

    // Now check the status indicator class
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toHaveClass('bg-status-error');

    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('handles failed API call for /health/ endpoint', async () => {
    // Mock fetch for failure on /health/
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.resolve({ ok: false, status: 500, headers: { get: () => 'text/plain' } }); // Simulate server error, non-JSON response
      }
       // Keep other mocks default/healthy
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve({}) });
    });

    render(<Footer />); 

    // Advance timers minimally
    act(() => {
      jest.advanceTimersByTime(1);
    });

    // Check for the RED status indicator (fallback)
    const statusIndicator = await screen.findByTestId('api-status-indicator'); // Use findBy here too, as state update is async
    expect(statusIndicator).toHaveClass('bg-status-error');

    // Check for the fallback version 
    const versionText = await screen.findByText('v0.0.0'); // Use findBy here
    expect(versionText).toBeInTheDocument();

    // Expect console.error for the failed /health/ fetch
    await waitFor(() => {
      // Error message might vary slightly depending on fetch mock details, check for core message
      expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Failed to fetch overall health status'));
    });
  });

  it('handles network error fetching /health/ endpoint', async () => {
     // Mock fetch for network error on /health/
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.reject(new Error('Network error'));
      }
      // Keep other mocks default/healthy
       if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, headers: { get: () => 'application/json' }, json: () => Promise.resolve({}) });
    });

    render(<Footer />); 

    // Advance timers minimally
    act(() => {
       jest.advanceTimersByTime(1);
     });

    // Check for the RED status indicator (fallback)
    const statusIndicator = await screen.findByTestId('api-status-indicator'); // Use findBy
    expect(statusIndicator).toHaveClass('bg-status-error');

    // Check for the fallback version
    const versionText = await screen.findByText('v0.0.0'); // Use findBy
    expect(versionText).toBeInTheDocument();

    // Expect console.error for the network error on /health/ fetch
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching overall health status:', new Error('Network error'));
    });
  });
}); 