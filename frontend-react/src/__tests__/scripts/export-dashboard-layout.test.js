/**
 * Tests for export-dashboard-layout.js using a minimal approach for coverage
 */

// Mock fs module
const mockFs = {
  writeFileSync: jest.fn(),
  readFileSync: jest.fn(),
  existsSync: jest.fn(),
};

jest.mock('fs', () => mockFs);

// Mock path module
const mockPath = {
  join: jest.fn(),
  resolve: jest.fn(),
};

jest.mock('path', () => mockPath);

describe('Dashboard Layout Export Script', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Reset module registry before each test
    jest.resetModules();
    
    // Setup default mock implementations
    mockFs.writeFileSync.mockImplementation(() => {});
    mockFs.readFileSync.mockImplementation(() => '{}');
    mockFs.existsSync.mockImplementation(() => true);
    mockPath.join.mockImplementation((...args) => args.join('/'));
    mockPath.resolve.mockImplementation((...args) => args.join('/'));

    // Mock browser APIs
    global.localStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
    };
    global.document = {
      createElement: jest.fn(() => ({
        click: jest.fn(),
        href: '',
        download: '',
      })),
      body: {
        appendChild: jest.fn(),
        removeChild: jest.fn(),
      },
    };
    global.URL = {
      createObjectURL: jest.fn(),
      revokeObjectURL: jest.fn(),
    };
    global.Blob = jest.fn();
  });

  it('exports dashboard layout correctly', async () => {
    const mockLayout = {
      lg: [
        { i: 'widget1', x: 0, y: 0, w: 2, h: 2 },
        { i: 'widget2', x: 2, y: 0, w: 2, h: 2 },
      ],
    };

    // Import the script after setting up mocks
    const { exportDashboardLayout } = await import('../../scripts/export-dashboard-layout');
    
    const result = await exportDashboardLayout(mockLayout);
    expect(result).toEqual(mockLayout);
    expect(mockFs.writeFileSync).toHaveBeenCalled();
    expect(mockFs.writeFileSync.mock.calls[0][1]).toContain('widget1');
  });

  it('handles empty layout', async () => {
    const mockLayout = {};

    // Import the script after setting up mocks
    const { exportDashboardLayout } = await import('../../scripts/export-dashboard-layout');
    
    const result = await exportDashboardLayout(mockLayout);
    expect(result).toEqual(mockLayout);
    expect(mockFs.writeFileSync).toHaveBeenCalled();
    expect(mockFs.writeFileSync.mock.calls[0][1]).toBe('{}');
  });

  it('handles invalid layout gracefully', async () => {
    const mockLayout = null;

    // Import the script after setting up mocks
    const { exportDashboardLayout } = await import('../../scripts/export-dashboard-layout');
    
    await expect(exportDashboardLayout(mockLayout)).rejects.toThrow('Invalid layout format');
  });

  it('handles filesystem errors', async () => {
    const mockLayout = {
      lg: [{ i: 'widget1', x: 0, y: 0, w: 2, h: 2 }],
    };

    mockFs.writeFileSync.mockImplementation(() => {
      throw new Error('Write error');
    });

    // Import the script after setting up mocks
    const { exportDashboardLayout } = await import('../../scripts/export-dashboard-layout');
    
    await expect(exportDashboardLayout(mockLayout)).rejects.toThrow('Write error');
  });

  it('validates layout format', async () => {
    const mockLayout = {
      lg: 'invalid',
    };

    // Import the script after setting up mocks
    const { exportDashboardLayout } = await import('../../scripts/export-dashboard-layout');
    
    await expect(exportDashboardLayout(mockLayout)).rejects.toThrow('Invalid layout format');
  });
}); 