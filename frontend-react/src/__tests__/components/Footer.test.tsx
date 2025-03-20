import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Footer } from '@/components/Footer';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

// Mock react-i18next
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

describe('Footer', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch = jest.fn();
    
    // Reset document styles
    document.documentElement.style.setProperty('--footer-height', '0px');
    document.documentElement.style.setProperty('--dev-bar-height', '0px');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders copyright information', () => {
    render(<Footer />);
    expect(screen.getByText(/© \d{4} pyERP System/)).toBeInTheDocument();
  });

  it('shows version number when API is available', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy', version: '1.0.0' }),
    });

    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      expect(screen.getByText(/v1\.0\.0/)).toBeInTheDocument();
    });
  });

  it('shows loading indicator while fetching data', async () => {
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));

    await act(async () => {
      render(<Footer />);
    });
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('shows green indicator when API is healthy', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ status: 'healthy', version: '1.0.0' }),
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
      json: () => Promise.resolve({ status: 'unhealthy', version: '1.0.0' }),
    });

    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      const indicator = screen.getByTestId('api-status-indicator');
      expect(indicator).toHaveClass('bg-red-500');
    });
  });

  it('shows red indicator when API fetch fails', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    });

    await act(async () => {
      render(<Footer />);
    });
    
    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    });

    await waitFor(() => {
      const indicator = screen.getByTestId('api-status-indicator');
      expect(indicator).toHaveClass('bg-red-500');
    });
  });

  it('toggles development bar on click and updates height', async () => {
    const user = userEvent.setup();
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ 
          status: 'healthy', 
          version: '1.0.0', 
          environment: 'development' 
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ branch: 'main' }),
      });

    await act(async () => {
      render(<Footer />);
    });
    
    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    });

    const devModeButton = screen.getByText(/DEV MODE/);
    expect(devModeButton).toBeInTheDocument();

    const mockDevBarHeight = 200;
    const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = jest.fn().mockReturnValue({
      height: mockDevBarHeight,
      width: 100,
      top: 0,
      left: 0,
      right: 100,
      bottom: mockDevBarHeight,
      x: 0,
      y: 0,
    });

    // Click to expand
    await act(async () => {
      await user.click(devModeButton);
    });

    await waitFor(() => {
      const height = document.documentElement.style.getPropertyValue('--dev-bar-height');
      expect(height).toBe(`${mockDevBarHeight}px`);
    });

    // Click to collapse
    await act(async () => {
      await user.click(devModeButton);
    });

    await waitFor(() => {
      expect(document.documentElement.style.getPropertyValue('--dev-bar-height')).toBe('0px');
    });

    Element.prototype.getBoundingClientRect = originalGetBoundingClientRect;
    process.env.NODE_ENV = originalEnv;
  });
}); 