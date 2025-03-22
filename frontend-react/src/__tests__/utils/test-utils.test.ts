/**
 * Tests for test-utils.ts
 */

import {
  mockMatchMedia,
  mockIntersectionObserver,
  mockResizeObserver,
  setupBrowserMocks
} from '../../utils/test-utils';

describe('Test Utilities', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    window.matchMedia = undefined as any;
    window.IntersectionObserver = undefined as any;
    window.ResizeObserver = undefined as any;
  });

  test('mockMatchMedia should mock window.matchMedia correctly', () => {
    mockMatchMedia();
    
    // Verify that matchMedia is defined
    expect(window.matchMedia).toBeDefined();
    
    // Call the mocked function
    const result = window.matchMedia('(min-width: 768px)');
    
    // Verify mock implementation
    expect(result).toEqual({
      matches: false,
      media: '(min-width: 768px)',
      onchange: null,
      addListener: expect.any(Function),
      removeListener: expect.any(Function),
      addEventListener: expect.any(Function),
      removeEventListener: expect.any(Function),
      dispatchEvent: expect.any(Function),
    });
    
    // Test that the functions are callable
    expect(() => result.addListener(jest.fn())).not.toThrow();
    expect(() => result.removeListener(jest.fn())).not.toThrow();
    expect(() => result.addEventListener('change', jest.fn())).not.toThrow();
    expect(() => result.removeEventListener('change', jest.fn())).not.toThrow();
    expect(() => result.dispatchEvent(new Event('change'))).not.toThrow();
  });

  test('mockIntersectionObserver should mock IntersectionObserver correctly', () => {
    mockIntersectionObserver();
    
    // Verify that IntersectionObserver is defined
    expect(window.IntersectionObserver).toBeDefined();
    
    // Create a mock callback
    const callback = jest.fn();
    
    // Create a new instance with the mock
    const observer = new window.IntersectionObserver(callback);
    
    // Verify that the observer instance has the expected methods
    expect(observer).toEqual({
      observe: expect.any(Function),
      unobserve: expect.any(Function),
      disconnect: expect.any(Function),
    });
    
    // Test that the functions are callable
    const element = document.createElement('div');
    expect(() => observer.observe(element)).not.toThrow();
    expect(() => observer.unobserve(element)).not.toThrow();
    expect(() => observer.disconnect()).not.toThrow();
  });

  test('mockResizeObserver should mock ResizeObserver correctly', () => {
    mockResizeObserver();
    
    // Verify that ResizeObserver is defined
    expect(window.ResizeObserver).toBeDefined();
    
    // Create a new instance with the mock
    const observer = new window.ResizeObserver(jest.fn());
    
    // Verify that the observer instance has the expected methods
    expect(observer).toEqual({
      observe: expect.any(Function),
      unobserve: expect.any(Function),
      disconnect: expect.any(Function),
    });
    
    // Test that the functions are callable
    const element = document.createElement('div');
    expect(() => observer.observe(element)).not.toThrow();
    expect(() => observer.unobserve(element)).not.toThrow();
    expect(() => observer.disconnect()).not.toThrow();
  });

  test('setupBrowserMocks should setup all browser mocks', () => {
    // Spy on the individual mock functions
    const matchMediaSpy = jest.spyOn({ mockMatchMedia }, 'mockMatchMedia');
    const intersectionObserverSpy = jest.spyOn({ mockIntersectionObserver }, 'mockIntersectionObserver');
    const resizeObserverSpy = jest.spyOn({ mockResizeObserver }, 'mockResizeObserver');
    
    // Override the functions with spies
    (matchMediaSpy as any).mockImplementation(mockMatchMedia);
    (intersectionObserverSpy as any).mockImplementation(mockIntersectionObserver);
    (resizeObserverSpy as any).mockImplementation(mockResizeObserver);
    
    // Call the setup function
    setupBrowserMocks();
    
    // Verify that all mock functions were called
    expect(matchMediaSpy).toHaveBeenCalled();
    expect(intersectionObserverSpy).toHaveBeenCalled();
    expect(resizeObserverSpy).toHaveBeenCalled();
    
    // Verify that the mocks are defined
    expect(window.matchMedia).toBeDefined();
    expect(window.IntersectionObserver).toBeDefined();
    expect(window.ResizeObserver).toBeDefined();
    
    // Clean up spies
    matchMediaSpy.mockRestore();
    intersectionObserverSpy.mockRestore();
    resizeObserverSpy.mockRestore();
  });
}); 