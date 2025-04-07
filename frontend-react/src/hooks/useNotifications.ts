import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api"; // Corrected import path
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

// --- API Interaction Functions ---

const fetchNotifications = async (filters: { type?: string; is_read?: boolean } = {}): Promise<Notification[]> => {
    const params = new URLSearchParams();
    if (filters.type) {
        params.append('type', filters.type);
    }
    if (filters.is_read !== undefined) {
        params.append('is_read', String(filters.is_read));
    }
    const response = await apiClient.get<Notification[]>(`/core/notifications/?${params.toString()}`);
    return response.data;
};

const fetchUnreadCount = async (): Promise<UnreadCountResponse> => {
    const response = await apiClient.get<UnreadCountResponse>("/core/notifications/unread_count/");
    return response.data;
};

const markNotificationAsRead = async (id: string): Promise<Notification> => {
    const response = await apiClient.patch<Notification>(`/core/notifications/${id}/mark_as_read/`);
    return response.data;
};

const markAllNotificationsAsRead = async (): Promise<{ message: string }> => {
    const response = await apiClient.patch<{ message: string }>("/core/notifications/mark_all_as_read/");
    return response.data;
};


// --- React Query Hook ---

export function useNotifications(filters: { type?: string; is_read?: boolean } = {}) {
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
        // Consider adding options like staleTime if needed
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
        // Often good to have a short staleTime/refetchInterval for unread count
        // staleTime: 60 * 1000, // 1 minute
        // refetchInterval: 5 * 60 * 1000, // 5 minutes
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
        // Refetch functions
        refetchNotifications,
        refetchUnreadCount,
    };
} 