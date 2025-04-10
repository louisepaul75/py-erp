import React from 'react';
import { CustomerNote } from '@/lib/definitions';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PlusIcon, MessageSquareTextIcon } from 'lucide-react';

interface CustomerNotesCardProps {
  activity_notes: CustomerNote[];
  // Add customerId if needed for adding new notes
}

// Helper to format date (replace with a robust library like date-fns if needed)
const formatDate = (dateString: string) => {
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  } catch (e) {
    return dateString; // Fallback
  }
};

export default function CustomerNotesCard({ activity_notes }: CustomerNotesCardProps) {
  // TODO: Implement adding new notes functionality

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Notes</CardTitle>
        <Button size="sm" variant="outline" disabled> {/* TODO: Enable and implement add note */}
          <PlusIcon className="mr-2 h-4 w-4" /> Add Note
        </Button>
      </CardHeader>
      <CardContent>
        {(!activity_notes || activity_notes.length === 0) ? (
          <p className="text-sm text-muted-foreground">No notes found for this customer.</p>
        ) : (
          <ul className="space-y-4">
            {activity_notes.map((note) => (
              <li key={note.id} className="p-3 border rounded-md bg-muted/50">
                <div className="flex items-start space-x-3">
                   <MessageSquareTextIcon className="h-5 w-5 text-muted-foreground mt-1" />
                  <div className="flex-1 space-y-1">
                    <p className="text-sm whitespace-pre-wrap">{note.content}</p>
                    <div className="text-xs text-muted-foreground">
                      <span>{formatDate(note.created_at)}</span>
                      {note.created_by && <span> by {note.created_by}</span>}
                    </div>
                  </div>
                  {/* Optional: Add Edit/Delete buttons per note */}
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
} 