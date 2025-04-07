import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { instance as apiClient } from "@/lib/api"; // Import the named export and alias it as apiClient
import { useToast } from "@/hooks/use-toast"; // Corrected import path for the toast hook

// Define the Notification type based on your Django model/serializer
// Ensure this matches the structure returned by your API
export interface Notification {
    id: string;
    username: string; // from serializer
    title: string;
    content: string;
    type: string;
    is_read: boolean;
    created_at: string; // ISO string format
    updated_at: string; // ISO string format
}

interface UnreadCountResponse {
    unread_count: number;
}

interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

// --- API Interaction Functions ---

const fetchNotifications = async (filters: { type?: string; is_read?: boolean; limit?: number } = {}): Promise<Notification[]> => {
    const params = new URLSearchParams();
    if (filters.type) {
        params.append('type', filters.type);
    }
    if (filters.is_read !== undefined) {
        params.append('is_read', String(filters.is_read));
    }
    if (filters.limit !== undefined) {
        params.append('limit', String(filters.limit));
    }
    const queryString = params.toString();

    const url = queryString ? `api/v1/notifications/?${queryString}` : 'api/v1/notifications/';
    
    try {
        console.log(`Fetching notifications from: ${url}`);
        const response = await apiClient.get<PaginatedResponse<Notification>>(url).json();
        console.log('API Response:', response);
        
        if (!response || !response.results) {
            console.error('Invalid response format:', response);
            return [];
        }
        
        return response.results; // Return just the results array from the paginated response
    } catch (error) {
        console.error('Error fetching notifications:', error);
        throw error;
    }
};

const fetchUnreadCount = async (): Promise<UnreadCountResponse> => {
    const response = await apiClient.get<UnreadCountResponse>("api/v1/notifications/unread_count/").json();
    return response;
};

const markNotificationAsRead = async (id: string): Promise<Notification> => {
    const response = await apiClient.patch<Notification>(`api/v1/notifications/${id}/mark_as_read/`).json();
    return response;
};

const markAllNotificationsAsRead = async (): Promise<{ message: string }> => {
    const response = await apiClient.patch<{ message: string }>("api/v1/notifications/mark_all_as_read/").json();
    return response;
};

const sendBroadcastMessage = async (title: string, content: string): Promise<{ message: string, recipients_count: number }> => {
    const response = await apiClient.post<{ message: string, recipients_count: number }>(
        "api/v1/notifications/send_broadcast/", 
        { json: { title, content } }
    ).json();
    return response;
};

// --- React Query Hook ---

export function useNotifications(filters: { type?: string; is_read?: boolean; limit?: number } = {}) {
    const queryClient = useQueryClient();
    const { toast } = useToast(); // Get toast function

    const queryKeyBase = "notifications";
    const queryKey = [queryKeyBase, filters]; // Include filters in query key

    /**
     * Query: Fetch list of notifications with optional filters
     */
    const {
        data: notifications = [],
        isLoading: isLoadingNotifications,
        error: errorNotifications,
        refetch: refetchNotifications,
    } = useQuery<Notification[], Error>({
        queryKey: queryKey,
        queryFn: () => fetchNotifications(filters),
        refetchOnMount: true,
        staleTime: 1000, // 1 second - set to a low value to ensure frequent refreshes
    });

    /**
     * Query: Fetch unread notification count
     */
    const {
        data: unreadCountData,
        isLoading: isLoadingUnreadCount,
        error: errorUnreadCount,
        refetch: refetchUnreadCount,
    } = useQuery<UnreadCountResponse, Error>({
        queryKey: [queryKeyBase, 'unreadCount'],
        queryFn: fetchUnreadCount,
        refetchOnMount: true,
        staleTime: 1000, // 1 second
    });

    const unreadCount = unreadCountData?.unread_count ?? 0;


    /**
     * Mutation: Mark a single notification as read
     */
    const markAsReadMutation = useMutation<Notification, Error, string>({
        mutationFn: markNotificationAsRead,
        onSuccess: (data) => {
            // Optimistically update the specific notification
            queryClient.setQueryData<Notification[]>(queryKey, (oldData) =>
                oldData?.map((notif) =>
                    notif.id === data.id ? { ...notif, is_read: true } : notif
                ) ?? []
            );
            // Invalidate count and potentially the list to ensure consistency
            queryClient.invalidateQueries({ queryKey: [queryKeyBase, 'unreadCount'] });
            queryClient.invalidateQueries({ queryKey: queryKey }); // Or more specific invalidation

            toast({ title: "Success", description: "Notification marked as read." });
        },
        onError: (error) => {
            console.error("Failed to mark notification as read:", error);
            toast({ variant: "destructive", title: "Error", description: "Failed to mark notification as read." });
        },
    });

    /**
     * Mutation: Mark all notifications as read
     */
    const markAllAsReadMutation = useMutation<{ message: string }, Error>({
        mutationFn: markAllNotificationsAsRead,
        onSuccess: (data) => {
             // Invalidate all notification queries and the count
            queryClient.invalidateQueries({ queryKey: [queryKeyBase] });

            toast({ title: "Success", description: data.message || "All notifications marked as read." });
        },
        onError: (error) => {
            console.error("Failed to mark all notifications as read:", error);
            toast({ variant: "destructive", title: "Error", description: "Failed to mark all notifications as read." });
        },
    });

    /**
     * Mutation: Send broadcast message to all users
     */
    const sendBroadcastMutation = useMutation<
        { message: string; recipients_count: number }, 
        Error, 
        { title: string; content: string }
    >({
        mutationFn: ({ title, content }) => sendBroadcastMessage(title, content),
        onSuccess: (data) => {
            // Invalidate all notification queries and the count
            queryClient.invalidateQueries({ queryKey: [queryKeyBase] });
            
            toast({ 
                title: "Success", 
                description: data.message || `Message sent to ${data.recipients_count} users.` 
            });
        },
        onError: (error) => {
            console.error("Failed to send broadcast message:", error);
            toast({ 
                variant: "destructive", 
                title: "Error", 
                description: "Failed to send broadcast message." 
            });
        },
    });


    return {
        // Data
        notifications,
        unreadCount,
        // Loading states
        isLoading: isLoadingNotifications || isLoadingUnreadCount, // Combined loading state
        isLoadingNotifications,
        isLoadingUnreadCount,
        // Error states
        error: errorNotifications || errorUnreadCount, // Combined error state
        errorNotifications,
        errorUnreadCount,
        // Mutations
        markAsRead: markAsReadMutation.mutate,
        markAsReadPending: markAsReadMutation.isPending,
        markAllAsRead: markAllAsReadMutation.mutate,
        markAllAsReadPending: markAllAsReadMutation.isPending,
        sendBroadcast: sendBroadcastMutation.mutate,
        sendBroadcastPending: sendBroadcastMutation.isPending,
        // Refetch functions
        refetchNotifications,
        refetchUnreadCount,
    };
} 