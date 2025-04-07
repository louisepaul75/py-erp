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

// Type definitions for recipients
type RecipientType = 'broadcast' | 'group' | 'individual';

type User = {
  id: string;
  name: string;
  email: string;
};

type Group = {
  id: string;
  name: string;
};

interface MessageSelectorFormProps {
  onSendMessage: (title: string, content: string, recipientType: RecipientType, recipientIds: string[]) => void;
  isPending: boolean;
  onCancel: () => void;
}

export function MessageSelectorForm({ onSendMessage, isPending, onCancel }: MessageSelectorFormProps) {
  const [title, setTitle] = useState<string>('');
  const [content, setContent] = useState<string>('');
  const [recipientType, setRecipientType] = useState<RecipientType>('broadcast');
  const [selectedRecipients, setSelectedRecipients] = useState<string[]>([]);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && content.trim()) {
      onSendMessage(title, content, recipientType, selectedRecipients);
      setTitle('');
      setContent('');
      setRecipientType('broadcast');
      setSelectedRecipients([]);
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
              {users.map((user: User) => (
                <SelectItem key={user.id} value={`user-${user.id}`}>
                  {user.name}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label htmlFor="message-title" className="text-sm font-medium">
          Message Title
        </label>
        <Input
          id="message-title"
          placeholder="Enter message title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      
      <div className="space-y-2">
        <label htmlFor="message-content" className="text-sm font-medium">
          Message Content
        </label>
        <Textarea
          id="message-content"
          placeholder="Enter your message"
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