import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react';
import { Footer } from '@/components/Footer';
import * as translationModule from '@/hooks/useTranslationWrapper';
import { API_URL } from '@/lib/config';

// Mock next/link
jest.mock('next/link', () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => children,
  };
});

// Mock translation hook
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (str: string) => str,
    i18n: {
      changeLanguage: () => new Promise(() => {}),
    },
  }),
}));

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Footer', () => {
  beforeEach(() => {
    mockFetch.mockReset();
    mockFetch.mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            version: '1.0.0',
            git_branch: 'main',
            environment: 'development',
          }),
      })
    );
  });

  afterEach(() => {
    delete process.env.NEXT_PUBLIC_ENVIRONMENT;
    document.documentElement.style.setProperty('--dev-bar-height', '0px');
  });

  it('renders copyright information', async () => {
    await act(async () => {
      render(<Footer />);
    });

    expect(screen.getByText(/© \d{4} pyERP System/)).toBeInTheDocument();
  });

  it('shows version number when API is available', async () => {
    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      expect(screen.getByText('v1.0.0')).toBeInTheDocument();
    });
  });

  it('shows loading indicator while fetching', async () => {
    let resolvePromise: (value: any) => void;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    (global.fetch as jest.Mock).mockImplementationOnce(() => promise);

    await act(async () => {
      render(<Footer />);
    });

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

    await act(async () => {
      resolvePromise!({
        ok: true,
        json: () =>
          Promise.resolve({
            version: '1.0.0',
            git_branch: 'main',
            environment: 'development',
          }),
      });
    });
  });

  it('shows green indicator when API is healthy', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          status: 'healthy',
          version: '1.0.0',
        }),
    });

    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      const indicator = screen.getByTestId('api-status-indicator');
      expect(indicator).toHaveClass('bg-green-500');
    });
  });

  it('shows red indicator when API is unhealthy', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          status: 'unhealthy',
          version: '1.0.0',
        }),
    });

    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      const indicator = screen.getByTestId('api-status-indicator');
      expect(indicator).toHaveClass('bg-red-500');
    });
  });

  it('shows development mode bar in development environment', async () => {
    process.env.NEXT_PUBLIC_ENVIRONMENT = 'development';

    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      expect(screen.getByText(/DEV MODE/)).toBeInTheDocument();
    });
  });

  it('toggles dev bar on click', async () => {
    process.env.NEXT_PUBLIC_ENVIRONMENT = 'development';
    const user = userEvent.setup();

    await act(async () => {
      render(<Footer />);
    });

    const devBar = await screen.findByText(/DEV MODE/);
    await act(async () => {
      await user.click(devBar);
    });

    await waitFor(() => {
      expect(document.documentElement.style.getPropertyValue('--dev-bar-height')).toBe('200px');
    });

    await act(async () => {
      await user.click(devBar);
    });

    await waitFor(() => {
      expect(document.documentElement.style.getPropertyValue('--dev-bar-height')).toBe('24px');
    });
  });

  it('handles API fetch error gracefully', async () => {
    mockFetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      expect(screen.getByTestId('api-status-indicator')).toHaveClass('bg-red-500');
    });
  });
}); 