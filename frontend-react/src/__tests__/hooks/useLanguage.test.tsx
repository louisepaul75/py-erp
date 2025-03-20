import { renderHook, act } from '@testing-library/react';
import { useLanguage } from '@/hooks/useLanguage';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

// Mock navigator
Object.defineProperty(window, 'navigator', {
  value: {
    language: 'en-US',
  },
  writable: true,
});

// Mock document methods
document.documentElement.lang = '';

describe('useLanguage hook', () => {
  beforeAll(() => {
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });
  });

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    document.documentElement.lang = '';
    // Reset navigator language
    Object.defineProperty(window.navigator, 'language', { value: 'en-US' });
  });

  // Helper function to run the effect hooks
  const runEffects = () => {
    // Force effects to run by simulating component mount and unmount
    jest.runAllTimers();
  };

  it('should initialize with English by default', () => {
    jest.useFakeTimers();
    
    const { result } = renderHook(() => useLanguage());
    runEffects();
    
    expect(result.current.language).toBe('en');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('language', 'en');
    expect(document.documentElement.lang).toBe('en');
    
    jest.useRealTimers();
  });

  it('should initialize with saved language from localStorage', () => {
    jest.useFakeTimers();
    localStorageMock.getItem.mockReturnValueOnce('de');
    
    const { result } = renderHook(() => useLanguage());
    runEffects();
    
    expect(result.current.language).toBe('de');
    expect(document.documentElement.lang).toBe('de');
    
    jest.useRealTimers();
  });

  it('should initialize with browser language if available and not in localStorage', () => {
    jest.useFakeTimers();
    Object.defineProperty(window.navigator, 'language', { value: 'fr-FR' });
    
    const { result } = renderHook(() => useLanguage());
    runEffects();
    
    expect(result.current.language).toBe('fr');
    expect(document.documentElement.lang).toBe('fr');
    
    jest.useRealTimers();
  });

  it('should default to English if browser language is not supported', () => {
    jest.useFakeTimers();
    Object.defineProperty(window.navigator, 'language', { value: 'it-IT' });
    
    const { result } = renderHook(() => useLanguage());
    runEffects();
    
    expect(result.current.language).toBe('en');
    expect(document.documentElement.lang).toBe('en');
    
    jest.useRealTimers();
  });

  it('should change language and update localStorage', () => {
    jest.useFakeTimers();
    
    const { result } = renderHook(() => useLanguage());
    
    act(() => {
      result.current.changeLanguage('es');
    });
    
    expect(result.current.language).toBe('es');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('language', 'es');
    expect(document.documentElement.lang).toBe('es');
    
    jest.useRealTimers();
  });
}); 