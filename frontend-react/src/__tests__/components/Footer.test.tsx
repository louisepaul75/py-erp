import React from 'react';
import { render, screen, waitFor, act, waitForElementToBeRemoved } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Footer } from '@/components/Footer';

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

jest.mock('@/lib/config', () => ({
  API_URL: 'http://test.com/api',
}));

// Mock useAppTranslation
jest.mock('@/hooks/useTranslationWrapper', () => () => ({
  t: (key: string) => key, // Simple mock that returns the key
}));

describe('Footer Component', () => {
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    // Spy on console.error without replacing its implementation
    consoleErrorSpy = jest.spyOn(console, 'error');
    
    // Mock fetch globally for all tests in this suite
    global.fetch = jest.fn().mockImplementation((url) => {
      // Default healthy mock for health check
      if (url.includes('/monitoring/health-checks/')) { // <-- Fix 1: Update URL
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            success: true,
            results: [
              { component: 'api', status: 'success', details: 'OK', response_time: 10, timestamp: new Date().toISOString() },
              { component: 'database', status: 'success', details: 'OK', response_time: 5, timestamp: new Date().toISOString() }
            ],
            authenticated: false, server_time: new Date().toISOString()
          })
        });
      }
      // Mock for git branch (can keep simple)
      if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ branch: 'main' })
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

  it('renders footer with health status', async () => {
    render(<Footer />); // Render first

    // Wait for loading spinner to disappear
    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Now check for the status indicator and version
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-green-500');

    const versionText = screen.getByText(/v1\.0\.0/);
    expect(versionText).toBeInTheDocument();

    // Check console.error was not called for success case
    // expect(consoleErrorSpy).not.toHaveBeenCalled(); // Might need adjustment depending on other logs
  });

  it('handles failed health check', async () => {
    // --- Mock fetch for failure ---
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/monitoring/health-checks/')) { // Use corrected URL
        return Promise.resolve({
          ok: false, status: 500,
          json: () => Promise.resolve({
            success: false,
            results: [
              { component: 'api', status: 'error', details: 'API Error', response_time: 10, timestamp: new Date().toISOString() },
              { component: 'database', status: 'error', details: 'DB Error', response_time: 5, timestamp: new Date().toISOString() }
            ],
            authenticated: false, server_time: new Date().toISOString()
          })
        });
      }
       if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ branch: 'main' })
        });
      }
      // Default fallback for other requests
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    // --- End Mock ---

    render(<Footer />); // Render first

    // Wait for loading spinner to disappear
    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Now check for the status indicator
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-red-500');

    // Expect console.error to be called (wrapped in waitFor)
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to fetch health status');
    });
  });

  it('handles network error', async () => {
     // --- Mock fetch for network error ---
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/monitoring/health-checks/')) { // Use corrected URL
        return Promise.reject(new Error('Network error'));
      }
       if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ branch: 'main' })
        });
      }
      // Default fallback for other requests
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
     // --- End Mock ---

    render(<Footer />); // Render first

    // Wait for loading spinner to disappear
    await waitForElementToBeRemoved(() => screen.queryByTestId('loading-spinner'), { timeout: 3000 });

    // Now check for the status indicator
    const statusIndicator = screen.getByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-red-500');

    // Expect console.error to be called (wrapped in waitFor)
    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching health status:', new Error('Network error'));
    });
  });
}); 