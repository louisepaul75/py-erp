"use client";

import { Notification } from "@/hooks/useNotifications";
import { cn } from "@/lib/utils";
import { formatDistanceToNow, differenceInMinutes } from 'date-fns';
import { Bell, MessageSquare, Check, Flag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";

const isUserActive = (lastSeen: string | null | undefined): boolean => {
  if (!lastSeen) return false;
  const lastSeenDate = new Date(lastSeen);
  const now = new Date();
  return differenceInMinutes(now, lastSeenDate) < 5;
};

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => void; // Callback to trigger mark as read
  onToggleComplete: (id: string, isCompleted: boolean) => void; // Callback for To-Do toggle
  isMarkingRead?: boolean; // Optional flag if the parent needs to show loading
  isTogglingComplete?: boolean; // Optional flag for To-Do toggle loading
}

export function NotificationItem({
  notification,
  onMarkAsRead,
  onToggleComplete,
  isMarkingRead,
  isTogglingComplete,
}: NotificationItemProps) {

  const isTodo = notification.type === 'todo';
  const Icon = isTodo ? Flag : notification.type === "system" ? Bell : MessageSquare;
  const formattedDate = formatDistanceToNow(new Date(notification.created_at), {
    addSuffix: true,
  });

  const isSenderActive = notification.type === 'direct_message' && 
                         isUserActive(notification.sender_last_seen);

  const handleMarkRead = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering other click events if nested
    if (!notification.is_read) {
      onMarkAsRead(notification.id);
    }
  };

  const handleToggleComplete = (checked: boolean | 'indeterminate') => {
    // Ensure we pass a boolean
    if (typeof checked === 'boolean') {
      onToggleComplete(notification.id, checked);
    }
  };
  
  // Determine badge variant based on priority
  const getPriorityBadgeVariant = (priority: string | null | undefined): "default" | "secondary" | "destructive" | "outline" => {
    switch (priority) {
      case 'high':
        return "destructive";
      case 'medium':
        return "secondary"; // Or choose another appropriate variant
      case 'low':
        return "outline";
      default:
        return "default"; // Fallback, though should ideally not happen for todos
    }
  };

  return (
    <div
      className={cn(
        "flex items-start p-4 border-b last:border-b-0",
        notification.is_read && !isTodo ? "bg-background" : "bg-accent/50 dark:bg-accent/20", // Don't grey out completed todos
        isTodo && notification.is_completed ? "opacity-60" : "", // Dim completed todos
        "hover:bg-accent/80 dark:hover:bg-accent/40 transition-colors duration-150 group"
      )}
    >
      {/* Left section: Checkbox for Todos OR Icon for others */}
      <div className="mr-4 mt-1 flex-shrink-0">
        {isTodo ? (
          <Checkbox
            id={`todo-${notification.id}`}
            checked={!!notification.is_completed} 
            onCheckedChange={handleToggleComplete}
            disabled={isTogglingComplete}
            aria-label={notification.is_completed ? "Mark as pending" : "Mark as completed"}
            className="mt-0.5" // Align checkbox better
          />
        ) : (
          <Icon className="h-5 w-5 text-muted-foreground" />
        )}
      </div>
      
      {/* Middle section: Content */}
      <div className="flex-grow">
        <div className="flex items-center justify-between mb-1">
            {/* Title and sender/priority info */}
            <div className="flex items-center space-x-2">
                {notification.type === 'direct_message' && notification.sender_username && (
                    <span 
                    className={cn(
                        'h-2 w-2 rounded-full flex-shrink-0',
                        isSenderActive ? 'bg-green-500' : 'bg-gray-400'
                    )}
                    title={isSenderActive ? 'Online' : 'Offline'}
                    />
                )}
                <h4 className="font-semibold text-sm leading-tight group-hover:text-primary transition-colors">{notification.title}</h4>
            </div>
            {/* Priority Badge for Todos */}
            {isTodo && notification.priority && (
              <Badge variant={getPriorityBadgeVariant(notification.priority)} className="capitalize text-xs h-5 px-1.5">
                {notification.priority}
              </Badge>
            )}
        </div>
        <p className="text-sm text-muted-foreground mb-2">{notification.content}</p>
        <p className="text-xs text-muted-foreground/80">{formattedDate}</p>
      </div>
      
      {/* Right section: Mark as Read Button (only for non-todos) */}
      {!notification.is_read && !isTodo && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleMarkRead}
          disabled={isMarkingRead}
          aria-label="Mark as read"
          className="ml-2 p-1 h-auto self-center text-primary hover:text-primary/80"
        >
          <Check className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}

export default NotificationItem; 