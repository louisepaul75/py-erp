"use client";

import { Notification } from "@/hooks/useNotifications";
import { cn } from "@/lib/utils";
import { formatDistanceToNow, differenceInMinutes } from 'date-fns';
import { Bell, MessageSquare, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

const isUserActive = (lastSeen: string | null | undefined): boolean => {
  if (!lastSeen) return false;
  const lastSeenDate = new Date(lastSeen);
  const now = new Date();
  return differenceInMinutes(now, lastSeenDate) < 5;
};

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => void; // Callback to trigger mark as read
  isMarkingRead?: boolean; // Optional flag if the parent needs to show loading
}

export function NotificationItem({
  notification,
  onMarkAsRead,
  isMarkingRead,
}: NotificationItemProps) {

  const Icon = notification.type === "system" ? Bell : MessageSquare;
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

  return (
    <div
      className={cn(
        "flex items-start p-4 border-b last:border-b-0",
        notification.is_read ? "bg-background" : "bg-accent/50 dark:bg-accent/20",
        "hover:bg-accent/80 dark:hover:bg-accent/40 transition-colors duration-150"
      )}
    >
      <Icon className="h-5 w-5 text-muted-foreground mr-4 mt-1 flex-shrink-0" />
      <div className="flex-grow">
        <div className="flex items-center space-x-2 mb-1">
          {notification.type === 'direct_message' && notification.sender_username && (
            <span 
              className={cn(
                'h-2 w-2 rounded-full flex-shrink-0',
                isSenderActive ? 'bg-green-500' : 'bg-gray-400'
              )}
              title={isSenderActive ? 'Online' : 'Offline'}
            />
          )}
          <h4 className="font-semibold text-sm leading-tight">{notification.title}</h4>
        </div>
        <p className="text-sm text-muted-foreground mb-2">{notification.content}</p>
        <p className="text-xs text-muted-foreground/80">{formattedDate}</p>
      </div>
      {!notification.is_read && (
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