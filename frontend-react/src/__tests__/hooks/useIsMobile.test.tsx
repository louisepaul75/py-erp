import { renderHook, act } from '@testing-library/react';
import { useIsMobile } from '@/hooks/use-mobile';

describe('useIsMobile hook', () => {
  const originalInnerWidth = window.innerWidth;
  let resizeEventListeners: Array<() => void> = [];

  // Mock window properties and event listeners
  beforeAll(() => {
    // Mock window.innerWidth
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      value: originalInnerWidth,
    });

    // Mock addEventListener
    window.addEventListener = jest.fn((event, cb) => {
      if (event === 'resize') {
        resizeEventListeners.push(cb as () => void);
      }
    });

    // Mock removeEventListener
    window.removeEventListener = jest.fn((event, cb) => {
      if (event === 'resize') {
        resizeEventListeners = resizeEventListeners.filter(listener => listener !== cb);
      }
    });
  });

  // Reset window.innerWidth and clear event listeners after each test
  afterEach(() => {
    window.innerWidth = originalInnerWidth;
    resizeEventListeners = [];
  });

  it('should return false for desktop screen width', () => {
    window.innerWidth = 1024;
    
    const { result } = renderHook(() => useIsMobile());
    
    expect(result.current).toBe(false);
  });

  it('should return true for mobile screen width', () => {
    window.innerWidth = 480;
    
    const { result } = renderHook(() => useIsMobile());
    
    expect(result.current).toBe(true);
  });

  it('should update state when window is resized', () => {
    // Start with desktop size
    window.innerWidth = 1024;
    
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
    
    // Simulate resize to mobile size
    act(() => {
      window.innerWidth = 480;
      // Trigger all resize event listeners
      resizeEventListeners.forEach(listener => listener());
    });
    
    expect(result.current).toBe(true);
    
    // Simulate resize back to desktop size
    act(() => {
      window.innerWidth = 1024;
      // Trigger all resize event listeners
      resizeEventListeners.forEach(listener => listener());
    });
    
    expect(result.current).toBe(false);
  });

  it('should add resize event listener on mount', () => {
    renderHook(() => useIsMobile());
    
    expect(window.addEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
  });

  it('should remove resize event listener on unmount', () => {
    const { unmount } = renderHook(() => useIsMobile());
    
    unmount();
    
    expect(window.removeEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
  });
}); 