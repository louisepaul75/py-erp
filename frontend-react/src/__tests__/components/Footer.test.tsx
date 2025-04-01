import React from 'react';
import { render, screen, waitFor, act, waitForElementToBeRemoved } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Footer } from '@/components/Footer';

// Mock the i18n functionality at component level
jest.mock('react-i18next', () => ({
  // Mock the useTranslation hook
  useTranslation: () => {
    return {
      t: (key) => key,
      i18n: {
        changeLanguage: jest.fn(),
        language: 'en'
      }
    };
  }
}));

jest.mock('@/lib/config', () => ({
  API_URL: 'http://test.com/api',
}));

// Mock useAppTranslation
jest.mock('@/hooks/useTranslationWrapper', () => () => ({
  t: (key) => key, // Simple mock that returns the key
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
  let consoleErrorSpy;

  beforeEach(() => {
    // Spy on console.error without replacing its implementation
    consoleErrorSpy = jest.spyOn(console, 'error');
    
    // Mock fetch globally for all tests in this suite
    global.fetch = jest.fn().mockImplementation((url) => {
      // Default healthy mock for /health/
      if (url.includes('/health/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockHealthyHealthResponse)
        });
      }
      // Default healthy mock for health checks (used for dev bar condition)
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockHealthChecksResponse)
        });
      }
      // Mock for git branch
      if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGitBranchResponse)
        });
      }
      // Default fallback for other requests
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    consoleErrorSpy.mockRestore(); // Restore console.error
  });

  it('renders footer with healthy status and correct version', async () => {
    // Fetch mock is already set up for healthy state in beforeEach
    render(<Footer />); 

    // Wait for loading spinner to disappear (checks both fetches)
    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Check for the GREEN status indicator
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-green-500');

    // Check for the version from the mocked /health/ response
    const versionText = screen.getByText(`v${mockHealthyHealthResponse.version}`);
    expect(versionText).toBeInTheDocument();

    // Check console.error was not called
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('renders footer with warning status and correct version', async () => {
    // Override fetch mock for /health/ to return warning status
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockWarningHealthResponse)
        });
      }
      // Keep other mocks default/healthy
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<Footer />); 

    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Check for the YELLOW status indicator
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-yellow-500');

    // Check for the version from the mocked /health/ response
    const versionText = screen.getByText(`v${mockWarningHealthResponse.version}`);
    expect(versionText).toBeInTheDocument();

    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });


  it('handles error status from /health/ endpoint', async () => {
    // Override fetch mock for /health/ to return error status
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.resolve({
          ok: true, // API call itself is ok, but status is error
          json: () => Promise.resolve(mockErrorHealthResponse)
        });
      }
      // Keep other mocks default/healthy
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<Footer />); 

    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Check for the RED status indicator
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-red-500');

    // Check for the version from the mocked /health/ response
    const versionText = screen.getByText(`v${mockErrorHealthResponse.version}`);
    expect(versionText).toBeInTheDocument();

    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('handles failed API call for /health/ endpoint', async () => {
    // --- Mock fetch for failure on /health/ ---
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.resolve({ ok: false, status: 500 }); // Simulate server error
      }
      // Keep other mocks default/healthy
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    // --- End Mock ---

    render(<Footer />); 

    // Wait for loading spinner to disappear
    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Check for the RED status indicator (fallback)
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-red-500');

    // Check for the fallback version (adjust if env var is set in test env)
    const versionText = screen.getByText('v0.0.0');
    expect(versionText).toBeInTheDocument();

    // Expect console.error for the failed /health/ fetch
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to fetch overall health status');
    });
  });

  it('handles network error fetching /health/ endpoint', async () => {
     // --- Mock fetch for network error on /health/ ---
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.reject(new Error('Network error'));
      }
      // Keep other mocks default/healthy
      if (url.includes('/monitoring/health-checks/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockHealthChecksResponse) });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockGitBranchResponse) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
     // --- End Mock ---

    render(<Footer />); 

    // Wait for loading spinner to disappear
    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Check for the RED status indicator (fallback)
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-red-500');

    // Check for the fallback version (adjust if env var is set in test env)
    const versionText = screen.getByText('v0.0.0');
    expect(versionText).toBeInTheDocument();

    // Expect console.error for the network error on /health/ fetch
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching overall health status:', new Error('Network error'));
    });
  });
}); 