import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
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
        // Return a response matching the HealthStatus interface
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            success: true, // Match expected structure
            results: [    // Match expected structure
              { component: 'api', status: 'success', details: 'OK', response_time: 10, timestamp: new Date().toISOString() },
              { component: 'database', status: 'success', details: 'Connected', response_time: 5, timestamp: new Date().toISOString() }
            ],
            authenticated: true, 
            server_time: new Date().toISOString() 
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
    render(<Footer />); // Render first
    // Optionally wait for initial loading state if it's consistently visible
    // await screen.findByTestId('loading-spinner', {}, { timeout: 500 });

    await act(async () => { // Wrap the async find and assertions in act
      const statusIndicator = await screen.findByTestId('api-status-indicator', {}, { timeout: 2000 }); 
      expect(statusIndicator).toBeInTheDocument();
      expect(statusIndicator).toHaveClass('bg-green-500');
      
      const versionText = await screen.findByText(/v1\.0\.0/, {}, { timeout: 2000 });
      expect(versionText).toBeInTheDocument();
    });
    // expect(consoleErrorSpy).not.toHaveBeenCalled(); 
  });

  it('handles failed health check', async () => {
    // --- Mock fetch for failure --- 
    global.fetch = jest.fn().mockImplementation((url) => {
      if (url.includes('/health/')) {
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
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    // --- End Mock --- 
    
    render(<Footer />); // Render first

    await act(async () => { // Wrap the async find and assertions in act
      const statusIndicator = await screen.findByTestId('api-status-indicator', {}, { timeout: 2000 });
      expect(statusIndicator).toBeInTheDocument();
      expect(statusIndicator).toHaveClass('bg-red-500');
    });
    // expect(consoleErrorSpy).toHaveBeenCalledWith(/* Expected error message */);
  });

  it('handles network error', async () => {
     // --- Mock fetch for network error --- 
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
     // --- End Mock --- 

    render(<Footer />); // Render first

    await act(async () => { // Wrap the async find and assertions in act
      const statusIndicator = await screen.findByTestId('api-status-indicator', {}, { timeout: 2000 });
      expect(statusIndicator).toBeInTheDocument();
      expect(statusIndicator).toHaveClass('bg-red-500');
    });

    expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching health status:', new Error('Network error'));
  });
}); 