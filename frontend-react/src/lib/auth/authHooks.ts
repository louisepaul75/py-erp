import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { authService } from './authService';
import { User, LoginCredentials } from './authTypes';

// Hook for the current user
export const useUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: authService.getCurrentUser,
    retry: false,
    staleTime: Infinity,
  });
};

// Hook for login
export const useLogin = () => {
  const queryClient = useQueryClient();
  const router = useRouter();
  
  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials),
    onSuccess: (user: User) => {
      queryClient.setQueryData(['user'], user);
      // Redirect to dashboard after login
      router.push('/dashboard');
    },
  });
};

// Hook for logout
export const useLogout = () => {
  let queryClient;
  let router;
  
  try {
    queryClient = useQueryClient();
    router = useRouter();
  } catch (error) {
    // Fallback for when QueryClient is not available
    console.warn('QueryClient not available, using fallback logout behavior');
    
    return {
      mutate: () => {
        authService.logout();
        window.location.href = '/login';
      },
      isPending: false,
      isError: false,
      error: null,
      isSuccess: false,
      reset: () => {}
    };
  }
  
  return useMutation({
    mutationFn: () => {
      authService.logout();
      return Promise.resolve();
    },
    onSuccess: () => {
      if (queryClient) {
        queryClient.setQueryData(['user'], null);
        queryClient.invalidateQueries();
      }
      if (router) {
        router.push('/login');
      } else {
        window.location.href = '/login';
      }
    },
  });
};

// Hook for profile update
export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userData: Partial<User>) => authService.updateProfile(userData),
    onSuccess: (updatedUser: User) => {
      queryClient.setQueryData(['user'], updatedUser);
    },
  });
};

// Hook for password change
export const useChangePassword = () => {
  return useMutation({
    mutationFn: ({ oldPassword, newPassword }: { oldPassword: string; newPassword: string }) =>
      authService.changePassword(oldPassword, newPassword),
  });
};

// Hook to check if user is authenticated
export const useIsAuthenticated = () => {
  const { data: user, isLoading } = useUser();
  return {
    isAuthenticated: !!user,
    isLoading,
    user,
  };
}; 