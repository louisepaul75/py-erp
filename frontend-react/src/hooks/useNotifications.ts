import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { instance as apiClient } from "@/lib/api"; // Import the named export and alias it as apiClient
import { useToast } from "@/hooks/use-toast"; // Corrected import path for the toast hook
import { useIsAuthenticated } from "@/lib/auth/authHooks"; // Import the auth hook

// Define the Notification type based on your Django model/serializer
// Ensure this matches the structure returned by your API
export interface Notification {
    id: string;
    username: string; // Recipient username
    sender_username?: string | null; // Sender username (if applicable)
    sender_last_seen?: string | null; // Sender last seen timestamp (if applicable)
    title: string;
    content: string;
    type: 'system' | 'direct_message' | 'todo'; // Updated type
    is_read: boolean;
    is_completed?: boolean | null; // New field for To-Do
    priority?: 'low' | 'medium' | 'high' | null; // New field for To-Do
    created_at: string; // ISO string format
    updated_at: string; // ISO string format
}

// Define the structure for paginated API responses
// Make this generic if it's used elsewhere, or specific to Notifications
export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

// Define the structure for the unread count response
export interface UnreadCountResponse {
    unread_count: number;
}

// Type alias for notification type
type NotificationType = 'system' | 'direct_message' | 'todo';
// Type alias for priority level
type PriorityLevel = 'low' | 'medium' | 'high';

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

    const url = queryString ? `v1/notifications/?${queryString}` : 'v1/notifications/';
    
    try {
        const response = await apiClient.get<PaginatedResponse<Notification>>(url);
        const data = await response.json();
        
        if (!data || !data.results) {
            return [];
        }
        
        return data.results;
    } catch (error) {
        throw error;
    }
};

const fetchUnreadCount = async (): Promise<UnreadCountResponse> => {
    const response = await apiClient.get<UnreadCountResponse>("v1/notifications/unread_count/");
    const data = await response.json();
    return data;
};

const markNotificationAsRead = async (id: string): Promise<Notification> => {
    const response = await apiClient.patch<Notification>(`v1/notifications/${id}/mark_as_read/`, {});
    const data = await response.json();
    return data;
};

const markAllNotificationsAsRead = async (): Promise<{ message: string }> => {
    const response = await apiClient.patch<{ message: string }>("v1/notifications/mark_all_as_read/", {});
    const data = await response.json();
    return data;
};

const sendBroadcastMessage = async (title: string, content: string): Promise<{ message: string, recipients_count: number }> => {
    const response = await apiClient.post<{ message: string, recipients_count: number }>(
        "v1/notifications/send_broadcast/", 
        { json: { title, content } }
    );
    const data = await response.json();
    return data;
};

// Add new functions for sending to groups and individual users
const sendGroupMessage = async (
    title: string, 
    content: string, 
    groupId: string,
    type?: NotificationType, // Added optional type
    priority?: PriorityLevel | null // Added optional priority
): Promise<{ message: string, recipients_count: number }> => {
    const payload: any = { title, content, group_id: groupId };
    if (type) payload.type = type;
    if (priority) payload.priority = priority;

    const response = await apiClient.post<{ message: string, recipients_count: number }>(
        "v1/notifications/send_group/", 
        { json: payload } // Use constructed payload
    );
    const data = await response.json();
    return data;
};

const sendUserMessage = async (
    title: string, 
    content: string, 
    userId: string,
    type?: NotificationType, // Added optional type
    priority?: PriorityLevel | null // Added optional priority
): Promise<{ message: string, recipients_count: number }> => {
    const payload: any = { title, content, user_id: userId };
    if (type) payload.type = type;
    if (priority) payload.priority = priority;

    const response = await apiClient.post<{ message: string, recipients_count: number }>(
        "v1/notifications/send_user/", 
        { json: payload } // Use constructed payload
    );
    const data = await response.json();
    return data;
};

// --- New API function to toggle completion status ---
const toggleNotificationComplete = async (
    { id, is_completed }: { id: string; is_completed: boolean }
): Promise<Notification> => {
    // Assuming a PATCH request to update the specific field
    const response = await apiClient.patch<Notification>(
        `v1/notifications/${id}/`, // Use the detail view endpoint
        { json: { is_completed } } // Send only the field to update
    );
    const data = await response.json();
    return data;
};

// --- React Query Hook ---

export function useNotifications(filters: { type?: string; is_read?: boolean; limit?: number } = {}) {
    const queryClient = useQueryClient();
    const { toast } = useToast(); // Get toast function
    const { isAuthenticated } = useIsAuthenticated(); // Get authentication status

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
        enabled: isAuthenticated, // Only run if authenticated
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
        enabled: isAuthenticated, // Only run if authenticated
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

    /**
     * Mutation: Send message to a group
     */
    const sendGroupMessageMutation = useMutation<
        { message: string; recipients_count: number }, 
        Error, 
        { 
            title: string; 
            content: string; 
            groupId: string; 
            type?: NotificationType; // Added optional type
            priority?: PriorityLevel | null; // Added optional priority
        }
    >({
        mutationFn: ({ title, content, groupId, type, priority }) => 
            sendGroupMessage(title, content, groupId, type, priority),
        onSuccess: (data) => {
            // Invalidate all notification queries and the count
            queryClient.invalidateQueries({ queryKey: [queryKeyBase] });
            
            toast({ 
                title: "Success", 
                description: data.message || `Message sent to ${data.recipients_count} users in the group.` 
            });
        },
        onError: (error) => {
            console.error("Failed to send group message:", error);
            toast({ 
                variant: "destructive", 
                title: "Error", 
                description: "Failed to send message to group." 
            });
        },
    });

    /**
     * Mutation: Send message to an individual user
     */
    const sendUserMessageMutation = useMutation<
        { message: string; recipients_count: number }, 
        Error, 
        { 
            title: string; 
            content: string; 
            userId: string; 
            type?: NotificationType; // Added optional type
            priority?: PriorityLevel | null; // Added optional priority
        }
    >({
        mutationFn: ({ title, content, userId, type, priority }) => 
            sendUserMessage(title, content, userId, type, priority),
        onSuccess: (data) => {
            // Invalidate all notification queries and the count
            queryClient.invalidateQueries({ queryKey: [queryKeyBase] });
            
            toast({ 
                title: "Success", 
                description: data.message || `Message sent to user.` 
            });
        },
        onError: (error) => {
            console.error("Failed to send user message:", error);
            toast({ 
                variant: "destructive", 
                title: "Error", 
                description: "Failed to send message to user." 
            });
        },
    });

    /**
     * Mutation: Toggle the completion status of a To-Do notification
     */
    const toggleCompleteMutation = useMutation<
        Notification, 
        Error, 
        { id: string; is_completed: boolean } // Input type for the mutation
    >({
        mutationFn: toggleNotificationComplete,
        onSuccess: (data, variables) => {
            // Optimistically update the specific notification in the cache
            queryClient.setQueryData<Notification[]>(queryKey, (oldData) =>
                oldData?.map((notif) =>
                    notif.id === variables.id ? { ...notif, is_completed: variables.is_completed } : notif
                ) ?? []
            );
            
            // Optional: Invalidate specific queries if needed, though optimistic update might suffice
            // queryClient.invalidateQueries({ queryKey: queryKey });

            const status = variables.is_completed ? "completed" : "pending";
            toast({ title: "Success", description: `To-Do marked as ${status}.` });
        },
        onError: (error, variables) => {
            console.error("Failed to toggle To-Do status:", error);
            const status = variables.is_completed ? "completed" : "pending";
            toast({ 
                variant: "destructive", 
                title: "Error", 
                description: `Failed to mark To-Do as ${status}.` 
            });
            // Optional: Revert optimistic update on error
            // queryClient.invalidateQueries({ queryKey: queryKey }); 
        },
    });

    // Helper function to send a message based on recipient type
    const sendMessage = (
        title: string, 
        content: string, 
        recipientType: 'broadcast' | 'group' | 'individual', 
        recipientIds: string[],
        notificationType: NotificationType, // Use the correct type name
        priority?: PriorityLevel | null
    ) => {
        if (recipientType === 'broadcast') {
            // Broadcast doesn't support type/priority in this setup, send as system/default
            sendBroadcastMutation.mutate({ title, content });
        } else if (recipientType === 'group' && recipientIds.length > 0) {
            // --- Pass type and priority to mutate ---
            sendGroupMessageMutation.mutate({ 
                title, 
                content, 
                groupId: recipientIds[0], 
                type: notificationType, // Pass type
                priority // Pass priority (optional)
            });
            // --- End Pass ---
        } else if (recipientType === 'individual' && recipientIds.length > 0) {
            // --- Pass type and priority to mutate ---
            sendUserMessageMutation.mutate({ 
                title, 
                content, 
                userId: recipientIds[0], 
                type: notificationType, // Pass type
                priority // Pass priority (optional)
            });
            // --- End Pass ---
        }
    };

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
        sendGroupMessage: sendGroupMessageMutation.mutate,
        sendGroupMessagePending: sendGroupMessageMutation.isPending,
        sendUserMessage: sendUserMessageMutation.mutate,
        sendUserMessagePending: sendUserMessageMutation.isPending,
        sendMessage,
        sendMessagePending: sendBroadcastMutation.isPending || 
                           sendGroupMessageMutation.isPending || 
                           sendUserMessageMutation.isPending,
        toggleComplete: toggleCompleteMutation.mutate,
        toggleCompletePending: toggleCompleteMutation.isPending,
        // Refetch functions
        refetchNotifications,
        refetchUnreadCount,
    };
} 