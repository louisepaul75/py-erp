import React from 'react';
import { ContactPerson } from '@/lib/definitions';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'; // Assuming shadcn/ui Card component
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import {
  MailIcon,
  PhoneIcon,
  UserIcon,
  BriefcaseIcon,
} from "lucide-react"; // Or your preferred icon library

interface CustomerContactPersonsCardProps {
  contactPersons: ContactPerson[];
  // Add isLoading, error states if needed
}

export default function CustomerContactPersonsCard({
  contactPersons,
}: CustomerContactPersonsCardProps) {
  // TODO: Implement data fetching and display logic

  if (!contactPersons || contactPersons.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Contact Persons</CardTitle>
        </CardHeader>
        <CardContent>
          <p>No contact persons found for this customer.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Contact Persons</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4">
          {contactPersons.map((person) => (
            <li key={person.id} className="flex items-start space-x-4 p-3 border rounded-md">
              <Avatar className="h-10 w-10 border">
                {/* Placeholder avatar - replace with actual image if available */}
                <AvatarFallback>{person.name?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
              </Avatar>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold flex items-center">
                    <UserIcon className="mr-1.5 h-4 w-4 text-muted-foreground" />
                    {person.name}
                    {person.is_primary && (
                      <Badge variant="secondary" className="ml-2">Primary</Badge>
                    )}
                  </h4>
                  {/* Add Edit/Delete buttons here later if needed */}
                </div>
                {person.position && (
                  <p className="text-sm text-muted-foreground flex items-center">
                    <BriefcaseIcon className="mr-1.5 h-4 w-4" />
                    {person.position}
                  </p>
                )}
                {person.email && (
                  <p className="text-sm text-muted-foreground flex items-center">
                    <MailIcon className="mr-1.5 h-4 w-4" />
                    <a href={`mailto:${person.email}`} className="hover:underline">
                      {person.email}
                    </a>
                  </p>
                )}
                {person.phone && (
                  <p className="text-sm text-muted-foreground flex items-center">
                    <PhoneIcon className="mr-1.5 h-4 w-4" />
                    <a href={`tel:${person.phone}`} className="hover:underline">
                      {person.phone}
                    </a>
                  </p>
                )}
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
} 