'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth/authService';
import { Suspense } from 'react';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

export default function Home() {
  const router = useRouter();

  // Prefetch auth state on initial page load
  useEffect(() => {
    // Immediately try to get user authentication state
    const initializeAuth = async () => {
      try {
        const user = await authService.getCurrentUser();
        // If authenticated, redirect to dashboard
        if (user) {
          router.push('/dashboard');
        } else {
          // Otherwise redirect to login
          router.push('/login');
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        // On error, redirect to login
        router.push('/login');
      }
    };

    initializeAuth();
  }, [router]);

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    </Suspense>
  );
} 