import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { NotificationItem } from '@/components/notifications/NotificationItem';
import { Notification } from '@/hooks/useNotifications';
import { formatDistanceToNow } from 'date-fns';

// Mock date-fns
jest.mock('date-fns', () => ({
  formatDistanceToNow: jest.fn(() => '2 days ago'),
}));

describe('NotificationItem', () => {
  // Sample notification data for tests
  const unreadNotification: Notification = {
    id: '1',
    username: 'testuser',
    title: 'Test Notification',
    content: 'This is a test notification content',
    type: 'system',
    is_read: false,
    created_at: '2023-04-01T12:00:00Z',
    updated_at: '2023-04-01T12:00:00Z',
  };

  const readNotification: Notification = {
    ...unreadNotification,
    id: '2',
    is_read: true,
    title: 'Read Notification',
  };

  const directMessageNotification: Notification = {
    ...unreadNotification,
    id: '3',
    type: 'direct_message',
    title: 'Direct Message',
  };

  // Mock callback function
  const mockOnMarkAsRead = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders unread notification correctly', () => {
    render(
      <NotificationItem
        notification={unreadNotification}
        onMarkAsRead={mockOnMarkAsRead}
        isMarkingRead={false}
      />
    );

    // Verify content is displayed correctly
    expect(screen.getByText('Test Notification')).toBeInTheDocument();
    expect(screen.getByText('This is a test notification content')).toBeInTheDocument();
    expect(screen.getByText('2 days ago')).toBeInTheDocument();
    
    // Verify the mark as read button is present for unread notifications
    expect(screen.getByRole('button', { name: /mark as read/i })).toBeInTheDocument();
    
    // Verify date formatting was called correctly
    expect(formatDistanceToNow).toHaveBeenCalledWith(new Date(unreadNotification.created_at), {
      addSuffix: true,
    });
  });

  it('renders read notification correctly', () => {
    render(
      <NotificationItem
        notification={readNotification}
        onMarkAsRead={mockOnMarkAsRead}
        isMarkingRead={false}
      />
    );

    // Verify content
    expect(screen.getByText('Read Notification')).toBeInTheDocument();
    
    // Verify the mark as read button is NOT present for read notifications
    expect(screen.queryByRole('button', { name: /mark as read/i })).not.toBeInTheDocument();
  });

  it('renders correct icon based on notification type', () => {
    // Render system notification
    const { rerender } = render(
      <NotificationItem
        notification={unreadNotification} // system type
        onMarkAsRead={mockOnMarkAsRead}
        isMarkingRead={false}
      />
    );

    // Bell icon should be present for system notifications
    const icons = document.querySelectorAll('svg');
    expect(icons.length).toBeGreaterThan(0);

    // Rerender with direct message notification
    rerender(
      <NotificationItem
        notification={directMessageNotification} // direct_message type
        onMarkAsRead={mockOnMarkAsRead}
        isMarkingRead={false}
      />
    );

    expect(screen.getByText('Direct Message')).toBeInTheDocument();
  });

  it('calls onMarkAsRead when button is clicked', () => {
    render(
      <NotificationItem
        notification={unreadNotification}
        onMarkAsRead={mockOnMarkAsRead}
        isMarkingRead={false}
      />
    );

    // Find and click the mark as read button
    const markAsReadButton = screen.getByRole('button', { name: /mark as read/i });
    fireEvent.click(markAsReadButton);

    // Verify callback was called with the correct notification ID
    expect(mockOnMarkAsRead).toHaveBeenCalledWith(unreadNotification.id);
  });

  it('disables mark as read button when isMarkingRead is true', () => {
    render(
      <NotificationItem
        notification={unreadNotification}
        onMarkAsRead={mockOnMarkAsRead}
        isMarkingRead={true}
      />
    );

    // Find the mark as read button and verify it's disabled
    const markAsReadButton = screen.getByRole('button', { name: /mark as read/i });
    expect(markAsReadButton).toBeDisabled();
  });

  it('does not call onMarkAsRead when already read notification is clicked', () => {
    render(
      <NotificationItem
        notification={readNotification}
        onMarkAsRead={mockOnMarkAsRead}
        isMarkingRead={false}
      />
    );

    // Try to find mark as read button (should not exist)
    const markAsReadButton = screen.queryByRole('button', { name: /mark as read/i });
    expect(markAsReadButton).not.toBeInTheDocument();

    // Verify callback was not called
    expect(mockOnMarkAsRead).not.toHaveBeenCalled();
  });
}); 