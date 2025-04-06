import { NextRequest, NextResponse } from 'next/server';
import { MiddlewareConfig } from 'next/dist/build/analysis/get-page-static-info';

// --- Define Mock Implementations First (for clarity) ---
class MockCookies {
  private store: Map<string, { name: string; value: string; options?: any }> = new Map();

  constructor(initialCookies: Record<string, string> = {}) {
    for (const [name, value] of Object.entries(initialCookies)) {
      this.store.set(name, { name, value });
    }
  }
  get(key: string) { return this.store.get(key); }
  has(key: string): boolean { return this.store.has(key); }
  set(name: string, value: string, options?: any) { this.store.set(name, { name, value, options }); }
  delete(key: string) { this.store.delete(key); }
}

// --- Now Mock next/server using a factory function with INLINE mock definitions ---
jest.mock('next/server', () => ({
  NextRequest: jest.fn().mockImplementation((input: Request | string, init?: RequestInit) => {
    // Basic mock implementation - adapt as needed for your middleware tests
    const url = typeof input === 'string' ? new URL(input) : new URL(input.url);
    const cookies = new MockCookies(init?.headers?.cookie ? 
        Object.fromEntries(init.headers.cookie.split('; ').map(c => c.split('='))) 
        : {}
    );
    return {
      nextUrl: url,
      cookies: cookies,
      headers: new Headers(init?.headers),
      url: url.toString(),
      // Add other necessary properties/methods used by your middleware
    };
  }),
  NextResponse: {
    next: jest.fn(() => ({
      cookies: new MockCookies(),
      headers: new Headers(),
      status: 200,
    })),
    redirect: jest.fn((url: URL | string) => ({
      cookies: new MockCookies(),
      headers: new Headers({ 'location': url.toString() }),
      status: 307,
    })),
    // Mock other static methods if used (e.g., .json())
  },
}));

// --- Import middleware AFTER mocks are defined ---
import { middleware, config } from '../middleware';

// --- Tests ---
describe('Middleware', () => {

  // Reference the mock functions *after* jest.mock has run
  const MockNextResponse = require('next/server').NextResponse;

  beforeEach(() => {
    // Clear mocks using the reference obtained after jest.mock
    MockNextResponse.next.mockClear();
    MockNextResponse.redirect.mockClear();
  });

  const createMockReq = (pathname: string, cookies: Record<string, string> = {}) => {
    // Construct a simple request object for the mock
    const cookieString = Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ');
    const mockedRequest = new NextRequest(`http://localhost${pathname}`, {
        headers: cookieString ? { cookie: cookieString } : {},
    });
    return mockedRequest as any; 
  }

  it('should redirect unauthenticated user from protected route to /login with "from" param', () => {
    const req = createMockReq('/dashboard');
    const res = middleware(req);
    expect(MockNextResponse.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(MockNextResponse.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/login');
    expect(redirectUrl.searchParams.get('from')).toBe('/dashboard');
    const responseCookies = (MockNextResponse.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('1');
  });

  it('should allow unauthenticated user to access public route /login', () => {
    const req = createMockReq('/login');
    const res = middleware(req);
    expect(MockNextResponse.next).toHaveBeenCalledTimes(1);
    expect(MockNextResponse.redirect).not.toHaveBeenCalled();
    const responseCookies = (MockNextResponse.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });
  
  it('should allow unauthenticated user to access public route /health-status', () => {
    const req = createMockReq('/health-status');
    const res = middleware(req);
    expect(MockNextResponse.next).toHaveBeenCalledTimes(1);
    expect(MockNextResponse.redirect).not.toHaveBeenCalled();
    const responseCookies = (MockNextResponse.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });

  it('should allow authenticated user to access protected route', () => {
    const req = createMockReq('/dashboard', { access_token: 'dummy-token' });
    const res = middleware(req);
    expect(MockNextResponse.next).toHaveBeenCalledTimes(1);
    expect(MockNextResponse.redirect).not.toHaveBeenCalled();
    const responseCookies = (MockNextResponse.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });

  it('should redirect authenticated user from /login to /dashboard', () => {
    const req = createMockReq('/login', { access_token: 'dummy-token' });
    const res = middleware(req);
    expect(MockNextResponse.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(MockNextResponse.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/dashboard');
    expect(redirectUrl.searchParams.has('from')).toBe(false);
    const responseCookies = (MockNextResponse.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('1');
  });

  it('should detect redirect loop and clear cookies, redirecting to /login', () => {
    const req = createMockReq('/some-protected-path', { redirect_count: '6' }); 
    const res = middleware(req);
    expect(MockNextResponse.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(MockNextResponse.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/login');
    const responseCookies = (MockNextResponse.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.has('access_token')).toBe(false);
    expect(responseCookies.has('refresh_token')).toBe(false);
    expect(responseCookies.has('redirect_count')).toBe(false);
  });
  
  it('should increment redirect_count on redirects', () => {
    const req = createMockReq('/dashboard', { redirect_count: '2' }); 
    const res = middleware(req);
    expect(MockNextResponse.redirect).toHaveBeenCalledTimes(1);
    const redirectUrl = new URL(MockNextResponse.redirect.mock.calls[0][0]);
    expect(redirectUrl.pathname).toBe('/login');
    const responseCookies = (MockNextResponse.redirect.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('3');
  });

  it('should reset redirect_count on allowed navigation', () => {
    const req = createMockReq('/dashboard', { access_token: 'dummy-token', redirect_count: '3' });
    const res = middleware(req);
    expect(MockNextResponse.next).toHaveBeenCalledTimes(1);
    const responseCookies = (MockNextResponse.next.mock.results[0].value as any).cookies;
    expect(responseCookies.get('redirect_count')?.value).toBe('0');
  });
}); 