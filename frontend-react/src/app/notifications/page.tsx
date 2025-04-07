'use client';

import React, { useState } from 'react';
import { useNotifications, Notification } from '@/hooks/useNotifications';
import { NotificationItem } from '@/components/notifications/NotificationItem';
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BroadcastMessageForm } from '@/components/notifications/BroadcastMessageForm';

export default function NotificationsPage() {
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const queryParams = filter === 'unread' ? { is_read: false } : {};

  const {
    notifications,
    isLoadingNotifications,
    errorNotifications,
    markAsRead,
    markAsReadPending,
    markAllAsRead,
    markAllAsReadPending,
    sendBroadcast,
    sendBroadcastPending,
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

  const handleSendBroadcast = (title: string, content: string) => {
    sendBroadcast({ title, content });
  };

  const unreadNotifications = notificationList.filter((n: Notification) => !n.is_read);

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Broadcast Message Form */}
      <BroadcastMessageForm 
        onSendMessage={handleSendBroadcast} 
        isPending={sendBroadcastPending} 
      />
      
      {/* Notifications Card */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>View and manage your notifications.</CardDescription>
            </div>
            <Button onClick={handleRefresh} variant="outline" size="sm">
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={filter} onValueChange={(value) => setFilter(value as 'all' | 'unread')}>
            <div className="flex justify-between items-center mb-4">
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="unread">Unread</TabsTrigger>
              </TabsList>
              <Button
                onClick={handleMarkAllRead}
                disabled={markAllAsReadPending || unreadNotifications.length === 0}
                size="sm"
              >
                {markAllAsReadPending ? 'Marking...' : 'Mark All as Read'}
              </Button>
            </div>
            <TabsContent value="all">
              {isLoadingNotifications && (
                <div className="space-y-4">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              )}
              {errorNotifications && <p className="text-red-500">Error loading notifications: {errorNotifications.message}</p>}
              {!isLoadingNotifications && !errorNotifications && notificationList.length === 0 && (
                <p className="text-center text-gray-500 py-4">You have no notifications.</p>
              )}
              {!isLoadingNotifications && !errorNotifications && notificationList.length > 0 && (
                <div className="space-y-2">
                  {notificationList.map((notification: Notification) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onMarkAsRead={handleMarkOneRead}
                      isMarkingRead={markAsReadPending}
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
              {errorNotifications && <p className="text-red-500">Error loading notifications: {errorNotifications.message}</p>}
              {!isLoadingNotifications && !errorNotifications && unreadNotifications.length === 0 && (
                <p className="text-center text-gray-500 py-4">You have no unread notifications.</p>
              )}
              {!isLoadingNotifications && !errorNotifications && unreadNotifications.length > 0 && (
                <div className="space-y-2">
                  {unreadNotifications.map((notification: Notification) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onMarkAsRead={handleMarkOneRead}
                        isMarkingRead={markAsReadPending}
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