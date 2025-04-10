'use client';

import React from 'react';
import { Address } from '@/lib/definitions';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PlusIcon, MapPinIcon, StarIcon } from 'lucide-react'; // Example icons
import { Badge } from '@/components/ui/badge';

interface CustomerShippingAddressesCardProps {
  addresses: Address[];
  // Add customerId if needed for adding/editing addresses
}

// Helper to format address into a single string
const formatAddress = (address: Address): string => {
  return [
    address.street,
    address.city,
    address.state,
    address.postal_code,
    address.country,
  ].filter(Boolean).join(', ');
};

export default function CustomerShippingAddressesCard({ addresses }: CustomerShippingAddressesCardProps) {
  // TODO: Implement adding/editing shipping addresses functionality

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Shipping Addresses</CardTitle>
        {/* TODO: Add button to manage/add addresses */}
        {/* <Button size="sm" variant="outline" disabled>
          <PlusIcon className="mr-2 h-4 w-4" /> Add Address
        </Button> */}
      </CardHeader>
      <CardContent>
        {(!addresses || addresses.length === 0) ? (
          <p className="text-sm text-muted-foreground py-4 text-center">No shipping addresses found.</p>
        ) : (
          <ul className="space-y-4">
            {addresses.map((address) => (
              <li key={address.id} className="p-3 border rounded-md bg-muted/50 flex items-start space-x-3">
                <MapPinIcon className="h-5 w-5 text-muted-foreground mt-1 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium">{formatAddress(address)}</p>
                  {address.is_primary && (
                    <Badge variant="secondary" className="mt-1">
                      <StarIcon className="mr-1 h-3 w-3" /> Primary
                    </Badge>
                  )}
                </div>
                 {/* Optional: Add Edit/Delete buttons per address */}
                 {/* <Button variant="ghost" size="icon" className="ml-auto" disabled>
                   <PencilIcon className="h-4 w-4" />
                 </Button> */}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
} 