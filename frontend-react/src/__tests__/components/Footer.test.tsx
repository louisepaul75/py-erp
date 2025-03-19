import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Footer } from '@/components/Footer';
import * as translationModule from '@/hooks/useTranslationWrapper';
import { API_URL } from '@/lib/config';
import { act } from 'react-dom/test-utils';

// Mock next/link
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>;
  },
}));

// Mock translation hook
jest.mock('@/hooks/useTranslationWrapper', () => ({
  __esModule: true,
  default: jest.fn(),
}));

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Footer', () => {
  // Define common mock data
  const mockHealthData = {
    status: 'healthy',
    database: { status: 'connected', message: 'Database is connected' },
    environment: 'development',
    version: '1.0.0-dev',
  };

  const mockGitData = {
    branch: 'main',
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock translation
    const mockUseTranslation = jest.fn().mockReturnValue({
      t: (key: string) => {
        const translations: Record<string, string> = {
          'health.debugInfo': 'Debug Information',
          'health.environment': 'Environment',
          'health.version': 'Version',
          'health.databaseStatus': 'Database Status',
          'health.gitBranch': 'Git Branch',
          'health.apiAvailable': 'API Available',
          'common.yes': 'Yes',
          'common.no': 'No',
        };
        return translations[key] || key;
      },
    });
    jest.spyOn(translationModule, 'default').mockImplementation(mockUseTranslation);

    // Mock successful fetch responses
    mockFetch.mockImplementation((url) => {
      if (url === `${API_URL}/health`) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockHealthData),
        });
      } else if (url === `${API_URL}/git/branch`) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockGitData),
        });
      }
      return Promise.reject(new Error('Not found'));
    });

    // Mock DOM methods
    Element.prototype.getBoundingClientRect = jest.fn().mockReturnValue({
      height: 50,
      width: 100,
      top: 0,
      left: 0,
      right: 100,
      bottom: 50,
    });

    // Mock document querySelector
    document.querySelector = jest.fn().mockImplementation(() => ({
      getBoundingClientRect: () => ({
        height: 50,
      }),
    }));

    // Mock style property
    document.documentElement.style.setProperty = jest.fn();
  });

  it('renders the copyright information', async () => {
    render(<Footer />);
    const currentYear = new Date().getFullYear();
    expect(screen.getByText(`© ${currentYear} pyERP System`)).toBeInTheDocument();
  });

  it('displays the version number from the health API', async () => {
    await act(async () => {
      render(<Footer />);
    });
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(`v${mockHealthData.version}`)).toBeInTheDocument();
    });
  });

  it('shows a loading indicator while fetching health status', async () => {
    // Set up a delayed mock response to ensure loading state is captured
    mockFetch.mockImplementationOnce(() => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: () => Promise.resolve(mockHealthData),
          });
        }, 100);
      });
    });

    render(<Footer />);
    
    // The loading indicator should be visible - use the screen object instead of document
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });

  it('shows the DEV MODE bar in development environment', async () => {
    // Ensure we're in development mode
    const originalNodeEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    await act(async () => {
      render(<Footer />);
    });
    
    // Wait for health data to load
    await waitFor(() => {
      expect(screen.getByText(/DEV MODE/)).toBeInTheDocument();
    });
    
    // Reset environment
    process.env.NODE_ENV = originalNodeEnv;
  });

  it('toggles the dev bar when clicking the button', async () => {
    // Ensure we're in development mode
    const originalNodeEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    await act(async () => {
      render(<Footer />);
    });
    
    // Wait for health data to load
    await waitFor(() => {
      expect(screen.getByText(/DEV MODE/)).toBeInTheDocument();
    });
    
    // Initially, the dev bar content should be hidden
    expect(screen.queryByText('Debug Information')).not.toBeInTheDocument();
    
    // Click the toggle button
    await act(async () => {
      fireEvent.click(screen.getByText(/DEV MODE/));
    });
    
    // Now the dev bar content should be visible
    expect(screen.getByText('Debug Information')).toBeInTheDocument();
    
    // Reset environment
    process.env.NODE_ENV = originalNodeEnv;
  });

  it('displays git branch information when available', async () => {
    // Ensure we're in development mode
    const originalNodeEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    await act(async () => {
      render(<Footer />);
    });
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/DEV MODE \(main\)/)).toBeInTheDocument();
    });
    
    // Click the toggle button to see debug info
    await act(async () => {
      fireEvent.click(screen.getByText(/DEV MODE/));
    });
    
    // Check git branch info
    expect(screen.getByText('main')).toBeInTheDocument();
    
    // Reset environment
    process.env.NODE_ENV = originalNodeEnv;
  });

  it('handles API fetch errors gracefully', async () => {
    // Mock failed fetch response
    mockFetch.mockImplementationOnce(() => {
      return Promise.resolve({
        ok: false,
      });
    });
    
    render(<Footer />);
    
    // Even with a failed fetch, the default mock data should be used
    // So it will still show the version from the mockHealthStatus default
    await waitFor(() => {
      expect(screen.getByText(`v1.0.0-dev`)).toBeInTheDocument();
    });
  });

  it('updates CSS variables when dev bar is expanded', async () => {
    // Ensure we're in development mode
    const originalNodeEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    await act(async () => {
      render(<Footer />);
    });
    
    // Wait for health data to load
    await waitFor(() => {
      expect(screen.getByText(/DEV MODE/)).toBeInTheDocument();
    });
    
    // Click the toggle button
    await act(async () => {
      fireEvent.click(screen.getByText(/DEV MODE/));
    });
    
    // Wait for the setTimeout in the component to execute
    await waitFor(() => {
      expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--dev-bar-height', '50px');
    });
    
    // Reset environment
    process.env.NODE_ENV = originalNodeEnv;
  });

  it('displays API status correctly', async () => {
    // Ensure we're in development mode
    const originalNodeEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    await act(async () => {
      render(<Footer />);
    });
    
    // Wait for health data to load
    await waitFor(() => {
      expect(screen.getByText(/DEV MODE/)).toBeInTheDocument();
    });
    
    // Click the toggle button
    await act(async () => {
      fireEvent.click(screen.getByText(/DEV MODE/));
    });
    
    // Check API available status
    expect(screen.getByText('Yes')).toBeInTheDocument();
    
    // Reset environment
    process.env.NODE_ENV = originalNodeEnv;
  });
}); 