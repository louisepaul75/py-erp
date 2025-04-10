import React from 'react';
import { ContactInfo } from '@/lib/definitions';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'; // Assuming shadcn/ui Card component
import {
  MailIcon,
  PhoneIcon,
  GlobeIcon,
  PrinterIcon,
  SmartphoneIcon,
  InfoIcon,
} from "lucide-react"; // Or your preferred icon library
import { Badge } from "@/components/ui/badge"

interface CustomerContactInfosCardProps {
  contactInfos: ContactInfo[];
  // Add isLoading, error states if needed
}

// Helper function to get icon based on type
const getIconForType = (type: ContactInfo['type']) => {
  switch (type) {
    case 'email':
      return <MailIcon className="mr-2 h-4 w-4 text-muted-foreground" />;
    case 'phone':
      return <PhoneIcon className="mr-2 h-4 w-4 text-muted-foreground" />;
    case 'mobile':
      return <SmartphoneIcon className="mr-2 h-4 w-4 text-muted-foreground" />;
    case 'fax':
      return <PrinterIcon className="mr-2 h-4 w-4 text-muted-foreground" />;
    case 'website':
      return <GlobeIcon className="mr-2 h-4 w-4 text-muted-foreground" />;
    default:
      return <InfoIcon className="mr-2 h-4 w-4 text-muted-foreground" />;
  }
};

export default function CustomerContactInfosCard({
  contactInfos,
}: CustomerContactInfosCardProps) {
  // TODO: Implement data fetching and display logic

  if (!contactInfos || contactInfos.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
        </CardHeader>
        <CardContent>
          <p>No contact information found for this customer.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Contact Information</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {contactInfos.map((info) => (
            <li key={info.id} className="flex items-center justify-between p-2 border rounded-md">
              <div className="flex items-center">
                {getIconForType(info.type)}
                <span className="text-sm font-medium capitalize">{info.type}:</span>
                <span className="ml-2 text-sm">{info.value}</span>
                {info.description && (
                  <span className="ml-2 text-sm text-muted-foreground">({info.description})</span>
                )}
              </div>
              {info.is_primary && (
                <Badge variant="secondary">Primary</Badge>
              )}
              {/* Add Edit/Delete buttons here later if needed */}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
} 