import { renderHook, act } from '@testing-library/react';
import { useTheme } from '@/hooks/useTheme';

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

// Mock matchMedia
const mockMatchMedia = jest.fn().mockImplementation((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: jest.fn(),
  removeListener: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
}));

// Mock document methods
const classListMock = {
  add: jest.fn(),
  remove: jest.fn(),
};

describe('useTheme hook', () => {
  beforeAll(() => {
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });
    Object.defineProperty(window, 'matchMedia', { value: mockMatchMedia });
    
    // Mock classList using spyOn
    jest.spyOn(document.documentElement.classList, 'add').mockImplementation(classListMock.add);
    jest.spyOn(document.documentElement.classList, 'remove').mockImplementation(classListMock.remove);
  });

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
  });

  it('should initialize with light theme when no preferences are set', () => {
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('light');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
    expect(classListMock.remove).toHaveBeenCalledWith('dark');
  });

  it('should initialize with saved theme from localStorage', () => {
    localStorageMock.getItem.mockReturnValueOnce('dark');
    
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('dark');
    expect(classListMock.add).toHaveBeenCalledWith('dark');
  });

  it('should toggle theme from light to dark', () => {
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('light');
    
    act(() => {
      result.current.toggleTheme();
    });
    
    expect(result.current.theme).toBe('dark');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
    expect(classListMock.add).toHaveBeenCalledWith('dark');
  });

  it('should toggle theme from dark to light', () => {
    localStorageMock.getItem.mockReturnValueOnce('dark');
    
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('dark');
    
    act(() => {
      result.current.toggleTheme();
    });
    
    expect(result.current.theme).toBe('light');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
    expect(classListMock.remove).toHaveBeenCalledWith('dark');
  });

  it('should use system preference when no localStorage value is present', () => {
    // Mock system preference to dark
    mockMatchMedia.mockImplementationOnce((query) => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));
    
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('dark');
    expect(classListMock.add).toHaveBeenCalledWith('dark');
  });
}); 