// --- Define Mocks FIRST ---

const mockUrl = (pathname: string, searchParams = {}) => ({
  pathname: pathname,
  searchParams: new URLSearchParams(searchParams),
  toString: () => `http://localhost:3000${pathname}${searchParams ? '?' + new URLSearchParams(searchParams).toString() : ''}`,
  origin: 'http://localhost:3000',
  protocol: 'http:',
  host: 'localhost:3000',
  hostname: 'localhost',
  port: '3000',
  search: searchParams ? '?' + new URLSearchParams(searchParams).toString() : '',
  hash: '',
  href: `http://localhost:3000${pathname}${searchParams ? '?' + new URLSearchParams(searchParams).toString() : ''}`,
});

class MockCookies {
  private store: Map<string, { name: string; value: string; options?: any }> = new Map();

  constructor(initialCookies: Record<string, string> = {}) {
    Object.entries(initialCookies).forEach(([name, value]) => {
      this.store.set(name, { name, value });
    });
  }

  get(key: string) {
    return this.store.get(key);
  }

  has(key: string): boolean {
    return this.store.has(key);
  }

  set(name: string, value: string, options?: any) {
    this.store.set(name, { name, value, options });
  }

  delete(key: string) {
    this.store.delete(key);
  }
  
  [Symbol.iterator]() {
      return this.store.values();
  }
}

const mockNextRequestImplementation = (pathname: string, initialCookies: Record<string, string> = {}) => {
  const urlObj = mockUrl(pathname);
  return {
    nextUrl: urlObj,
    cookies: new MockCookies(initialCookies),
    url: urlObj.href,
  };
};

const mockNextResponseImplementation = {
  next: jest.fn(() => ({
    cookies: new MockCookies(),
    headers: new Headers(),
    status: 200,
  })),
  redirect: jest.fn((url: URL) => ({
    cookies: new MockCookies(),
    headers: new Headers({'location': url.toString()}),
    status: 307,
  })),
};

// --- Now Mock next/server using a factory function ---

jest.mock('next/server', () => ({
  // Reference the implementations inside the factory
  NextRequest: jest.fn().mockImplementation((...args: any[]) => 
      mockNextRequestImplementation(args[0]?.pathname || '/', args[0]?.cookies?.store ? Object.fromEntries(args[0].cookies.store) : {}) // Adjust based on actual constructor usage if needed
  ),
  NextResponse: mockNextResponseImplementation,
}));

// --- Import middleware AFTER mocks are defined ---
import { middleware } from '../middleware';

// --- Tests ---
describe('Middleware', () => {

  beforeEach(() => {
    // Use the mock object directly for clearing
    mockNextResponseImplementation.next.mockClear();
    mockNextResponseImplementation.redirect.mockClear();
  });
  
  const createMockReq = (pathname: string, cookies: Record<string, string> = {}) => {
      // Use the implementation function to create the mock object
      const req = mockNextRequestImplementation(pathname, cookies); 
      return req as any; // Cast as needed for the middleware function signature
  }

  it('should redirect unauthenticated user from protected route to /login with "from" param', () => {
    const req = createMockReq('/dashboard');
    const res = middleware(req);
    // Assert using the mock object directly
    expect(mockNextResponseImplementation.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(mockNextResponseImplementation.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/login');
    expect(redirectUrl.searchParams.get('from')).toBe('/dashboard');
    const responseCookies = (mockNextResponseImplementation.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('1');
  });

  it('should allow unauthenticated user to access public route /login', () => {
    const req = createMockReq('/login');
    const res = middleware(req);
    expect(mockNextResponseImplementation.next).toHaveBeenCalledTimes(1);
    expect(mockNextResponseImplementation.redirect).not.toHaveBeenCalled();
    const responseCookies = (mockNextResponseImplementation.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });
  
  it('should allow unauthenticated user to access public route /health-status', () => {
    const req = createMockReq('/health-status');
    const res = middleware(req);
    expect(mockNextResponseImplementation.next).toHaveBeenCalledTimes(1);
    expect(mockNextResponseImplementation.redirect).not.toHaveBeenCalled();
    const responseCookies = (mockNextResponseImplementation.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });

  it('should allow authenticated user to access protected route', () => {
    const req = createMockReq('/dashboard', { access_token: 'dummy-token' });
    const res = middleware(req);
    expect(mockNextResponseImplementation.next).toHaveBeenCalledTimes(1);
    expect(mockNextResponseImplementation.redirect).not.toHaveBeenCalled();
    const responseCookies = (mockNextResponseImplementation.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });

  it('should redirect authenticated user from /login to /dashboard', () => {
    const req = createMockReq('/login', { access_token: 'dummy-token' });
    const res = middleware(req);
    expect(mockNextResponseImplementation.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(mockNextResponseImplementation.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/dashboard');
    expect(redirectUrl.searchParams.has('from')).toBe(false);
    const responseCookies = (mockNextResponseImplementation.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('1');
  });

  it('should detect redirect loop and clear cookies, redirecting to /login', () => {
    const req = createMockReq('/some-protected-path', { redirect_count: '6' }); 
    const res = middleware(req);
    expect(mockNextResponseImplementation.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(mockNextResponseImplementation.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/login');
    const responseCookies = (mockNextResponseImplementation.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.has('access_token')).toBe(false);
    expect(responseCookies.has('refresh_token')).toBe(false);
    expect(responseCookies.has('redirect_count')).toBe(false);
  });
  
  it('should increment redirect_count on redirects', () => {
    const req = createMockReq('/dashboard', { redirect_count: '2' }); 
    const res = middleware(req);
    expect(mockNextResponseImplementation.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(mockNextResponseImplementation.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/login');
    const responseCookies = (mockNextResponseImplementation.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('3');
  });

  it('should reset redirect_count on allowed navigation', () => {
    const req = createMockReq('/dashboard', { access_token: 'dummy-token', redirect_count: '3' });
    const res = middleware(req);
    expect(mockNextResponseImplementation.next).toHaveBeenCalledTimes(1);
    const responseCookies = (mockNextResponseImplementation.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });
}); 