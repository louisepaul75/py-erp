import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { fetchUsers } from "@/lib/api/users";
import { useQuery } from '@tanstack/react-query';
import { User } from '@/types/user';
import { differenceInMinutes } from 'date-fns';
import { cn } from '@/lib/utils';

// Type definitions for recipients
type RecipientType = 'broadcast' | 'group' | 'individual';
// --- Add Notification Type and Priority Types ---
type NotificationType = 'direct_message' | 'todo';
type PriorityLevel = 'low' | 'medium' | 'high' | 'none';
// --- End Add ---

type Group = {
  id: string;
  name: string;
};

// Function to determine if user is recently active (e.g., within the last 5 minutes)
const isUserActive = (lastSeen: string | null | undefined): boolean => {
  if (!lastSeen) return false;
  const lastSeenDate = new Date(lastSeen);
  const now = new Date();
  return differenceInMinutes(now, lastSeenDate) < 5; // Active if seen in last 5 mins
};

interface MessageSelectorFormProps {
  // --- Update onSendMessage prop signature ---
  onSendMessage: (
    title: string, 
    content: string, 
    recipientType: RecipientType, 
    recipientIds: string[],
    notificationType: NotificationType, // Added
    priority?: PriorityLevel | null      // Added (optional)
  ) => void;
  // --- End Update ---
  isPending: boolean;
  onCancel: () => void;
}

export function MessageSelectorForm({ onSendMessage, isPending, onCancel }: MessageSelectorFormProps) {
  const [title, setTitle] = useState<string>('');
  const [content, setContent] = useState<string>('');
  const [recipientType, setRecipientType] = useState<RecipientType>('broadcast');
  const [selectedRecipients, setSelectedRecipients] = useState<string[]>([]);
  // --- Add state for type and priority ---
  const [notificationType, setNotificationType] = useState<NotificationType>('direct_message');
  const [priority, setPriority] = useState<PriorityLevel | null>(null); // Use null for unset/none initially
  // --- End Add ---

  // Fetch users and groups
  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  // For a real implementation, you would fetch groups from the API
  // This is a placeholder for groups data
  const groups: Group[] = [
    { id: '1', name: 'Administrators' },
    { id: '2', name: 'Content Editors' },
    { id: '3', name: 'Viewers' },
  ];

  // Reset selected recipients when recipient type changes
  useEffect(() => {
    setSelectedRecipients([]);
  }, [recipientType]);

  // --- Reset priority when type changes from todo ---
  useEffect(() => {
    if (notificationType !== 'todo') {
      setPriority(null); // Reset to null
    }
  }, [notificationType]);
  // --- End Reset ---

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && content.trim()) {
      // --- Pass type and priority to onSendMessage ---
      // Pass priority directly if it's set and type is todo, otherwise null
      const selectedPriority = notificationType === 'todo' && priority !== 'none' ? priority : null;
      onSendMessage(
        title, 
        content, 
        recipientType, 
        selectedRecipients, 
        notificationType, 
        selectedPriority 
      );
      // --- End Pass ---
      setTitle('');
      setContent('');
      setRecipientType('broadcast');
      setSelectedRecipients([]);
      // --- Reset type and priority ---
      setNotificationType('direct_message');
      setPriority(null); // Reset to null
      // --- End Reset ---
    }
  };

  const handleRecipientChange = (value: string) => {
    if (value === 'broadcast') {
      setRecipientType('broadcast');
      setSelectedRecipients([]);
    } else if (value.startsWith('group-')) {
      setRecipientType('group');
      setSelectedRecipients([value.replace('group-', '')]);
    } else if (value.startsWith('user-')) {
      setRecipientType('individual');
      setSelectedRecipients([value.replace('user-', '')]);
    }
  };

  // --- Handle Notification Type Change ---
  const handleNotificationTypeChange = (value: string) => {
    if (value === 'direct_message' || value === 'todo') {
      setNotificationType(value);
    }
  };
  // --- End Handle ---

  // --- Handle Priority Change ---
  const handlePriorityChange = (value: string) => {
     // Allow 'none', 'low', 'medium', 'high'
     if (value === 'low' || value === 'medium' || value === 'high' || value === 'none') {
       setPriority(value as PriorityLevel);
     } else {
       setPriority(null); // Handle potential unexpected values, fallback to null
     }
  };
  // --- End Handle ---

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="recipient-type" className="text-sm font-medium">
          Recipient
        </label>
        <Select 
          value={
            recipientType === 'broadcast' 
              ? 'broadcast' 
              : recipientType === 'group' && selectedRecipients.length > 0
                ? `group-${selectedRecipients[0]}`
                : recipientType === 'individual' && selectedRecipients.length > 0
                  ? `user-${selectedRecipients[0]}`
                  : ''
          }
          onValueChange={handleRecipientChange}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select recipient" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Broadcast</SelectLabel>
              <SelectItem value="broadcast">Everyone</SelectItem>
            </SelectGroup>
            
            <SelectGroup>
              <SelectLabel>Groups</SelectLabel>
              {groups.map((group) => (
                <SelectItem key={group.id} value={`group-${group.id}`}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectGroup>
            
            <SelectGroup>
              <SelectLabel>Individual Users</SelectLabel>
              {(users as User[]).map((user: User) => (
                <SelectItem key={user.id} value={`user-${user.id}`}>
                  <div className="flex items-center space-x-2">
                    <span 
                      className={cn(
                        'h-2 w-2 rounded-full',
                        isUserActive(user.last_seen) ? 'bg-green-500' : 'bg-gray-400'
                      )}
                      title={isUserActive(user.last_seen) ? 'Online' : 'Offline'}
                    />
                    <span>{user.name}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label htmlFor="notification-type" className="text-sm font-medium">
          Message Type
        </label>
        <Select value={notificationType} onValueChange={handleNotificationTypeChange}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select message type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="direct_message">Direct Message</SelectItem>
            <SelectItem value="todo">To-Do Task</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {notificationType === 'todo' && (
        <div className="space-y-2">
          <label htmlFor="priority-level" className="text-sm font-medium">
            Priority Level (Optional)
          </label>
          <Select value={priority ?? 'none'} onValueChange={handlePriorityChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select priority (optional)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">None</SelectItem>
              <SelectItem value="low">Low</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="high">High</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="space-y-2">
        <label htmlFor="message-title" className="text-sm font-medium">
          {notificationType === 'todo' ? 'Task Title' : 'Message Title'}
        </label>
        <Input
          id="message-title"
          placeholder={notificationType === 'todo' ? 'Enter task title' : 'Enter message title'}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      
      <div className="space-y-2">
        <label htmlFor="message-content" className="text-sm font-medium">
          {notificationType === 'todo' ? 'Task Description' : 'Message Content'}
        </label>
        <Textarea
          id="message-content"
          placeholder={notificationType === 'todo' ? 'Enter task description' : 'Enter your message'}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={4}
          required
        />
      </div>

      <div className="flex justify-end space-x-2 pt-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button 
          type="submit" 
          onClick={handleSubmit}
          disabled={isPending || !title.trim() || !content.trim()}
        >
          {isPending ? 'Sending...' : 'Send Message'}
        </Button>
      </div>
    </div>
  );
} 