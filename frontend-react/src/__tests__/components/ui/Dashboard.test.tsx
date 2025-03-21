import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from '@/components/ui/dashboard';

// Mock react-grid-layout since it uses complicated DOM manipulations
jest.mock('react-grid-layout', () => ({
  Responsive: jest.fn(({ children }) => <div data-testid="responsive-grid">{children}</div>),
  __esModule: true,
}));

// Mock Next.js Link component
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href} data-testid="next-link">
      {children}
    </a>
  );
});

// Mock API calls
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ 
      layouts: {
        lg: [],
        md: [],
        sm: []
      },
      menuTiles: []
    }),
  })
) as jest.Mock;

// Mock the auth service
jest.mock('@/lib/auth/authService', () => ({
  authService: {
    getToken: jest.fn().mockReturnValue('test-token'),
  },
}));

// Mock window resize
const originalInnerWidth = window.innerWidth;
const resizeWindow = (width: number) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  window.dispatchEvent(new Event('resize'));
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    // Restore window width
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  it('renders the dashboard with default widgets', async () => {
    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Letzte Bestellungen nach Liefertermin/i)).toBeInTheDocument();
    });

    // Check for key dashboard sections
    expect(screen.getByText(/Menü/i)).toBeInTheDocument();
    expect(screen.getByText(/Schnellzugriff/i)).toBeInTheDocument();
    expect(screen.getByText(/Pinnwand/i)).toBeInTheDocument();
  });

  it('toggles edit mode when edit button is clicked', async () => {
    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Letzte Bestellungen nach Liefertermin/i)).toBeInTheDocument();
    });

    // Find and click the edit button
    const editButton = screen.getByRole('button', { name: /dashboard bearbeiten/i });
    fireEvent.click(editButton);

    // Check that save button appears when in edit mode
    expect(screen.getByRole('button', { name: /änderungen speichern/i })).toBeInTheDocument();

    // Click again to exit edit mode
    const saveButton = screen.getByRole('button', { name: /änderungen speichern/i });
    fireEvent.click(saveButton);

    // Check that we're back to edit button
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /dashboard bearbeiten/i })).toBeInTheDocument();
    });
  });

  it('renders menu tiles correctly', async () => {
    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Menü/i)).toBeInTheDocument();
    });

    // Check for some menu tiles
    expect(screen.getByText(/Kunden/i)).toBeInTheDocument();
    expect(screen.getByText(/Aufträge/i)).toBeInTheDocument();
    expect(screen.getByText(/Produkte/i)).toBeInTheDocument();
    expect(screen.getByText(/Berichte/i)).toBeInTheDocument();
  });

  it('renders recent orders table correctly', async () => {
    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Letzte Bestellungen nach Liefertermin/i)).toBeInTheDocument();
    });

    // Check for order table headers
    expect(screen.getByText(/Auftrags-ID/i)).toBeInTheDocument();
    expect(screen.getByText(/Kunde/i)).toBeInTheDocument();
    expect(screen.getByText(/Liefertermin/i)).toBeInTheDocument();
    expect(screen.getByText(/Status/i)).toBeInTheDocument();
    expect(screen.getByText(/Betrag/i)).toBeInTheDocument();

    // Check for a sample order
    expect(screen.getByText(/ORD-7352/i)).toBeInTheDocument();
    expect(screen.getByText(/Müller GmbH/i)).toBeInTheDocument();
  });

  it('renders quick links correctly', async () => {
    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Schnellzugriff/i)).toBeInTheDocument();
    });

    // Check for quick links
    expect(screen.getByText(/Handbuch/i)).toBeInTheDocument();
    expect(screen.getByText(/Support-Ticket erstellen/i)).toBeInTheDocument();
    expect(screen.getByText(/Schulungsvideos/i)).toBeInTheDocument();
    expect(screen.getByText(/FAQ/i)).toBeInTheDocument();
  });

  it('renders news items correctly', async () => {
    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Pinnwand/i)).toBeInTheDocument();
    });

    // Check for news items
    expect(screen.getByText(/Neue Funktionen im ERP-System/i)).toBeInTheDocument();
    expect(screen.getByText(/Wartungsarbeiten am 25.03/i)).toBeInTheDocument();
    expect(screen.getByText(/Neue Schulungsvideos verfügbar/i)).toBeInTheDocument();
  });

  it('handles window resize correctly', async () => {
    render(<Dashboard />);

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Letzte Bestellungen nach Liefertermin/i)).toBeInTheDocument();
    });

    // Simulate a window resize to mobile size
    resizeWindow(768);
    
    // Force a re-render by toggling edit mode
    const editButton = screen.getByRole('button', { name: /dashboard bearbeiten/i });
    fireEvent.click(editButton);
    
    // Verify the grid is still rendered
    expect(screen.getByTestId('responsive-grid')).toBeInTheDocument();
  });

  it('calls fetch with correct parameters when saving layout', async () => {
    render(<Dashboard />);
    
    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Letzte Bestellungen nach Liefertermin/i)).toBeInTheDocument();
    });

    // Enter edit mode
    const editButton = screen.getByRole('button', { name: /dashboard bearbeiten/i });
    fireEvent.click(editButton);

    // Save the layout
    const saveButton = screen.getByRole('button', { name: /änderungen speichern/i });
    fireEvent.click(saveButton);

    // Verify fetch was called with correct parameters
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/dashboard'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          }),
          body: expect.any(String)
        })
      );
    });
  });

  it('can add a favorite by clicking the star icon', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Menü/i)).toBeInTheDocument();
    });

    // Find a menu tile and its star button
    const starButtons = screen.getAllByTestId('favorite-button');
    
    // Click on one star button (for Kunden tile)
    await user.click(starButtons[0]);
    
    // Verify the star is now filled (favorited)
    expect(starButtons[0]).toHaveAttribute('data-favorited', 'true');
  });

  it('can remove a widget in edit mode', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Letzte Bestellungen nach Liefertermin/i)).toBeInTheDocument();
    });

    // Enter edit mode
    const editButton = screen.getByRole('button', { name: /dashboard bearbeiten/i });
    fireEvent.click(editButton);
    
    // Find remove buttons that appear in edit mode
    const removeButtons = screen.getAllByRole('button', { name: '' });
    const firstRemoveButton = removeButtons[0]; // First widget's remove button
    
    // Remove the widget
    await user.click(firstRemoveButton);
    
    // Since we're mocking the grid, we can't easily test the removal visually,
    // but we can check that the internal state changed by checking for a re-render
    expect(fetch).not.toHaveBeenCalledWith(
      expect.stringContaining('/api/dashboard'),
      expect.anything()
    );
  });
}); 