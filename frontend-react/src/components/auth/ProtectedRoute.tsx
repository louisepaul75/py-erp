'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';
import { useIsAuthenticated } from '../../lib/auth/authHooks';
import { LoadingSpinner } from '../ui/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useIsAuthenticated();
  const router = useRouter();
  const pathname = usePathname();
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated && pathname) {
      const redirectUrl = `/login?from=${encodeURIComponent(pathname)}`;
      router.push(redirectUrl);
    }
  }, [isAuthenticated, isLoading, router, pathname]);
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return isAuthenticated ? <>{children}</> : null;
}; 