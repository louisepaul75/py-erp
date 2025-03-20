import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { useIsAuthenticated } from '../../lib/auth/authHooks';
import { LoadingSpinner } from '../ui/LoadingSpinner';

interface AdminRouteProps {
  children: React.ReactNode;
}

export const AdminRoute = ({ children }: AdminRouteProps) => {
  const { isAuthenticated, isLoading, user } = useIsAuthenticated();
  const router = useRouter();
  
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user?.isAdmin)) {
      router.push('/unauthorized');
    }
  }, [isAuthenticated, isLoading, router, user]);
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return isAuthenticated && user?.isAdmin ? <>{children}</> : null;
}; 