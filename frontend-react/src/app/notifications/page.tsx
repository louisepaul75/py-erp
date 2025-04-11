'use client';

import React, { useState } from 'react';
import { useNotifications, Notification } from '@/hooks/useNotifications';
import { NotificationItem } from '@/components/notifications/NotificationItem';
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { MessageSelectorForm } from '@/components/notifications/MessageSelectorForm';
import { MessageSquare, Bell, Filter, ListTodo } from 'lucide-react';

export default function NotificationsPage() {
  const [category, setCategory] = useState<'all' | 'direct' | 'system' | 'todo'>('all');
  const [readStatus, setReadStatus] = useState<'all' | 'unread'>('all');

  // Create query params based on both filters
  const queryParams: any = {
    ...(readStatus === 'unread' ? { is_read: false } : {}),
    ...(category !== 'all' ? { type: category } : {}),
  };

  const {
    notifications,
    isLoadingNotifications,
    errorNotifications,
    markAsRead,
    markAsReadPending,
    markAllAsRead,
    markAllAsReadPending,
    sendMessage,
    sendMessagePending,
    toggleComplete,
    toggleCompletePending,
    refetchNotifications,
  } = useNotifications(queryParams);

  const handleMarkAllRead = () => {
    markAllAsRead();
  };

  const handleRefresh = () => {
    refetchNotifications();
  };

  const notificationList = Array.isArray(notifications) ? notifications : [];

  const handleMarkOneRead = (id: string) => {
    markAsRead(id);
  };

  const handleToggleComplete = (id: string, isCompleted: boolean) => {
    toggleComplete({ id, is_completed: isCompleted });
  };

  const handleSendMessage = (
    title: string, 
    content: string, 
    recipientType: 'broadcast' | 'group' | 'individual', 
    recipientIds: string[]
  ) => {
    sendMessage(title, content, recipientType, recipientIds);
    setMessageFormOpen(false);
  };

  const [messageFormOpen, setMessageFormOpen] = useState(false);
  
  const unreadNonTodoNotifications = notificationList.filter(
    (n: Notification) => !n.is_read && n.type !== 'todo'
  );
  const unreadNotificationsForTab = notificationList.filter((n: Notification) => !n.is_read);

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Notifications Card with New Message Button */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Notifications & Todos</CardTitle>
              <CardDescription>View messages, system alerts, and manage tasks.</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleRefresh} variant="outline" size="sm">
                Refresh
              </Button>
              <Popover open={messageFormOpen} onOpenChange={setMessageFormOpen}>
                <PopoverTrigger asChild>
                  <Button size="sm" className="flex items-center gap-1">
                    <MessageSquare className="h-4 w-4" />
                    New Message
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-96 p-4" align="end">
                  <div className="font-medium mb-2">Send Message</div>
                  <MessageSelectorForm 
                    onSendMessage={handleSendMessage}
                    isPending={sendMessagePending}
                    onCancel={() => setMessageFormOpen(false)}
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Category tabs - All messages, Direct Messages, System Notifications, Todos */}
          <Tabs value={category} onValueChange={(value) => setCategory(value as 'all' | 'direct' | 'system' | 'todo')} className="mb-6">
            <div className="flex items-center mb-2">
              <TabsList>
                <TabsTrigger value="all" className="flex items-center gap-1">
                  All
                </TabsTrigger>
                <TabsTrigger value="direct" className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4" />
                  Messages
                </TabsTrigger>
                <TabsTrigger value="system" className="flex items-center gap-1">
                  <Bell className="h-4 w-4" />
                  System
                </TabsTrigger>
                <TabsTrigger value="todo" className="flex items-center gap-1">
                  <ListTodo className="h-4 w-4" />
                  Todos
                </TabsTrigger>
              </TabsList>
            </div>
          </Tabs>

          {/* Read status tabs - All vs Unread */}
          <Tabs value={readStatus} onValueChange={(value) => setReadStatus(value as 'all' | 'unread')}>
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <TabsList>
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="unread">Unread/Pending</TabsTrigger>
                </TabsList>
              </div>
              {category !== 'todo' && (
                 <Button
                    onClick={handleMarkAllRead}
                    disabled={markAllAsReadPending || unreadNonTodoNotifications.length === 0}
                    size="sm"
                  >
                    {markAllAsReadPending ? 'Marking...' : 'Mark All as Read'}
                  </Button>
              )}
            </div>
            
            <TabsContent value="all">
              {isLoadingNotifications && (
                <div className="space-y-4">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              )}
              {errorNotifications && <p className="text-red-500">Error loading items: {errorNotifications.message}</p>}
              {!isLoadingNotifications && !errorNotifications && notificationList.length === 0 && (
                <p className="text-center text-gray-500 py-4">No items found matching filters.</p>
              )}
              {!isLoadingNotifications && !errorNotifications && notificationList.length > 0 && (
                <div className="space-y-2 border rounded-md">
                  {notificationList.map((notification: Notification) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onMarkAsRead={handleMarkOneRead}
                      isMarkingRead={markAsReadPending}
                      onToggleComplete={handleToggleComplete}
                      isTogglingComplete={toggleCompletePending}
                    />
                  ))}
                </div>
              )}
              {/* TODO: Add pagination controls if needed */}
            </TabsContent>
            <TabsContent value="unread">
             {isLoadingNotifications && (
                <div className="space-y-4">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              )}
              {errorNotifications && <p className="text-red-500">Error loading items: {errorNotifications.message}</p>}
              {!isLoadingNotifications && !errorNotifications && unreadNotificationsForTab.length === 0 && (
                <p className="text-center text-gray-500 py-4">You have no unread messages or pending todos.</p>
              )}
              {!isLoadingNotifications && !errorNotifications && unreadNotificationsForTab.length > 0 && (
                <div className="space-y-2 border rounded-md">
                  {unreadNotificationsForTab.map((notification: Notification) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onMarkAsRead={handleMarkOneRead}
                        isMarkingRead={markAsReadPending}
                        onToggleComplete={handleToggleComplete}
                        isTogglingComplete={toggleCompletePending}
                      />
                  ))}
                </div>
              )}
               {/* TODO: Add pagination controls if needed */}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
} 