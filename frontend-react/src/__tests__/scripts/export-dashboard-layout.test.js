/**
 * Tests for export-dashboard-layout.js using a minimal approach for coverage
 */

describe('Export Dashboard Layout Script', () => {
  // Store original console methods
  const originalConsoleError = console.error;
  const originalConsoleLog = console.log;
  
  beforeEach(() => {
    // Reset modules for clean tests
    jest.resetModules();
    
    // Mock console methods
    console.error = jest.fn();
    console.log = jest.fn();
    
    // Create simple mock structure for the browser environment
    Object.defineProperty(global, 'localStorage', {
      value: {
        getItem: jest.fn()
      },
      writable: true
    });
    
    // Set up minimal document mock
    Object.defineProperty(global, 'document', {
      value: {
        createElement: jest.fn(() => ({
          click: jest.fn(),
          href: '',
          download: ''
        })),
        body: {
          appendChild: jest.fn(),
          removeChild: jest.fn()
        }
      },
      writable: true
    });
    
    // Set up URL mock
    Object.defineProperty(global, 'URL', {
      value: {
        createObjectURL: jest.fn(() => 'mock-url'),
        revokeObjectURL: jest.fn()
      },
      writable: true
    });
    
    // Set up Blob mock
    global.Blob = jest.fn(() => ({}));
    
    // Make setTimeout synchronous
    const realSetTimeout = global.setTimeout;
    global.setTimeout = jest.fn((cb) => cb());
    
    // Store real for cleanup
    global._realSetTimeout = realSetTimeout;
  });
  
  afterEach(() => {
    // Restore console
    console.error = originalConsoleError;
    console.log = originalConsoleLog;
    
    // Restore setTimeout
    global.setTimeout = global._realSetTimeout;
    delete global._realSetTimeout;
  });
  
  test('Should handle missing localStorage data', () => {
    // Setup localStorage to return null
    global.localStorage.getItem.mockReturnValue(null);
    
    // Import and test
    const module = require('../../scripts/export-dashboard-layout');
    
    // Test export
    expect(module.exportDashboardLayout()).toBe(false);
    expect(console.error).toHaveBeenCalledWith('No dashboard layout found in localStorage');
    
    // Test show
    console.error.mockClear();
    expect(module.showDashboardLayout()).toBeUndefined();
    expect(console.error).toHaveBeenCalledWith('No dashboard layout found in localStorage');
  });
  
  test('Should handle invalid JSON data', () => {
    // Setup localStorage to return invalid JSON
    global.localStorage.getItem.mockReturnValue('not valid json');
    
    // Import and test
    const module = require('../../scripts/export-dashboard-layout');
    
    // Test export
    expect(module.exportDashboardLayout()).toBe(false);
    expect(console.error).toHaveBeenCalled();
    expect(console.error.mock.calls[0][0]).toBe('Failed to export dashboard layout:');
    
    // Test show
    console.error.mockClear();
    expect(module.showDashboardLayout()).toBeUndefined();
    expect(console.error).toHaveBeenCalled();
    expect(console.error.mock.calls[0][0]).toBe('Failed to show dashboard layout:');
  });
  
  test('Should handle valid JSON data', () => {
    // Create valid layout data
    const validLayout = { layout: [{ i: 'widget1', x: 0, y: 0, w: 2, h: 2 }] };
    
    // Setup localStorage to return valid JSON
    global.localStorage.getItem.mockReturnValue(JSON.stringify(validLayout));
    
    // Import and test
    const module = require('../../scripts/export-dashboard-layout');
    
    // Test export
    expect(module.exportDashboardLayout()).toBe(true);
    expect(console.log).toHaveBeenCalledWith('Dashboard layout exported successfully!');
    
    // Test show
    console.log.mockClear();
    const result = module.showDashboardLayout();
    expect(result).toEqual(validLayout);
    expect(console.log).toHaveBeenCalledWith('Current dashboard layout:');
  });
  
  test('Should handle browser check for localStorage undefined', () => {
    // Create a non-browser environment
    delete global.localStorage;
    
    // Import and test
    const module = require('../../scripts/export-dashboard-layout');
    
    // Test export with no localStorage
    expect(module.exportDashboardLayout()).toBe(false);
    expect(console.error).toHaveBeenCalledWith('Not in a browser environment');
    
    // Test show with no localStorage
    console.error.mockClear();
    expect(module.showDashboardLayout()).toBeUndefined();
    expect(console.error).toHaveBeenCalledWith('Not in a browser environment');
  });
  
  test('Should handle browser check for document undefined', () => {
    // Create a partial browser environment
    delete global.document;
    
    // Import and test
    const module = require('../../scripts/export-dashboard-layout');
    
    // Test export with no document
    expect(module.exportDashboardLayout()).toBe(false);
    expect(console.error).toHaveBeenCalledWith('Not in a browser environment');
  });
}); 