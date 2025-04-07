import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface BroadcastMessageFormProps {
  onSendMessage: (title: string, content: string) => void;
  isPending: boolean;
}

export function BroadcastMessageForm({ onSendMessage, isPending }: BroadcastMessageFormProps) {
  const [title, setTitle] = useState<string>('');
  const [content, setContent] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim() && content.trim()) {
      onSendMessage(title, content);
      setTitle('');
      setContent('');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Send Broadcast Message</CardTitle>
        <CardDescription>
          Send a message to all users in the system
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
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
        </CardContent>
        <CardFooter className="flex justify-end">
          <Button type="submit" disabled={isPending || !title.trim() || !content.trim()}>
            {isPending ? 'Sending...' : 'Send to All Users'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
} 