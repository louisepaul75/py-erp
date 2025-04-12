import React from 'react';
import { Customer } from '@/lib/definitions';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BuildingIcon, MailIcon, PhoneIcon, GlobeIcon, HashIcon } from 'lucide-react';

interface CustomerGeneralInfoCardProps {
  customer: Customer; // Use Partial<Customer> if needed
}

export default function CustomerGeneralInfoCard({ customer }: CustomerGeneralInfoCardProps) {
  const { name, email, phone, website, tax_id, billing_address } = customer;

  return (
    <Card>
      <CardHeader>
        <CardTitle>General Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {name && (
          <div className="flex items-center">
            <BuildingIcon className="mr-2 h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Name:</span>
            <span className="ml-2 text-sm">{name}</span>
          </div>
        )}
        {tax_id && (
          <div className="flex items-center">
            <HashIcon className="mr-2 h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Tax ID:</span>
            <span className="ml-2 text-sm">{tax_id}</span>
          </div>
        )}
        {email && (
          <div className="flex items-center">
            <MailIcon className="mr-2 h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Email:</span>
            <a href={`mailto:${email}`} className="ml-2 text-sm hover:underline">{email}</a>
          </div>
        )}
        {phone && (
          <div className="flex items-center">
            <PhoneIcon className="mr-2 h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Phone:</span>
            <a href={`tel:${phone}`} className="ml-2 text-sm hover:underline">{phone}</a>
          </div>
        )}
        {website && (
          <div className="flex items-center">
            <GlobeIcon className="mr-2 h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Website:</span>
            <a href={website} target="_blank" rel="noopener noreferrer" className="ml-2 text-sm hover:underline">{website}</a>
          </div>
        )}
        {billing_address && (
          <div className="mt-4 pt-4 border-t">
            <h4 className="text-sm font-medium mb-2">Billing Address</h4>
            <address className="text-sm not-italic text-muted-foreground">
              {billing_address.street}<br />
              {billing_address.city}, {billing_address.state ? `${billing_address.state} ` : ''}{billing_address.postal_code}<br />
              {billing_address.country}
            </address>
          </div>
        )}
         {/* Add other fields as needed from Customer type */}
      </CardContent>
    </Card>
  );
} 