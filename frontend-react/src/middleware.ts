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

  // Redirect logic based on auth status
  if (isPublicPath && hasAuthCookie && path === '/login') {
    // If user has auth cookie and tries to access login page, redirect to dashboard
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  if (!isPublicPath && !hasAuthCookie) {
    // Store the original URL to redirect back after login
    const url = new URL('/login', request.url)
    url.searchParams.set('from', request.nextUrl.pathname)
    return NextResponse.redirect(url)
  }

  // Allow the request to proceed
  return NextResponse.next()
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