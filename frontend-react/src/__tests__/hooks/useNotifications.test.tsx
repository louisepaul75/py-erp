import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useNotifications } from '@/hooks/useNotifications';
import { instance as apiClient } from '@/lib/api';

// Mock the toast hook
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

// Mock the API client
jest.mock('@/lib/api', () => ({
  instance: {
    get: jest.fn(),
    patch: jest.fn(),
    post: jest.fn(),
  },
}));

// Create a wrapper component with QueryClientProvider
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        // Disable caching for tests
        cacheTime: 0,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

// Mock notification data
const mockNotifications = [
  {
    id: '1',
    username: 'john.doe',
    title: 'Test Notification',
    content: 'This is a test notification',
    type: 'system',
    is_read: false,
    created_at: '2023-01-01T12:00:00Z',
    updated_at: '2023-01-01T12:00:00Z',
  },
  {
    id: '2',
    username: 'john.doe',
    title: 'Read Notification',
    content: 'This notification is already read',
    type: 'system',
    is_read: true,
    created_at: '2023-01-01T10:00:00Z',
    updated_at: '2023-01-01T10:00:00Z',
  },
];

describe('useNotifications hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should make API calls to fetch notifications and unread count', async () => {
    // Mock implementation for the API calls
    (apiClient.get as jest.Mock).mockImplementation(() => ({
      json: () => Promise.resolve({})
    }));

    // Render the hook
    renderHook(() => useNotifications(), {
      wrapper: createWrapper(),
    });

    // Wait for the API calls to be made
    await waitFor(() => {
      return expect(apiClient.get).toHaveBeenCalled();
    });

    // Verify API endpoints were called
    expect(apiClient.get).toHaveBeenCalledWith('v1/notifications/');
    expect(apiClient.get).toHaveBeenCalledWith('v1/notifications/unread_count/');
  });

  it('should mark a notification as read', async () => {
    // Mock implementation for the API calls
    (apiClient.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('unread_count')) {
        return {
          json: () => Promise.resolve({ unread_count: 1 })
        };
      }
      return {
        json: () => Promise.resolve({
          count: 2,
          next: null,
          previous: null,
          results: mockNotifications
        })
      };
    });

    // Mock patch implementation
    (apiClient.patch as jest.Mock).mockImplementation(() => ({
      json: () => Promise.resolve({
        ...mockNotifications[0],
        is_read: true,
      })
    }));

    const { result } = renderHook(() => useNotifications(), {
      wrapper: createWrapper(),
    });

    // Wait for initial fetch
    await waitFor(() => !result.current.isLoading);

    // Act: mark notification as read
    act(() => {
      result.current.markAsRead('1');
    });

    // Wait for the mark as read mutation to complete
    await waitFor(() => !result.current.markAsReadPending);

    // Verify API call
    expect(apiClient.patch).toHaveBeenCalledWith('v1/notifications/1/mark_as_read/');
  });

  it('should mark all notifications as read', async () => {
    // Mock implementation for the API calls
    (apiClient.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('unread_count')) {
        return {
          json: () => Promise.resolve({ unread_count: 1 })
        };
      }
      return {
        json: () => Promise.resolve({
          count: 2,
          next: null,
          previous: null,
          results: mockNotifications
        })
      };
    });

    // Mock patch implementation
    (apiClient.patch as jest.Mock).mockImplementation(() => ({
      json: () => Promise.resolve({
        message: '1 notifications marked as read.',
      })
    }));

    const { result } = renderHook(() => useNotifications(), {
      wrapper: createWrapper(),
    });

    // Wait for initial fetch
    await waitFor(() => !result.current.isLoading);

    // Act: mark all notifications as read
    act(() => {
      result.current.markAllAsRead();
    });

    // Wait for the mark all as read mutation to complete
    await waitFor(() => !result.current.markAllAsReadPending);

    // Verify API call
    expect(apiClient.patch).toHaveBeenCalledWith('v1/notifications/mark_all_as_read/');
  });

  it('should send a broadcast message', async () => {
    // Mock implementation for the API calls
    (apiClient.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('unread_count')) {
        return {
          json: () => Promise.resolve({ unread_count: 1 })
        };
      }
      return {
        json: () => Promise.resolve({
          count: 2,
          next: null,
          previous: null,
          results: mockNotifications
        })
      };
    });

    // Mock post implementation
    (apiClient.post as jest.Mock).mockImplementation(() => ({
      json: () => Promise.resolve({
        message: 'Broadcast message sent to 10 users.',
        recipients_count: 10,
      })
    }));

    const { result } = renderHook(() => useNotifications(), {
      wrapper: createWrapper(),
    });

    // Wait for initial fetch
    await waitFor(() => !result.current.isLoading);

    // Act: send broadcast message
    act(() => {
      result.current.sendBroadcast({
        title: 'Broadcast Test',
        content: 'Test broadcast message',
      });
    });

    // Wait for the send broadcast mutation to complete
    await waitFor(() => !result.current.sendBroadcastPending);

    // Verify API call
    expect(apiClient.post).toHaveBeenCalledWith(
      'v1/notifications/send_broadcast/',
      { json: { title: 'Broadcast Test', content: 'Test broadcast message' } }
    );
  });

  it('should send a group message', async () => {
    // Mock implementation for the API calls
    (apiClient.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('unread_count')) {
        return {
          json: () => Promise.resolve({ unread_count: 1 })
        };
      }
      return {
        json: () => Promise.resolve({
          count: 2,
          next: null,
          previous: null,
          results: mockNotifications
        })
      };
    });
    
    // Mock post implementation
    (apiClient.post as jest.Mock).mockImplementation(() => ({
      json: () => Promise.resolve({
        message: 'Message sent to 5 users in group "Admins".',
        recipients_count: 5,
      })
    }));

    const { result } = renderHook(() => useNotifications(), {
      wrapper: createWrapper(),
    });

    // Wait for initial fetch
    await waitFor(() => !result.current.isLoading);

    // Act: send group message
    act(() => {
      result.current.sendGroupMessage({
        title: 'Group Test',
        content: 'Test group message',
        groupId: '1',
      });
    });

    // Wait for the send group message mutation to complete
    await waitFor(() => !result.current.sendGroupMessagePending);

    // Verify API call
    expect(apiClient.post).toHaveBeenCalledWith(
      'v1/notifications/send_group/',
      { json: { title: 'Group Test', content: 'Test group message', group_id: '1' } }
    );
  });

  it('should send a user message', async () => {
    // Mock implementation for the API calls
    (apiClient.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('unread_count')) {
        return {
          json: () => Promise.resolve({ unread_count: 1 })
        };
      }
      return {
        json: () => Promise.resolve({
          count: 2,
          next: null,
          previous: null,
          results: mockNotifications
        })
      };
    });
    
    // Mock post implementation
    (apiClient.post as jest.Mock).mockImplementation(() => ({
      json: () => Promise.resolve({
        message: 'Message sent to John Doe.',
        recipients_count: 1,
      })
    }));

    const { result } = renderHook(() => useNotifications(), {
      wrapper: createWrapper(),
    });

    // Wait for initial fetch
    await waitFor(() => !result.current.isLoading);

    // Act: send user message
    act(() => {
      result.current.sendUserMessage({
        title: 'User Test',
        content: 'Test user message',
        userId: 'user123',
      });
    });

    // Wait for the send user message mutation to complete
    await waitFor(() => !result.current.sendUserMessagePending);

    // Verify API call
    expect(apiClient.post).toHaveBeenCalledWith(
      'v1/notifications/send_user/',
      { json: { title: 'User Test', content: 'Test user message', user_id: 'user123' } }
    );
  });

  it('should handle sendMessage utility function', async () => {
    // Mock implementation for the API calls
    (apiClient.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('unread_count')) {
        return {
          json: () => Promise.resolve({ unread_count: 1 })
        };
      }
      return {
        json: () => Promise.resolve({
          count: 2,
          next: null,
          previous: null,
          results: mockNotifications
        })
      };
    });
    
    // Mock post implementation
    (apiClient.post as jest.Mock).mockImplementation(() => ({
      json: () => Promise.resolve({
        message: 'Message sent to 5 users in group "Admins".',
        recipients_count: 5,
      })
    }));

    const { result } = renderHook(() => useNotifications(), {
      wrapper: createWrapper(),
    });

    // Wait for initial fetch
    await waitFor(() => !result.current.isLoading);

    // Act: use sendMessage utility with 'group' type
    act(() => {
      result.current.sendMessage(
        'Group Message',
        'This is a test for the group',
        'group',
        ['group-1']
      );
    });

    // Wait for the send message mutation to complete
    await waitFor(() => !result.current.sendMessagePending);

    // Verify API call
    expect(apiClient.post).toHaveBeenCalled();
  });
}); 