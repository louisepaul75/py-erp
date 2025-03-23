import { renderHook, act } from '@testing-library/react';
import { useScreenSize, getResponsiveClasses, breakpoints } from '@/utils/responsive';

// Mock window resize events
const resizeWindow = (width: number, height: number) => {
  window.innerWidth = width;
  window.innerHeight = height;
  window.dispatchEvent(new Event('resize'));
};

describe('Responsive Utilities', () => {
  describe('useScreenSize', () => {
    beforeEach(() => {
      // Default to desktop size
      resizeWindow(1200, 800);
    });

    it('should return correct screen dimensions', () => {
      const { result } = renderHook(() => useScreenSize());
      
      expect(result.current.width).toBe(1200);
      expect(result.current.height).toBe(800);
    });

    it('should detect mobile screens correctly', () => {
      const { result } = renderHook(() => useScreenSize());
      
      // Start with desktop size
      expect(result.current.isMobile).toBe(false);
      
      // Resize to mobile
      act(() => {
        resizeWindow(600, 800);
      });
      
      expect(result.current.isMobile).toBe(true);
      expect(result.current.isTablet).toBe(false);
      expect(result.current.isDesktop).toBe(false);
    });

    it('should detect tablet screens correctly', () => {
      const { result } = renderHook(() => useScreenSize());
      
      // Start with desktop size
      expect(result.current.isTablet).toBe(false);
      
      // Resize to tablet
      act(() => {
        resizeWindow(800, 800);
      });
      
      expect(result.current.isMobile).toBe(false);
      expect(result.current.isTablet).toBe(true);
      expect(result.current.isDesktop).toBe(false);
    });

    it('should detect desktop screens correctly', () => {
      const { result } = renderHook(() => useScreenSize());
      
      // Ensure we start with desktop
      act(() => {
        resizeWindow(1200, 800);
      });
      
      expect(result.current.isMobile).toBe(false);
      expect(result.current.isTablet).toBe(false);
      expect(result.current.isDesktop).toBe(true);
    });
  });

  describe('getResponsiveClasses', () => {
    it('should combine default classes with responsive variants', () => {
      const defaultClasses = 'text-base font-medium';
      const responsiveClasses = {
        'sm': 'text-sm',
        'md': 'text-md',
        'lg': 'text-lg'
      };
      
      const result = getResponsiveClasses(defaultClasses, responsiveClasses);
      
      expect(result).toBe('text-base font-medium sm:text-sm md:text-md lg:text-lg');
    });

    it('should work with empty responsive classes', () => {
      const defaultClasses = 'text-base font-medium';
      const responsiveClasses = {};
      
      const result = getResponsiveClasses(defaultClasses, responsiveClasses);
      
      expect(result).toBe('text-base font-medium');
    });
  });

  describe('breakpoints', () => {
    it('should have the correct breakpoint values', () => {
      expect(breakpoints.sm).toBe(640);
      expect(breakpoints.md).toBe(768);
      expect(breakpoints.lg).toBe(1024);
      expect(breakpoints.xl).toBe(1280);
      expect(breakpoints['2xl']).toBe(1536);
    });
  });
}); 