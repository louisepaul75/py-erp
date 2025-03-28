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
  const queryClient = useQueryClient();
  const router = useRouter();
  
  const mutation = useMutation({
    mutationFn: () => {
      authService.logout();
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.setQueryData(['user'], null);
      queryClient.invalidateQueries();
      router.push('/login');
    },
  });

  // Provide a fallback method that can be used outside React components
  const fallbackLogout = () => {
    authService.logout();
    window.location.href = '/login';
  };

  return {
    ...mutation,
    fallbackLogout
  };
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