import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
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

describe('Footer Component', () => {
  // Spy on console.error before all tests
  let consoleErrorSpy: jest.SpyInstance;

  beforeAll(() => {
    // Mock console.error to prevent logging during tests
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterAll(() => {
    // Restore console.error after all tests
    consoleErrorSpy.mockRestore();
  });

  beforeEach(() => {
    // Clear mock calls before each test
    consoleErrorSpy.mockClear();
    
    // Reset fetch mock before each test
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
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
      if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ branch: 'main' })
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders footer with health status', async () => {
    render(<Footer />);

    // Wait for loading state
    const loadingSpinner = await screen.findByTestId('loading-spinner');
    expect(loadingSpinner).toBeInTheDocument();

    // Wait for health status to be rendered
    await waitFor(() => {
      const statusIndicator = screen.getByTestId('api-status-indicator');
      expect(statusIndicator).toHaveClass('bg-green-500');
    });

    // Verify version is displayed
    const versionText = await screen.findByText(/v1\.0\.0/);
    expect(versionText).toBeInTheDocument();

    // Verify no console errors were logged
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('handles failed health check', async () => {
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.resolve({
          ok: false,
          json: () => Promise.resolve({
            status: 'unhealthy',
            database: { status: 'unhealthy', message: 'Connection failed' },
            environment: 'test',
            version: '1.0.0'
          })
        });
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ branch: 'main' })
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<Footer />);

    // Wait for error state to be rendered
    await waitFor(() => {
      const statusIndicator = screen.getByTestId('api-status-indicator');
      expect(statusIndicator).toHaveClass('bg-red-500');
    });

    // Verify the correct error was logged
    expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to fetch health status');
  });

  it('handles network error', async () => {
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
        return Promise.reject(new Error('Network error'));
      }
      if (url.includes('/git/branch/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ branch: 'main' })
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<Footer />);

    // Wait for error state to be rendered
    await waitFor(() => {
      const statusIndicator = screen.getByTestId('api-status-indicator');
      expect(statusIndicator).toHaveClass('bg-red-500');
    });

    // Verify the correct error was logged
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching health status:', new Error('Network error'));
  });
}); 