import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// This function can be marked `async` if using `await` inside
export function middleware(request: NextRequest) {
  // Get the pathname of the request
  const path = request.nextUrl.pathname

  // Define public paths that don't require authentication
  const isPublicPath = 
    path === '/login' || 
    path === '/health-status' ||
    path === '/api/csrf/' ||  // Allow CSRF token endpoint
    path === '/api/token/' ||  // Allow token endpoint
    path === '/api/token/refresh/' ||  // Allow token refresh endpoint
    path.startsWith('/images/') ||
    path.startsWith('/fonts/') ||
    path.startsWith('/assets/') ||
    path.startsWith('/locales/') ||  // Allow translations
    path.startsWith('/_next/') ||  // Allow Next.js assets
    path.startsWith('/favicon')  // Allow favicon
  
  // Check for authentication cookie
  const hasAuthCookie = request.cookies.has('access_token')
  
  // Check if this is a loop by counting redirects in the cookie
  const redirectCount = parseInt(request.cookies.get('redirect_count')?.value || '0')
  
  // If we've redirected too many times, break the loop and clear cookies
  if (redirectCount > 5) {
    const response = NextResponse.redirect(new URL('/login', request.url))
    response.cookies.delete('access_token')
    response.cookies.delete('refresh_token')
    response.cookies.delete('redirect_count')
    return response
  }

  // Redirect logic based on auth status
  if (isPublicPath && hasAuthCookie && path === '/login') {
    // If user has auth cookie and tries to access login page, redirect to dashboard
    const response = NextResponse.redirect(new URL('/dashboard', request.url))
    response.cookies.set('redirect_count', String(redirectCount + 1))
    return response
  }

  if (!isPublicPath && !hasAuthCookie) {
    // Store the original URL to redirect back after login
    const url = new URL('/login', request.url)
    url.searchParams.set('from', request.nextUrl.pathname)
    const response = NextResponse.redirect(url)
    response.cookies.set('redirect_count', String(redirectCount + 1))
    return response
  }
  
  // Reset redirect count for normal navigation
  const response = NextResponse.next()
  response.cookies.set('redirect_count', '0')
  return response
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
} 