import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Footer } from './Footer'; // Corrected to named import

// Mock react-i18next
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key, // Simple mock returns the key
    i18n: {
      changeLanguage: () => new Promise(() => {}),
      language: 'en',
    },
  }),
}));

// Mock the custom translation hook if it does more than just call useTranslation
jest.mock('@/hooks/useTranslationWrapper', () => ({
  __esModule: true,
  default: () => ({
    t: (key: string) => key, // Simple mock returns the key
  }),
}));

describe('Footer', () => {
  // Mock fetch before each test
  beforeEach(() => {
    global.fetch = jest.fn((url) => {
      let responseData;
      if (url.toString().endsWith('/health/')) {
        responseData = { 
          status: 'healthy', 
          version: '1.2.3',
          database: { status: 'connected', message: 'OK' },
          environment: 'test',
        };
      } else if (url.toString().endsWith('/monitoring/health-checks/')) {
        responseData = { 
          success: true,
          results: [ // Provide the missing results array
            { component: 'database', status: 'operational', details: 'OK', response_time: 0.1, timestamp: new Date().toISOString() },
            { component: 'api', status: 'operational', details: 'OK', response_time: 0.2, timestamp: new Date().toISOString() },
          ],
          authenticated: false,
          server_time: new Date().toISOString(),
        };
      } else if (url.toString().endsWith('/git/branch/')) {
        responseData = { 
          branch: 'test-branch' 
        };
      } else {
        // Default or error case
        responseData = { message: 'Mock endpoint not configured' };
        return Promise.resolve({ 
          ok: false, 
          status: 404,
          headers: new Headers({ 'Content-Type': 'application/json' }),
          json: () => Promise.resolve(responseData)
        });
      }

      return Promise.resolve({
        ok: true,
        status: 200,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () => Promise.resolve(responseData),
      });
    }) as jest.Mock;
  });

  // Restore fetch after each test
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders footer text and link', async () => {
    render(<Footer />);
    // Check for static text
    expect(screen.getByText(/©\s*\d{4}\s*pyERP/)).toBeInTheDocument();

    // Wait for the fetch to complete and check for the version link
    // The link text itself is just the version, e.g., v1.2.3 (based on mock)
    const versionLink = await screen.findByRole('link', { name: /v1\.2\.3/ });
    expect(versionLink).toBeInTheDocument();
    expect(versionLink).toHaveAttribute('href', '/health-status');

    // Wait for the status indicator to appear and check its class
    // Based on the mock (/health/ returns 'healthy'), we expect 'bg-status-success'
    const statusIndicator = await screen.findByTestId('api-status-indicator');
    expect(statusIndicator).toBeInTheDocument();
    expect(statusIndicator).toHaveClass('bg-status-success');
  });

  it('shows loading spinner initially', () => {
    // ... existing code ...
  });
}); 